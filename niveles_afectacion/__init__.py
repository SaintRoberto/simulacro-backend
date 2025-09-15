from flask import Blueprint

niveles_afectacion_bp = Blueprint('niveles_afectacion', __name__)

from .routes import *
