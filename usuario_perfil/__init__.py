from flask import Blueprint

usuario_perfil_bp = Blueprint('usuario_perfil', __name__)

from .routes import *
