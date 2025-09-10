from flask import request, jsonify
from mesas import mesas_bp
from models import db
from datetime import datetime, timezone

@mesas_bp.route('/api/mesas', methods=['GET'])
def get_mesas():
    result = db.session.execute(db.text("SELECT * FROM mesas"))
    mesas = []
    for row in result:
        mesas.append({
            'id': row.id,
            'nombre': row.nombre,
            'siglas': row.siglas,
            'tipo_id': row.tipo_id,
            'estado': row.estado,
            'creador': row.creador,
            'creacion': row.creacion.isoformat() if row.creacion else None,
            'modificador': row.modificador,
            'modificacion': row.modificacion.isoformat() if row.modificacion else None
        })
    return jsonify(mesas)

@mesas_bp.route('/api/mesas', methods=['POST'])
def create_mesa():
    data = request.get_json()
    now = datetime.now(timezone.utc)
    
    query = db.text("""
        INSERT INTO mesas (nombre, siglas, tipo_id, estado, creador, creacion, modificador, modificacion)
        VALUES (:nombre, :siglas, :tipo_id, :estado, :creador, :creacion, :modificador, :modificacion)
        RETURNING id
    """)
    
    result = db.session.execute(query, {
        'nombre': data['nombre'],
        'siglas': data.get('siglas', ''),
        'tipo_id': data.get('tipo_id'),
        'estado': data.get('estado', 'Activo'),
        'creador': data.get('creador', 'Sistema'),
        'creacion': now,
        'modificador': data.get('creador', 'Sistema'),
        'modificacion': now
    })
    
    mesa_id = result.fetchone()[0]
    db.session.commit()
    
    mesa = db.session.execute(
        db.text("SELECT * FROM mesas WHERE id = :id"), 
        {'id': mesa_id}
    ).fetchone()
    
    return jsonify({
        'id': mesa.id,
        'nombre': mesa.nombre,
        'siglas': mesa.siglas,
        'tipo_id': mesa.tipo_id,
        'estado': mesa.estado,
        'creador': mesa.creador,
        'creacion': mesa.creacion.isoformat() if mesa.creacion else None,
        'modificador': mesa.modificador,
        'modificacion': mesa.modificacion.isoformat() if mesa.modificacion else None
    }), 201

@mesas_bp.route('/api/mesas/<int:id>', methods=['GET'])
def get_mesa(id):
    result = db.session.execute(
        db.text("SELECT * FROM mesas WHERE id = :id"), 
        {'id': id}
    )
    mesa = result.fetchone()
    
    if not mesa:
        return jsonify({'error': 'Mesa no encontrada'}), 404
    
    return jsonify({
        'id': mesa.id,
        'nombre': mesa.nombre,
        'siglas': mesa.siglas,
        'tipo_id': mesa.tipo_id,
        'estado': mesa.estado,
        'creador': mesa.creador,
        'creacion': mesa.creacion.isoformat() if mesa.creacion else None,
        'modificador': mesa.modificador,
        'modificacion': mesa.modificacion.isoformat() if mesa.modificacion else None
    })

@mesas_bp.route('/api/mesas/<int:id>', methods=['PUT'])
def update_mesa(id):
    data = request.get_json()
    now = datetime.now(timezone.utc)
    
    query = db.text("""
        UPDATE mesas 
        SET nombre = :nombre, 
            siglas = :siglas, 
            tipo_id = :tipo_id, 
            estado = :estado, 
            modificador = :modificador, 
            modificacion = :modificacion
        WHERE id = :id
    """)
    
    result = db.session.execute(query, {
        'id': id,
        'nombre': data.get('nombre'),
        'siglas': data.get('siglas'),
        'tipo_id': data.get('tipo_id'),
        'estado': data.get('estado'),
        'modificador': data.get('modificador', 'Sistema'),
        'modificacion': now
    })
    
    if result.rowcount == 0:
        return jsonify({'error': 'Mesa no encontrada'}), 404
    
    db.session.commit()
    
    mesa = db.session.execute(
        db.text("SELECT * FROM mesas WHERE id = :id"), 
        {'id': id}
    ).fetchone()
    
    return jsonify({
        'id': mesa.id,
        'nombre': mesa.nombre,
        'siglas': mesa.siglas,
        'tipo_id': mesa.tipo_id,
        'estado': mesa.estado,
        'creador': mesa.creador,
        'creacion': mesa.creacion.isoformat() if mesa.creacion else None,
        'modificador': mesa.modificador,
        'modificacion': mesa.modificacion.isoformat() if mesa.modificacion else None
    })

@mesas_bp.route('/api/mesas/<int:id>', methods=['DELETE'])
def delete_mesa(id):
    result = db.session.execute(
        db.text("DELETE FROM mesas WHERE id = :id"), 
        {'id': id}
    )
    
    if result.rowcount == 0:
        return jsonify({'error': 'Mesa no encontrada'}), 404
    
    db.session.commit()
    return jsonify({'mensaje': 'Mesa eliminada correctamente'})