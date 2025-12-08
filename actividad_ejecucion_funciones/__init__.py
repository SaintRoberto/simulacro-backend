from flask import Blueprint

actividad_ejecucion_funciones_bp = Blueprint('actividad_ejecucion_funciones', __name__)

from . import routes
