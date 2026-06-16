from flask import Blueprint

asistencia_humanitaria_entregada_bp = Blueprint("asistencia_humanitaria_entregada", __name__)

from .routes import *
