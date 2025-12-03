from flask import Blueprint

accion_respuesta_origenes_bp = Blueprint('accion_respuesta_origenes', __name__)

from . import routes  # noqa: F401
