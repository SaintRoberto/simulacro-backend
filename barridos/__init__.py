from flask import Blueprint

barridos_bp = Blueprint("barridos", __name__)

from .routes import *
