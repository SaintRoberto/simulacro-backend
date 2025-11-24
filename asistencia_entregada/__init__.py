from flask import Blueprint

asistencia_entregada_bp = Blueprint('asistencia_entregada', __name__)

from .routes import *
