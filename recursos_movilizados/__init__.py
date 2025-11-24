from flask import Blueprint

recursos_movilizados_bp = Blueprint('recursos_movilizados', __name__)

from .routes import *
