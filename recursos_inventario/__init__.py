from flask import Blueprint

recursos_inventario_bp = Blueprint('recursos_inventario', __name__)

from .routes import *
