from flask import Blueprint

evento_atencion_estados_bp = Blueprint('evento_atencion_estados', __name__)

from .routes import *
