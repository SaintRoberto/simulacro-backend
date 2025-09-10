from flask import Blueprint

menus_bp = Blueprint('menus', __name__)

from .routes import *
