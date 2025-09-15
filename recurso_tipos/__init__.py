from flask import Blueprint

recurso_tipos_bp = Blueprint('recurso_tipos', __name__)

from .routes import *
