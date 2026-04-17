from flask import Blueprint

instituciones_coe_mesa_bp = Blueprint('instituciones_coe_mesa', __name__)

from .routes import *
