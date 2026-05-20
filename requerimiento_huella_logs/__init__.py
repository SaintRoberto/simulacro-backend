from flask import Blueprint

requerimiento_huella_logs_bp = Blueprint('requerimiento_huella_logs', __name__)

from .routes import *
