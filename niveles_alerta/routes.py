from flask import request, jsonify
from niveles_alerta import niveles_alerta_bp
from models import db
from datetime import datetime, timezone

from utils.db_helpers import check_row_or_abort
@niveles_alerta_bp.route('/api/niveles-alerta', methods=['GET'])
def get_niveles_alerta():
    result = db.session.execute(db.text("SELECT * FROM niveles_alerta"))
    niveles = []
    for row in result:
        niveles.append({
            'id': row.id,
            'nombre': row.nombre,
            'descripcion': row.descripcion,
            'activo': row.activo,
            'creador': row.creador,
            'creacion': row.creacion.isoformat() if row.creacion else None,
            'modificador': row.modificador,
            'modificacion': row.modificacion.isoformat() if row.modificacion else None
        })
    return jsonify(niveles)

@niveles_alerta_bp.route('/api/niveles-alerta', methods=['POST'])
def create_nivel_alerta():
    data = request.get_json() or {}
    # Validate required fields
    if 'nombre' not in data or not data.get('nombre'):
        return jsonify({'error': 'El campo "nombre" es obligatorio'}), 400

    now = datetime.now(timezone.utc)

    query = db.text("""
        INSERT INTO niveles_alerta (nombre, descripcion, activo, creador, creacion, modificador, modificacion)
        VALUES (:nombre, :descripcion, :activo, :creador, :creacion, :modificador, :modificacion)
        RETURNING id
    """)

    result = db.session.execute(query, {
        'nombre': data['nombre'],
        'descripcion': data.get('descripcion'),
        'activo': data.get('activo', True),
        'creador': data.get('creador', 'Sistema'),
        'creacion': now,
        # Prefer explicit 'modificador' if provided, otherwise fall back to 'modificador' or 'creador'
        'modificador': data.get('modificador', data.get('creador', 'Sistema')),
        'modificacion': now
    })

    row = result.fetchone()
    if row is None:
        # Rollback to keep session consistent on unexpected failure
        db.session.rollback()
        return jsonify({'error': 'Insert failed'}), 500

    nivel_id = row[0]
    db.session.commit()

    nivel = db.session.execute(
        db.text("SELECT * FROM niveles_alerta WHERE id = :id"),
        {'id': nivel_id}
    ).fetchone()

    if not nivel:
        # This is unexpected after a successful insert, return server error
        return jsonify({'error': 'Nivel creado pero no encontrado'}), 500

    return jsonify({
        'id': nivel.id,
        'nombre': nivel.nombre,
        'descripcion': nivel.descripcion,
        'activo': nivel.activo,
        'creador': nivel.creador,
        'creacion': nivel.creacion.isoformat() if nivel.creacion else None,
        'modificador': nivel.modificador,
        'modificacion': nivel.modificacion.isoformat() if nivel.modificacion else None
    }), 201

@niveles_alerta_bp.route('/api/niveles-alerta/<int:id>', methods=['GET'])
def get_nivel_alerta(id):
    result = db.session.execute(
        db.text("SELECT * FROM niveles_alerta WHERE id = :id"), 
        {'id': id}
    )
    nivel = result.fetchone()
    
    if not nivel:
        return jsonify({'error': 'Nivel no encontrado'}), 404
    
    return jsonify({
        'id': nivel.id,
        'nombre': nivel.nombre,
        'descripcion': nivel.descripcion,
        'activo': nivel.activo,
        'creador': nivel.creador,
        'creacion': nivel.creacion.isoformat() if nivel.creacion else None,
        'modificador': nivel.modificador,
        'modificacion': nivel.modificacion.isoformat() if nivel.modificacion else None
    })

@niveles_alerta_bp.route('/api/niveles-alerta/<int:id>', methods=['PUT'])
def update_nivel_alerta(id):
    data = request.get_json() or {}

    # Optional: validate at least one field is provided to update
    if not data:
        return jsonify({'error': 'No data provided for update'}), 400

    now = datetime.now(timezone.utc)

    query = db.text("""
        UPDATE niveles_alerta
        SET nombre = :nombre,
            descripcion = :descripcion,
            activo = :activo,
            modificador = :modificador,
            modificacion = :modificacion
        WHERE id = :id
    """)

    result = db.session.execute(query, {
        'id': id,
        'nombre': data.get('nombre'),
        'descripcion': data.get('descripcion'),
        'activo': data.get('activo'),
        'modificador': data.get('modificador', 'Sistema'),
        'modificacion': now
    })

    # Some DB drivers may not populate rowcount; keep the existing safe check
    if getattr(result, 'rowcount', 0) == 0:
        db.session.rollback()
        return jsonify({'error': 'Nivel no encontrado'}), 404

    db.session.commit()

    nivel = db.session.execute(
        db.text("SELECT * FROM niveles_alerta WHERE id = :id"),
        {'id': id}
    ).fetchone()

    if not nivel:
        # This would be unexpected after a successful update, return server error
        return jsonify({'error': 'Nivel actualizado pero no encontrado'}), 500

    return jsonify({
        'id': nivel.id,
        'nombre': nivel.nombre,
        'descripcion': nivel.descripcion,
        'activo': nivel.activo,
        'creador': nivel.creador,
        'creacion': nivel.creacion.isoformat() if nivel.creacion else None,
        'modificador': nivel.modificador,
        'modificacion': nivel.modificacion.isoformat() if nivel.modificacion else None
    })

@niveles_alerta_bp.route('/api/niveles-alerta/<int:id>', methods=['DELETE'])
def delete_nivel_alerta(id):
    result = db.session.execute(
        db.text("DELETE FROM niveles_alerta WHERE id = :id"), 
        {'id': id}
    )
    
    if getattr(result, 'rowcount', 0) == 0:
        return jsonify({'error': 'Nivel no encontrado'}), 404
    
    db.session.commit()
    return jsonify({'mensaje': 'Nivel eliminado correctamente'})
