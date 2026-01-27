import os
from flask import Blueprint, jsonify, request
from models import db
from config import PUBLIC_API_KEYS as CONFIG_PUBLIC_API_KEYS

afectaciones_public_bp = Blueprint('afectaciones_public', __name__)


def _validate_api_key():
    keys_env = os.environ.get('PUBLIC_API_KEYS') or CONFIG_PUBLIC_API_KEYS or ''
    allowed = [k.strip() for k in keys_env.split(',') if k.strip()]
    provided = request.headers.get('X-API-Key') or request.args.get('api_key')
    if not allowed:
        return False, 'Server misconfiguration: PUBLIC_API_KEYS not set'
    if not provided:
        return False, 'API key required (header X-API-Key or query param api_key)'
    if provided not in allowed:
        return False, 'Invalid API key'
    return True, None


@afectaciones_public_bp.route('/api/public/afectaciones_version1', methods=['GET'])
def get_afectaciones_version1():
    """Public endpoint (secured by API key): devuelve todos los registros de la vista afectaciones_version1"""
    ok, msg = _validate_api_key()
    if not ok:
        return jsonify({'error': msg}), 401

    result = db.session.execute(db.text("SELECT * FROM afectaciones_version1"))
    registros = []
    for row in result:
        try:
            mapping = row._mapping
        except Exception:
            mapping = dict(row)
        record = {}
        for k, v in mapping.items():
            if hasattr(v, 'isoformat'):
                try:
                    record[k] = v.isoformat()
                except Exception:
                    record[k] = v
            else:
                record[k] = v
        registros.append(record)
    return jsonify(registros)


@afectaciones_public_bp.route('/api/public/afectaciones_version1/<int:registro_id>', methods=['GET'])
def get_afectacion_version1_by_id(registro_id):
    """Public endpoint (secured by API key): devuelve un registro por id de la vista afectaciones_version1"""
    ok, msg = _validate_api_key()
    if not ok:
        return jsonify({'error': msg}), 401

    result = db.session.execute(db.text("SELECT * FROM afectaciones_version1 WHERE id = :id"), {'id': registro_id})
    row = result.fetchone()
    if not row:
        return jsonify({'error': 'Registro no encontrado'}), 404
    try:
        mapping = row._mapping
    except Exception:
        mapping = dict(row)
    record = {}
    for k, v in mapping.items():
        if hasattr(v, 'isoformat'):
            try:
                record[k] = v.isoformat()
            except Exception:
                record[k] = v
        else:
            record[k] = v
    return jsonify(record)
