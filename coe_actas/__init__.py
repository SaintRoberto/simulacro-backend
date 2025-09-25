from flask import Blueprint

coe_actas_bp = Blueprint('coe_actas', __name__)

from .routes import *