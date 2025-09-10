from flask import request, jsonify
from instituciones import instituciones_bp
from models import db
from datetime import datetime, timezone

@instituciones_bp.route('/api/instituciones', methods=['GET'])
def get_instituciones():
    result = db.session.execute(db.text("SELECT * FROM instituciones"))
    instituciones = []
    for row in result:
        instituciones.append({
            'id': row.id,
            'categoria_id': row.categoria_id,
            'nombre': row.nombre,
            'siglas': row.siglas,
            'estado': row.estado,
            'creador': row.creador,
            'creacion': row.creacion.isoformat() if row.creacion else None,
            'modificador': row.modificador,
            'modificacion': row.modificacion.isoformat() if row.modificacion else None
        })
    return jsonify(instituciones)

@instituciones_bp.route('/api/instituciones', methods=['POST'])
def create_institucion():
    data = request.get_json()
    now = datetime.now(timezone.utc)
    
    query = db.text("""
        INSERT INTO instituciones (categoria_id, nombre, siglas, estado, creador, creacion, modificador, modificacion)
        VALUES (:categoria_id, :nombre, :siglas, :estado, :creador, :creacion, :modificador, :modificacion)
        RETURNING id
    """)
    
    result = db.session.execute(query, {
        'categoria_id': data['categoria_id'],
        'nombre': data['nombre'],
        'siglas': data.get('siglas', ''),
        'estado': data.get('estado', 'Activo'),
        'creador': data.get('creador', 'Sistema'),
        'creacion': now,
        'modificador': data.get('creador', 'Sistema'),
        'modificacion': now
    })
    
    institucion_id = result.fetchone()[0]
    db.session.commit()
    
    institucion = db.session.execute(
        db.text("SELECT * FROM instituciones WHERE id = :id"), 
        {'id': institucion_id}
    ).fetchone()
    
    return jsonify({
        'id': institucion.id,
        'categoria_id': institucion.categoria_id,
        'nombre': institucion.nombre,
        'siglas': institucion.siglas,
        'estado': institucion.estado,
        'creador': institucion.creador,
        'creacion': institucion.creacion.isoformat() if institucion.creacion else None,
        'modificador': institucion.modificador,
        'modificacion': institucion.modificacion.isoformat() if institucion.modificacion else None
    }), 201

@instituciones_bp.route('/api/instituciones/<int:id>', methods=['GET'])
def get_institucion(id):
    result = db.session.execute(
        db.text("SELECT * FROM instituciones WHERE id = :id"), 
        {'id': id}
    )
    institucion = result.fetchone()
    
    if not institucion:
        return jsonify({'error': 'Institución no encontrada'}), 404
    
    return jsonify({
        'id': institucion.id,
        'categoria_id': institucion.categoria_id,
        'nombre': institucion.nombre,
        'siglas': institucion.siglas,
        'estado': institucion.estado,
        'creador': institucion.creador,
        'creacion': institucion.creacion.isoformat() if institucion.creacion else None,
        'modificador': institucion.modificador,
        'modificacion': institucion.modificacion.isoformat() if institucion.modificacion else None
    })

@instituciones_bp.route('/api/instituciones/<int:id>', methods=['PUT'])
def update_institucion(id):
    data = request.get_json()
    now = datetime.now(timezone.utc)
    
    query = db.text("""
        UPDATE instituciones 
        SET categoria_id = :categoria_id, 
            nombre = :nombre, 
            siglas = :siglas, 
            estado = :estado, 
            modificador = :modificador, 
            modificacion = :modificacion
        WHERE id = :id
    """)
    
    result = db.session.execute(query, {
        'id': id,
        'categoria_id': data.get('categoria_id'),
        'nombre': data.get('nombre'),
        'siglas': data.get('siglas'),
        'estado': data.get('estado'),
        'modificador': data.get('modificador', 'Sistema'),
        'modificacion': now
    })
    
    if result.rowcount == 0:
        return jsonify({'error': 'Institución no encontrada'}), 404
    
    db.session.commit()
    
    institucion = db.session.execute(
        db.text("SELECT * FROM instituciones WHERE id = :id"), 
        {'id': id}
    ).fetchone()
    
    return jsonify({
        'id': institucion.id,
        'categoria_id': institucion.categoria_id,
        'nombre': institucion.nombre,
        'siglas': institucion.siglas,
        'estado': institucion.estado,
        'creador': institucion.creador,
        'creacion': institucion.creacion.isoformat() if institucion.creacion else None,
        'modificador': institucion.modificador,
        'modificacion': institucion.modificacion.isoformat() if institucion.modificacion else None
    })

@instituciones_bp.route('/api/instituciones/<int:id>', methods=['DELETE'])
def delete_institucion(id):
    result = db.session.execute(
        db.text("DELETE FROM instituciones WHERE id = :id"), 
        {'id': id}
    )
    
    if result.rowcount == 0:
        return jsonify({'error': 'Institución no encontrada'}), 404
    
    db.session.commit()
    return jsonify({'mensaje': 'Institución eliminada correctamente'})
