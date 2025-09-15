from flask import Blueprint

respuesta_estados_bp = Blueprint('respuesta_estados', __name__)

from .routes import *
