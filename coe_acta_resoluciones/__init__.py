from flask import Blueprint

coe_acta_resoluciones_bp = Blueprint('coe_acta_resoluciones', __name__)

from .routes import *