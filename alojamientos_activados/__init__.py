from flask import Blueprint

alojamientos_activados_bp = Blueprint('alojamientos_activados', __name__)

from .routes import *
