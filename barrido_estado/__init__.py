from flask import Blueprint

barrido_estado_bp = Blueprint("barrido_estado", __name__)

from .routes import *
