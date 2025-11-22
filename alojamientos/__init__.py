from flask import Blueprint

alojamientos_bp = Blueprint('alojamientos', __name__)

from .routes import *
