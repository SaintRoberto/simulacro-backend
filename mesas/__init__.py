from flask import Blueprint

mesas_bp = Blueprint('mesas', __name__)

from .routes import *
