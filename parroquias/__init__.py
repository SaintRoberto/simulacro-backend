from flask import Blueprint

parroquias_bp = Blueprint('parroquias', __name__)

from .routes import *
