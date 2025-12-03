from flask import Blueprint

actividad_ejecucion_dpa_bp = Blueprint('actividad_ejecucion_dpa', __name__)

from . import routes
