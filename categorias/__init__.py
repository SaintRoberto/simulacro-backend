from flask import Blueprint

categorias_bp = Blueprint('categorias', __name__)

from .routes import *
