from flask import request, jsonify
from niveles_afectacion import niveles_afectacion_bp
from models import db
from datetime import datetime, timezone

@niveles_afectacion_bp.route('/api/niveles-afectacion', methods=['GET'])
def get_niveles_afectacion():
    result = db.session.execute(db.text("SELECT * FROM niveles_afectacion"))
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

@niveles_afectacion_bp.route('/api/niveles-afectacion', methods=['POST'])
def create_nivel_afectacion():
    data = request.get_json()
    now = datetime.now(timezone.utc)
    
    # Validate required fields
    if not data or not data.get('nombre'):
        return jsonify({'error': 'Field "nombre" is required'}), 400

    query = db.text("""
        INSERT INTO niveles_afectacion (nombre, descripcion, activo, creador, creacion, modificador, modificacion)
        VALUES (:nombre, :descripcion, :activo, :creador, :creacion, :modificador, :modificacion)
        RETURNING id
    """)

    # prefer an explicit modificador if provided, otherwise fall back to creador or 'Sistema'
    modificador_value = data.get('modificador', data.get('creador', 'Sistema'))

    result = db.session.execute(query, {
        'nombre': data.get('nombre'),
        'descripcion': data.get('descripcion'),
        'activo': data.get('activo', True),
        'creador': data.get('creador', 'Sistema'),
        'creacion': now,
        'modificador': modificador_value,
        'modificacion': now
    })

    row = result.fetchone()
    if row is None:
        # If INSERT didn't return an id, rollback and return an error
        try:
            db.session.rollback()
        except Exception:
            pass
        return jsonify({'error': 'Failed to create nivel'}), 500

    nivel_id = row[0]
    db.session.commit()

    nivel = db.session.execute(
        db.text("SELECT * FROM niveles_afectacion WHERE id = :id"),
        {'id': nivel_id}
    ).fetchone()

    if nivel is None:
        # This is unexpected after a successful insert/commit; return server error
        return jsonify({'error': 'Created nivel could not be retrieved'}), 500

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

@niveles_afectacion_bp.route('/api/niveles-afectacion/<int:id>', methods=['GET'])
def get_nivel_afectacion(id):
    result = db.session.execute(
        db.text("SELECT * FROM niveles_afectacion WHERE id = :id"), 
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

@niveles_afectacion_bp.route('/api/niveles-afectacion/<int:id>', methods=['PUT'])
def update_nivel_afectacion(id):
    data = request.get_json()
    now = datetime.now(timezone.utc)
    
    query = db.text("""
        UPDATE niveles_afectacion 
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
    
    if getattr(result, 'rowcount', 0) == 0:
        return jsonify({'error': 'Nivel no encontrado'}), 404
    
    db.session.commit()
    
    nivel = db.session.execute(
        db.text("SELECT * FROM niveles_afectacion WHERE id = :id"),
        {'id': id}
    ).fetchone()

    if nivel is None:
        # This is unexpected because we checked rowcount above, but handle defensively
        return jsonify({'error': 'Nivel could not be retrieved after update'}), 500

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

@niveles_afectacion_bp.route('/api/niveles-afectacion/<int:id>', methods=['DELETE'])
def delete_nivel_afectacion(id):
    result = db.session.execute(
        db.text("DELETE FROM niveles_afectacion WHERE id = :id"), 
        {'id': id}
    )
    
    if getattr(result, 'rowcount', 0) == 0:
        return jsonify({'error': 'Nivel no encontrado'}), 404
    
    db.session.commit()
    return jsonify({'mensaje': 'Nivel eliminado correctamente'})
