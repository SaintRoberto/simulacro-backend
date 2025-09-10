from flask import Blueprint

coes_bp = Blueprint('coes', __name__)

from .routes import *
