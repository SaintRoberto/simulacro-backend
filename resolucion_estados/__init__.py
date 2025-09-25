from flask import Blueprint

resolucion_estados_bp = Blueprint('resolucion_estados', __name__)

from .routes import *