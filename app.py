from flask import Flask, jsonify, request, g
from flask_sqlalchemy import SQLAlchemy
from config import DATABASE_URL, FRONTEND_ORIGIN
from flasgger import Swagger
from flask_cors import CORS
from auth import decode_token

app = Flask(__name__)

CORS(
    app,
    origins=[FRONTEND_ORIGIN],
    methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization"],
    supports_credentials=True
)

# Configuración de la base de datos
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Inicializar SQLAlchemy
from models import db
db.init_app(app)

swagger_template = {
    "swagger": "2.0",
    "info": {
        "title": "Mi API de Riesgos",
        "description": "Documentación de mi API con JWT",
        "version": "1.0.0"
    },
    "securityDefinitions": {
        "Bearer": {
            "type": "apiKey",
            "name": "Authorization",
            "in": "header",
            "description": "Escribe: Bearer <tu_jwt_token>"
        }
    },
    "security": [
        {"Bearer": []}
    ]
}



# Inicializar Swagger UI
#swagger = Swagger(app)


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
from eventos import eventos_bp
from evento_tipos.routes import evento_tipos_bp
from evento_subtipos.routes import evento_subtipos_bp
from evento_causas.routes import evento_causas_bp
from evento_origenes.routes import evento_origenes_bp
from evento_estados.routes import evento_estados_bp
from evento_categorias.routes import evento_categorias_bp
from recurso_tipos import recurso_tipos_bp
from recurso_categorias import recurso_categorias_bp
from recurso_grupos import recurso_grupos_bp
from recursos_movilizados import recursos_movilizados_bp
from asistencia_entregada import asistencia_entregada_bp
from alojamientos import alojamientos_bp
from alojamiento_estados import alojamiento_estados_bp
from alojamiento_situaciones import alojamiento_situaciones_bp
from alojamiento_tipos import alojamiento_tipos_bp
from alojamientos_activados import alojamientos_activados_bp
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
from acta_coe_resoluciones import acta_coe_resoluciones_bp
from acta_coe_resolucion_mesas import acta_coe_resolucion_mesas_bp
from acta_coe_resolucion_estados import acta_coe_resolucion_estados_bp
from acta_coe_estados import acta_coe_estados_bp
from afectacion_variable_registro_detalles import afectacion_variable_registro_detalles_bp
from acciones_respuesta import acciones_respuesta_bp
from accion_respuesta_origenes import accion_respuesta_origenes_bp
from accion_respuesta_estados import accion_respuesta_estados_bp
from actividades_ejecucion import actividades_ejecucion_bp
from actividad_ejecucion_apoyo import actividad_ejecucion_apoyo_bp
from actividad_ejecucion_dpa import actividad_ejecucion_dpa_bp
from actas_coe import actas_coe_bp
from actividad_ejecucion_funciones import actividad_ejecucion_funciones_bp      
from evento_atencion_estados import evento_atencion_estados_bp
from reportes.afectaciones_public import afectaciones_public_bp
from reportes.eventos_historico_csv import eventos_historico_csv_bp
from reportes.eventos_dashboard_csv import eventos_dashboard_csv_bp






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
app.register_blueprint(eventos_bp)
app.register_blueprint(emergencias_bp)
app.register_blueprint(evento_tipos_bp)
app.register_blueprint(evento_subtipos_bp)
app.register_blueprint(evento_causas_bp)
app.register_blueprint(evento_origenes_bp)
app.register_blueprint(evento_estados_bp)
app.register_blueprint(evento_categorias_bp)
app.register_blueprint(recurso_tipos_bp)
app.register_blueprint(recurso_categorias_bp)
app.register_blueprint(recurso_grupos_bp)
app.register_blueprint(recursos_movilizados_bp)
app.register_blueprint(asistencia_entregada_bp)
app.register_blueprint(alojamientos_bp)
app.register_blueprint(alojamiento_estados_bp)
app.register_blueprint(alojamiento_situaciones_bp)
app.register_blueprint(alojamiento_tipos_bp)
app.register_blueprint(alojamientos_activados_bp)
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
app.register_blueprint(actas_coe_bp)
app.register_blueprint(acta_coe_resoluciones_bp)
app.register_blueprint(acta_coe_resolucion_mesas_bp)
app.register_blueprint(acta_coe_resolucion_estados_bp)
app.register_blueprint(acta_coe_estados_bp)
app.register_blueprint(afectacion_variable_registro_detalles_bp)
app.register_blueprint(acciones_respuesta_bp)
app.register_blueprint(accion_respuesta_origenes_bp)
app.register_blueprint(accion_respuesta_estados_bp)
app.register_blueprint(actividades_ejecucion_bp)
app.register_blueprint(actividad_ejecucion_apoyo_bp)
app.register_blueprint(actividad_ejecucion_dpa_bp)
app.register_blueprint(actividad_ejecucion_funciones_bp)
app.register_blueprint(evento_atencion_estados_bp)
app.register_blueprint(afectaciones_public_bp)
app.register_blueprint(eventos_historico_csv_bp)
app.register_blueprint(eventos_dashboard_csv_bp)



# Initialize Swagger after all blueprints are registered so Flasgger picks up docstrings from new modules
swagger = Swagger(app, template=swagger_template)

# Global before_request: require JWT for all endpoints except whitelist
WHITELIST_PATHS = [
    '/api/health',
    '/api/usuarios/login',
    '/api/usuarios',  # allow user creation (POST) - if you want it public
    '/eventos_historico',
    '/eventos_historico_json',
    '/eventos_dashboard_json',
    '/eventos_dashboard',
    '/apidocs',             # UI Swagger
    '/apidocs/',            # por si acaso
    '/flasgger_static',     # archivos estáticos de Swagger UI
    '/apispec_1.json'       # especificación de la API que consume Swagger
]

@app.before_request
def require_jwt_for_all():
    # Allow OPTIONS for CORS preflight
    if request.method == 'OPTIONS':
        return None
    path = request.path
    # Allow whitelisted paths
    if (
        path in WHITELIST_PATHS
        or path.startswith("/apidocs")
        or path.startswith("/flasgger_static")
        or path.startswith("/apispec")
        or path.startswith("/api/public")
    ):
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
