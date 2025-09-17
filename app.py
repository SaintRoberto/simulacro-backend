from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy
from config import DATABASE_URL
from flasgger import Swagger
from flask_cors import CORS

app = Flask(__name__)
CORS(app, origins=["http://localhost:3000"])

# Configuración de la base de datos
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Inicializar SQLAlchemy
from models import db
db.init_app(app)

# Inicializar Swagger UI
swagger = Swagger(app)

# Registrar todos los módulos (Blueprints)
from categorias import categorias_bp
from instituciones import instituciones_bp
from usuarios import usuarios_bp
from perfiles import perfiles_bp
from menus import menus_bp
from provincias import provincias_bp
from cantones import cantones_bp
from parroquias import parroquias_bp
from coes import coes_bp
from mesas import mesas_bp
from institucion_categorias import institucion_categorias_bp
from niveles_afectacion import niveles_afectacion_bp
from niveles_alerta import niveles_alerta_bp
from opciones import opciones_bp
from mesa_grupos import mesa_grupos_bp
from emergencias import emergencias_bp
from recurso_tipos import recurso_tipos_bp
from recurso_categorias import recurso_categorias_bp
from recurso_grupos import recurso_grupos_bp
from requerimientos import requerimientos_bp
from requerimiento_recursos import requerimiento_recursos_bp
from requerimiento_respuestas import requerimiento_respuestas_bp
from respuestas_avances import respuestas_avances_bp
from respuesta_estados import respuesta_estados_bp
from usuario_perfil import usuario_perfil_bp
from perfil_menu import perfil_menu_bp

app.register_blueprint(categorias_bp)
app.register_blueprint(instituciones_bp)
app.register_blueprint(usuarios_bp)
app.register_blueprint(perfiles_bp)
app.register_blueprint(menus_bp)
app.register_blueprint(provincias_bp)
app.register_blueprint(cantones_bp)
app.register_blueprint(parroquias_bp)
app.register_blueprint(coes_bp)
app.register_blueprint(mesas_bp)
app.register_blueprint(institucion_categorias_bp)
app.register_blueprint(niveles_afectacion_bp)
app.register_blueprint(niveles_alerta_bp)
app.register_blueprint(opciones_bp)
app.register_blueprint(mesa_grupos_bp)
app.register_blueprint(emergencias_bp)
app.register_blueprint(recurso_tipos_bp)
app.register_blueprint(recurso_categorias_bp)
app.register_blueprint(recurso_grupos_bp)
app.register_blueprint(requerimientos_bp)
app.register_blueprint(requerimiento_recursos_bp)
app.register_blueprint(requerimiento_respuestas_bp)
app.register_blueprint(respuestas_avances_bp)
app.register_blueprint(respuesta_estados_bp)
app.register_blueprint(usuario_perfil_bp)
app.register_blueprint(perfil_menu_bp)

# Ruta de salud
@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check
    ---
    tags:
      - Salud
    responses:
      200:
        description: Estado de la API
        examples:
          application/json: {"estado": "OK", "mensaje": "API funcionando correctamente"}
    """
    return jsonify({'estado': 'OK', 'mensaje': 'API funcionando correctamente'})

# Inicializar base de datos
with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
