from flask import Blueprint

recurso_categorias_bp = Blueprint('recurso_categorias', __name__)

from .routes import *
