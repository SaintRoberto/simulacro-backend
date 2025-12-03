from flask import Blueprint

actividades_ejecucion_bp = Blueprint('actividades_ejecucion', __name__)

# Import routes to ensure they are registered when the package is imported
from . import routes  # noqa: F401