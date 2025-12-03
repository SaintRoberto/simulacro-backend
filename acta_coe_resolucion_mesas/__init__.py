from flask import Blueprint

acta_coe_resolucion_mesas_bp = Blueprint('acta_coe_resolucion_mesas', __name__)

from .routes import *
