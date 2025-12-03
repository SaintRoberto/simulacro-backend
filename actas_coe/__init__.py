from flask import Blueprint

actas_coe_bp = Blueprint('actas_coe', __name__)

from .routes import *