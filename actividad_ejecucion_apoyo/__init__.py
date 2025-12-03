from flask import Blueprint

actividad_ejecucion_apoyo_bp = Blueprint('actividad_ejecucion_apoyo', __name__)

from . import routes  # noqa: F401
