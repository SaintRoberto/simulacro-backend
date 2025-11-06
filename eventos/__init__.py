from flask import Blueprint

# Blueprint principal de eventos
eventos_bp = Blueprint('eventos', __name__)

# Blueprints independientes para cada submódulo
evento_tipos_bp = Blueprint('evento_tipos', __name__)
evento_origenes_bp = Blueprint('evento_origenes', __name__)
evento_estados_bp = Blueprint('evento_estados', __name__)
evento_causas_bp = Blueprint('evento_causas', __name__)
evento_categorias_bp = Blueprint('evento_categorias', __name__)

from .routes import *  # rutas de eventos principales