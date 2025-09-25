from flask import Blueprint

afectacion_variable_registro_detalles_bp = Blueprint('afectacion_variable_registro_detalles', __name__)

from .routes import *