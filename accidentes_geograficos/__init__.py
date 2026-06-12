from flask import Blueprint

accidentes_geograficos_bp = Blueprint("accidentes_geograficos", __name__)

from .routes import *
