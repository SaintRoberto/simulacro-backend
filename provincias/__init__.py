from flask import Blueprint

provincias_bp = Blueprint('provincias', __name__)

from .routes import *
