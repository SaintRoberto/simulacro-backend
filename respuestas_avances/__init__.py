from flask import Blueprint

respuestas_avances_bp = Blueprint('respuestas_avances', __name__)

from .routes import *
