from flask import request, jsonify
from niveles_alerta import niveles_alerta_bp
from models import db
from datetime import datetime, timezone

@niveles_alerta_bp.route('/api/niveles-alerta', methods=['GET'])
def get_niveles_alerta():
    result = db.session.execute(db.text("SELECT * FROM niveles_alerta"))
    niveles = []
    for row in result:
        niveles.append({
            'id': row.id,
            'nombre': row.nombre,
            'descripcion': row.descripcion,
            'estado': row.estado,
            'creador': row.creador,
            'creacion': row.creacion.isoformat() if row.creacion else None,
            'modificador': row.modificador,
            'modificacion': row.modificacion.isoformat() if row.modificacion else None
        })
    return jsonify(niveles)

@niveles_alerta_bp.route('/api/niveles-alerta', methods=['POST'])
def create_nivel_alerta():
    data = request.get_json()
    now = datetime.now(timezone.utc)
    
    query = db.text("""
        INSERT INTO niveles_alerta (nombre, descripcion, estado, creador, creacion, modificador, modificacion)
        VALUES (:nombre, :descripcion, :estado, :creador, :creacion, :modificador, :modificacion)
        RETURNING id
    """)
    
    result = db.session.execute(query, {
        'nombre': data['nombre'],
        'descripcion': data.get('descripcion'),
        'estado': data.get('estado', True),
        'creador': data.get('creador', 'Sistema'),
        'creacion': now,
        'modificador': data.get('creador', 'Sistema'),
        'modificacion': now
    })
    
    nivel_id = result.fetchone()[0]
    db.session.commit()
    
    nivel = db.session.execute(
        db.text("SELECT * FROM niveles_alerta WHERE id = :id"), 
        {'id': nivel_id}
    ).fetchone()
    
    return jsonify({
        'id': nivel.id,
        'nombre': nivel.nombre,
        'descripcion': nivel.descripcion,
        'estado': nivel.estado,
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
        'estado': nivel.estado,
        'creador': nivel.creador,
        'creacion': nivel.creacion.isoformat() if nivel.creacion else None,
        'modificador': nivel.modificador,
        'modificacion': nivel.modificacion.isoformat() if nivel.modificacion else None
    })

@niveles_alerta_bp.route('/api/niveles-alerta/<int:id>', methods=['PUT'])
def update_nivel_alerta(id):
    data = request.get_json()
    now = datetime.now(timezone.utc)
    
    query = db.text("""
        UPDATE niveles_alerta 
        SET nombre = :nombre, 
            descripcion = :descripcion, 
            estado = :estado, 
            modificador = :modificador, 
            modificacion = :modificacion
        WHERE id = :id
    """)
    
    result = db.session.execute(query, {
        'id': id,
        'nombre': data.get('nombre'),
        'descripcion': data.get('descripcion'),
        'estado': data.get('estado'),
        'modificador': data.get('modificador', 'Sistema'),
        'modificacion': now
    })
    
    if result.rowcount == 0:
        return jsonify({'error': 'Nivel no encontrado'}), 404
    
    db.session.commit()
    
    nivel = db.session.execute(
        db.text("SELECT * FROM niveles_alerta WHERE id = :id"), 
        {'id': id}
    ).fetchone()
    
    return jsonify({
        'id': nivel.id,
        'nombre': nivel.nombre,
        'descripcion': nivel.descripcion,
        'estado': nivel.estado,
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
    
    if result.rowcount == 0:
        return jsonify({'error': 'Nivel no encontrado'}), 404
    
    db.session.commit()
    return jsonify({'mensaje': 'Nivel eliminado correctamente'})
