from flask import Blueprint

perfil_menu_bp = Blueprint('perfil_menu', __name__)

from .routes import *
