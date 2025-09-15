from flask import request, jsonify
from opciones import opciones_bp
from models import db
from datetime import datetime, timezone

@opciones_bp.route('/api/opciones', methods=['GET'])
def get_opciones():
    result = db.session.execute(db.text("SELECT * FROM opciones"))
    opciones = []
    for row in result:
        opciones.append({
            'id': row.id,
            'nombre': row.nombre,
            'abreviatura': row.abreviatura,
            'ruta': row.ruta,
            'activo': row.activo,
            'creador': row.creador,
            'creacion': row.creacion.isoformat() if row.creacion else None,
            'modificador': row.modificador,
            'modificacion': row.modificacion.isoformat() if row.modificacion else None
        })
    return jsonify(opciones)

@opciones_bp.route('/api/opciones', methods=['POST'])
def create_opcion():
    data = request.get_json()
    now = datetime.now(timezone.utc)
    
    query = db.text("""
        INSERT INTO opciones (nombre, abreviatura, ruta, activo, creador, creacion, modificador, modificacion)
        VALUES (:nombre, :abreviatura, :ruta, :activo, :creador, :creacion, :modificador, :modificacion)
        RETURNING id
    """)
    
    result = db.session.execute(query, {
        'nombre': data['nombre'],
        'abreviatura': data['abreviatura'],
        'ruta': data.get('ruta'),
        'activo': data.get('activo', True),
        'creador': data.get('creador', 'Sistema'),
        'creacion': now,
        'modificador': data.get('creador', 'Sistema'),
        'modificacion': now
    })
    
    opcion_id = result.fetchone()[0]
    db.session.commit()
    
    opcion = db.session.execute(
        db.text("SELECT * FROM opciones WHERE id = :id"), 
        {'id': opcion_id}
    ).fetchone()
    
    return jsonify({
        'id': opcion.id,
        'nombre': opcion.nombre,
        'abreviatura': opcion.abreviatura,
        'ruta': opcion.ruta,
        'activo': opcion.activo,
        'creador': opcion.creador,
        'creacion': opcion.creacion.isoformat() if opcion.creacion else None,
        'modificador': opcion.modificador,
        'modificacion': opcion.modificacion.isoformat() if opcion.modificacion else None
    }), 201

@opciones_bp.route('/api/opciones/<int:id>', methods=['GET'])
def get_opcion(id):
    result = db.session.execute(
        db.text("SELECT * FROM opciones WHERE id = :id"), 
        {'id': id}
    )
    opcion = result.fetchone()
    
    if not opcion:
        return jsonify({'error': 'Opción no encontrada'}), 404
    
    return jsonify({
        'id': opcion.id,
        'nombre': opcion.nombre,
        'abreviatura': opcion.abreviatura,
        'ruta': opcion.ruta,
        'activo': opcion.activo,
        'creador': opcion.creador,
        'creacion': opcion.creacion.isoformat() if opcion.creacion else None,
        'modificador': opcion.modificador,
        'modificacion': opcion.modificacion.isoformat() if opcion.modificacion else None
    })

@opciones_bp.route('/api/opciones/<int:id>', methods=['PUT'])
def update_opcion(id):
    data = request.get_json()
    now = datetime.now(timezone.utc)
    
    query = db.text("""
        UPDATE opciones 
        SET nombre = :nombre, 
            abreviatura = :abreviatura, 
            ruta = :ruta, 
            activo = :activo, 
            modificador = :modificador, 
            modificacion = :modificacion
        WHERE id = :id
    """)
    
    result = db.session.execute(query, {
        'id': id,
        'nombre': data.get('nombre'),
        'abreviatura': data.get('abreviatura'),
        'ruta': data.get('ruta'),
        'activo': data.get('activo'),
        'modificador': data.get('modificador', 'Sistema'),
        'modificacion': now
    })
    
    if result.rowcount == 0:
        return jsonify({'error': 'Opción no encontrada'}), 404
    
    db.session.commit()
    
    opcion = db.session.execute(
        db.text("SELECT * FROM opciones WHERE id = :id"), 
        {'id': id}
    ).fetchone()
    
    return jsonify({
        'id': opcion.id,
        'nombre': opcion.nombre,
        'abreviatura': opcion.abreviatura,
        'ruta': opcion.ruta,
        'activo': opcion.activo,
        'creador': opcion.creador,
        'creacion': opcion.creacion.isoformat() if opcion.creacion else None,
        'modificador': opcion.modificador,
        'modificacion': opcion.modificacion.isoformat() if opcion.modificacion else None
    })

@opciones_bp.route('/api/opciones/<int:id>', methods=['DELETE'])
def delete_opcion(id):
    result = db.session.execute(
        db.text("DELETE FROM opciones WHERE id = :id"), 
        {'id': id}
    )
    
    if result.rowcount == 0:
        return jsonify({'error': 'Opción no encontrada'}), 404
    
    db.session.commit()
    return jsonify({'mensaje': 'Opción eliminada correctamente'})
