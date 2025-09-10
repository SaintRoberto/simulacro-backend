from flask import Blueprint

perfiles_bp = Blueprint('perfiles', __name__)

from .routes import *
