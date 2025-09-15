from flask import Blueprint

requerimiento_recursos_bp = Blueprint('requerimiento_recursos', __name__)

from .routes import *
