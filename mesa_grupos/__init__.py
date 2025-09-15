from flask import Blueprint

mesa_grupos_bp = Blueprint('mesa_grupos', __name__)

from .routes import *
