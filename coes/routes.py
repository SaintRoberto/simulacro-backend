from flask import request, jsonify
from coes import coes_bp
from models import db
from datetime import datetime, timezone

@coes_bp.route('/api/coes', methods=['GET'])
def get_coes():
    result = db.session.execute(db.text("SELECT * FROM coes"))
    coes = []
    for row in result:
        coes.append({
            'id': row.id,
            'nombre': row.nombre,
            'siglas': row.siglas,
            'descripcion': row.descripcion,
            'estado': row.estado,
            'creador': row.creador,
            'creacion': row.creacion.isoformat() if row.creacion else None,
            'modificador': row.modificador,
            'modificacion': row.modificacion.isoformat() if row.modificacion else None
        })
    return jsonify(coes)

@coes_bp.route('/api/coes', methods=['POST'])
def create_coe():
    data = request.get_json()
    now = datetime.now(timezone.utc)
    
    query = db.text("""
        INSERT INTO coes (nombre, siglas, descripcion, estado, creador, creacion, modificador, modificacion)
        VALUES (:nombre, :siglas, :descripcion, :estado, :creador, :creacion, :modificador, :modificacion)
        RETURNING id
    """)
    
    result = db.session.execute(query, {
        'nombre': data['nombre'],
        'siglas': data.get('siglas', ''),
        'descripcion': data.get('descripcion', ''),
        'estado': data.get('estado', 'Activo'),
        'creador': data.get('creador', 'Sistema'),
        'creacion': now,
        'modificador': data.get('creador', 'Sistema'),
        'modificacion': now
    })
    
    coe_id = result.fetchone()[0]
    db.session.commit()
    
    coe = db.session.execute(
        db.text("SELECT * FROM coes WHERE id = :id"), 
        {'id': coe_id}
    ).fetchone()
    
    return jsonify({
        'id': coe.id,
        'nombre': coe.nombre,
        'siglas': coe.siglas,
        'descripcion': coe.descripcion,
        'estado': coe.estado,
        'creador': coe.creador,
        'creacion': coe.creacion.isoformat() if coe.creacion else None,
        'modificador': coe.modificador,
        'modificacion': coe.modificacion.isoformat() if coe.modificacion else None
    }), 201

@coes_bp.route('/api/coes/<int:id>', methods=['GET'])
def get_coe(id):
    result = db.session.execute(
        db.text("SELECT * FROM coes WHERE id = :id"), 
        {'id': id}
    )
    coe = result.fetchone()
    
    if not coe:
        return jsonify({'error': 'COE no encontrado'}), 404
    
    return jsonify({
        'id': coe.id,
        'nombre': coe.nombre,
        'siglas': coe.siglas,
        'descripcion': coe.descripcion,
        'estado': coe.estado,
        'creador': coe.creador,
        'creacion': coe.creacion.isoformat() if coe.creacion else None,
        'modificador': coe.modificador,
        'modificacion': coe.modificacion.isoformat() if coe.modificacion else None
    })

@coes_bp.route('/api/coes/<int:id>', methods=['PUT'])
def update_coe(id):
    data = request.get_json()
    now = datetime.now(timezone.utc)
    
    query = db.text("""
        UPDATE coes 
        SET nombre = :nombre, 
            siglas = :siglas, 
            descripcion = :descripcion, 
            estado = :estado, 
            modificador = :modificador, 
            modificacion = :modificacion
        WHERE id = :id
    """)
    
    result = db.session.execute(query, {
        'id': id,
        'nombre': data.get('nombre'),
        'siglas': data.get('siglas'),
        'descripcion': data.get('descripcion'),
        'estado': data.get('estado'),
        'modificador': data.get('modificador', 'Sistema'),
        'modificacion': now
    })
    
    if result.rowcount == 0:
        return jsonify({'error': 'COE no encontrado'}), 404
    
    db.session.commit()
    
    coe = db.session.execute(
        db.text("SELECT * FROM coes WHERE id = :id"), 
        {'id': id}
    ).fetchone()
    
    return jsonify({
        'id': coe.id,
        'nombre': coe.nombre,
        'siglas': coe.siglas,
        'descripcion': coe.descripcion,
        'estado': coe.estado,
        'creador': coe.creador,
        'creacion': coe.creacion.isoformat() if coe.creacion else None,
        'modificador': coe.modificador,
        'modificacion': coe.modificacion.isoformat() if coe.modificacion else None
    })

@coes_bp.route('/api/coes/<int:id>', methods=['DELETE'])
def delete_coe(id):
    result = db.session.execute(
        db.text("DELETE FROM coes WHERE id = :id"), 
        {'id': id}
    )
    
    if result.rowcount == 0:
        return jsonify({'error': 'COE no encontrado'}), 404
    
    db.session.commit()
    return jsonify({'mensaje': 'COE eliminado correctamente'})