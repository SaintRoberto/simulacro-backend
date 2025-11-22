from flask import Blueprint

alojamiento_tipos_bp = Blueprint('alojamiento_tipos', __name__)

from .routes import *
