from flask import Flask, jsonify, request, g
from flask_sqlalchemy import SQLAlchemy
from config import DATABASE_URL
from flasgger import Swagger
from flask_cors import CORS
from auth import decode_token

app = Flask(__name__)
CORS(app, origins=["http://localhost:3000"], methods=["GET","POST","PUT","DELETE","OPTIONS"], allow_headers=["Content-Type","Authorization"], supports_credentials=True)

# Configuración de la base de datos
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Inicializar SQLAlchemy
from models import db
db.init_app(app)

# Inicializar Swagger UI
swagger = Swagger(app)

# Registrar todos los módulos (Blueprints)
from instituciones import instituciones_bp
from usuarios import usuarios_bp
from perfiles import perfiles_bp
from menus import menus_bp
from provincias import provincias_bp
from cantones import cantones_bp
from parroquias import parroquias_bp
from infraestructuras import infraestructuras_bp
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
from requerimiento_estados import requerimiento_estados_bp
from usuario_perfil import usuario_perfil_bp
from perfil_menu import perfil_menu_bp
from afectacion_variable_registros import afectacion_variable_registros_bp
from afectacion_variables import afectacion_variables_bp
from coe_actas import coe_actas_bp
from coe_acta_resoluciones import coe_acta_resoluciones_bp
from resolucion_estados import resolucion_estados_bp
from afectacion_variable_registro_detalles import afectacion_variable_registro_detalles_bp

app.register_blueprint(instituciones_bp)
app.register_blueprint(usuarios_bp)
app.register_blueprint(perfiles_bp)
app.register_blueprint(menus_bp)
app.register_blueprint(provincias_bp)
app.register_blueprint(cantones_bp)
app.register_blueprint(parroquias_bp)
app.register_blueprint(infraestructuras_bp)
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
app.register_blueprint(requerimiento_estados_bp)
app.register_blueprint(usuario_perfil_bp)
app.register_blueprint(perfil_menu_bp)
app.register_blueprint(afectacion_variable_registros_bp)
app.register_blueprint(afectacion_variables_bp)
app.register_blueprint(coe_actas_bp)
app.register_blueprint(coe_acta_resoluciones_bp)
app.register_blueprint(resolucion_estados_bp)
app.register_blueprint(afectacion_variable_registro_detalles_bp)

# Global before_request: require JWT for all endpoints except whitelist
WHITELIST_PATHS = [
    '/api/health',
    '/api/usuarios/login',
    '/api/usuarios'  # allow user creation (POST) - if you want it public
    # add other public endpoints as needed (Swagger UI, static files, etc.)
]

@app.before_request
def require_jwt_for_all():
    # Allow OPTIONS for CORS preflight
    if request.method == 'OPTIONS':
        return None
    path = request.path
    # Allow whitelisted paths
    if path in WHITELIST_PATHS:
        return None
    # Extract token
    auth = request.headers.get('Authorization', None)
    if not auth:
        return jsonify({'error': 'Authorization header required'}), 401
    parts = auth.split()
    if parts[0].lower() != 'bearer' or len(parts) != 2:
        return jsonify({'error': 'Authorization header must be Bearer token'}), 401
    token = parts[1]
    decoded = decode_token(token)
    if not decoded:
        return jsonify({'error': 'Invalid or expired token'}), 401
    # Attach decoded to request for downstream handlers
    g.user = decoded

# Ruta de salud
@app.route('/api/health', methods=['GET'])
def health_check():
    # Health check
    return jsonify({'estado': 'OK', 'mensaje': 'API funcionando correctamente'})

# Inicializar base de datos
with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
