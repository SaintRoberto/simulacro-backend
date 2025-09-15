from flask import Blueprint

requerimiento_respuestas_bp = Blueprint('requerimiento_respuestas', __name__)

from .routes import *
