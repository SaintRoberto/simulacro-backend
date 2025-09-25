from flask import Blueprint

infraestructuras_bp = Blueprint('infraestructuras', __name__)

from .routes import *