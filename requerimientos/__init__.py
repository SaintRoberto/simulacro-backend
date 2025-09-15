from flask import Blueprint

requerimientos_bp = Blueprint('requerimientos', __name__)

from .routes import *
