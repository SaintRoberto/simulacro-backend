from flask import Blueprint

accion_respuesta_estados_bp = Blueprint('accion_respuesta_estados', __name__)

from . import routes  # noqa: F401
