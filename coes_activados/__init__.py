from flask import Blueprint

coes_activados_bp = Blueprint('coes_activados', __name__)

from .routes import *
