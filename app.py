from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy
from config import DATABASE_URL

app = Flask(__name__)

# Configuración de la base de datos
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Inicializar SQLAlchemy
from models import db
db.init_app(app)

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

# Ruta de salud
@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({'estado': 'OK', 'mensaje': 'API funcionando correctamente'})

# Inicializar base de datos
with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
