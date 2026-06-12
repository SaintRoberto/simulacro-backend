from flask import Blueprint

accidente_geografico_tipos_bp = Blueprint("accidente_geografico_tipos", __name__)

from .routes import *
