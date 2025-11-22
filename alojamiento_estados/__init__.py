from flask import Blueprint

alojamiento_estados_bp = Blueprint('alojamiento_estados', __name__)

from .routes import *
