import os
import datetime
from functools import wraps
from flask import request, jsonify, current_app
import jwt
from passlib.hash import bcrypt

# bcrypt has a 72-byte input limit. Helper to safely prepare passwords for verify/hash.
BCRYPT_MAX_BYTES = 72



# Load secret from env or fallback (do NOT use fallback in production)
JWT_SECRET = os.environ.get('JWT_SECRET', 'change_this_secret_in_production')
JWT_ALGORITHM = 'HS256'
JWT_EXP_DELTA_SECONDS = int(os.environ.get('JWT_EXP_SECONDS', 3600))  # 1 hour default

def hash_password(password: str) -> str:
    return bcrypt.hash(password)

def verify_password(password: str, hashed: str) -> bool:
    return bcrypt.verify(password, hashed)

def generate_token(payload: dict, exp_seconds: int = None):
    exp_seconds = exp_seconds or JWT_EXP_DELTA_SECONDS
    payload_copy = payload.copy()
    payload_copy['exp'] = datetime.datetime.utcnow() + datetime.timedelta(seconds=exp_seconds)
    token = jwt.encode(payload_copy, JWT_SECRET, algorithm=JWT_ALGORITHM)
    # PyJWT>=2 returns str; ensure str
    if isinstance(token, bytes):
        token = token.decode('utf-8')
    return token

def decode_token(token: str):
    try:
        decoded = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return decoded
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None

def get_token_from_header():
    auth = request.headers.get('Authorization', None)
    if not auth:
        return None
    parts = auth.split()
    if parts[0].lower() != 'bearer' or len(parts) != 2:
        return None
    return parts[1]

def login_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        token = get_token_from_header()
        if not token:
            return jsonify({'error': 'Authorization header missing or malformed'}), 401
        decoded = decode_token(token)
        if not decoded:
            return jsonify({'error': 'Invalid or expired token'}), 401
        # attach user info to request context (Flask's global 'g' would be better, but keep simple)
        request.user = decoded
        return fn(*args, **kwargs)
    return wrapper

def roles_required(*allowed_roles):
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            token = get_token_from_header()
            if not token:
                return jsonify({'error': 'Authorization header missing or malformed'}), 401
            decoded = decode_token(token)
            if not decoded:
                return jsonify({'error': 'Invalid or expired token'}), 401
            roles = decoded.get('roles', [])
            # roles can be a single string or list
            if isinstance(roles, str):
                user_roles = [roles]
            else:
                user_roles = roles
            if not any(r in user_roles for r in allowed_roles):
                return jsonify({'error': 'Insufficient privileges'}), 403
            request.user = decoded
            return fn(*args, **kwargs)
        return wrapper
    return decorator
