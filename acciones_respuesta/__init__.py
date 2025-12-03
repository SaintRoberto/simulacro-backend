from flask import Blueprint

acciones_respuesta_bp = Blueprint('acciones_respuesta', __name__)

# Import routes to ensure they are registered when the package is imported
from . import routes  # noqa: F401