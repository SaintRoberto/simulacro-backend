from flask import Blueprint

acta_coe_resoluciones_bp = Blueprint('acta_coe_resoluciones', __name__)

from .routes import *