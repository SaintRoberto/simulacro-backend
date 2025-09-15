from flask import Blueprint

emergencias_bp = Blueprint('emergencias', __name__)

from .routes import *
