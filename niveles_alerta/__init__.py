from flask import Blueprint

niveles_alerta_bp = Blueprint('niveles_alerta', __name__)

from .routes import *
