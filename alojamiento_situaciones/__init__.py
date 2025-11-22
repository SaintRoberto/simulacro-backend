from flask import Blueprint

alojamiento_situaciones_bp = Blueprint('alojamiento_situaciones', __name__)

from .routes import *
