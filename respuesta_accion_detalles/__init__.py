from flask import Blueprint

respuesta_accion_detalles_bp = Blueprint('respuesta_accion_detalles', __name__)

# Import routes to ensure they are registered when the package is imported
from . import routes  # noqa: F401