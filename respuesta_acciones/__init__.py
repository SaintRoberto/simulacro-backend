from flask import Blueprint

respuesta_acciones_bp = Blueprint('respuesta_acciones', __name__)

# Import routes to ensure they are registered when the package is imported
from . import routes  # noqa: F401