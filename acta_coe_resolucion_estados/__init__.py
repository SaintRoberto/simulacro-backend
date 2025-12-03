from flask import Blueprint

acta_coe_resolucion_estados_bp = Blueprint('acta_coe_resolucion_estados', __name__)

from .routes import *