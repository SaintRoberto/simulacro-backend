from flask import Blueprint

eventos_bp = Blueprint('eventos', __name__)

from .routes import *