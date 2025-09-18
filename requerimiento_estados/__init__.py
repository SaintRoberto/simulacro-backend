from flask import Blueprint

requerimiento_estados_bp = Blueprint('requerimiento_estados', __name__)

from .routes import *