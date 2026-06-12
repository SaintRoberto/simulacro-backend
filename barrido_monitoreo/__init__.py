from flask import Blueprint

barrido_monitoreo_bp = Blueprint("barrido_monitoreo", __name__)

from .routes import *
