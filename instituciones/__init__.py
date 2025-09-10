from flask import Blueprint

instituciones_bp = Blueprint('instituciones', __name__)

from .routes import *
