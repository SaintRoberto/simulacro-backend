from flask import Blueprint

recurso_grupos_bp = Blueprint('recurso_grupos', __name__)

from .routes import *
