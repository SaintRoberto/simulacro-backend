from flask import Blueprint

barrido_intensidad_bp = Blueprint("barrido_intensidad", __name__)

from .routes import *
