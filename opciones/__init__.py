from flask import Blueprint

opciones_bp = Blueprint('opciones', __name__)

from .routes import *
