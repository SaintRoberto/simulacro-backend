from flask import Blueprint

cantones_bp = Blueprint('cantones', __name__)

from .routes import *
