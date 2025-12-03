from flask import Blueprint

acta_coe_estados_bp = Blueprint('acta_coe_estados', __name__)

from .routes import *
