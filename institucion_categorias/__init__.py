from flask import Blueprint

institucion_categorias_bp = Blueprint('institucion_categorias', __name__)

from .routes import *
