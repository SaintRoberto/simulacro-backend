from flask import request, jsonify
from cantones import cantones_bp
from models import db
from datetime import datetime, timezone

@cantones_bp.route('/api/cantones', methods=['GET'])
def get_cantones():
    result = db.session.execute(db.text("SELECT * FROM cantones"))
    cantones = []
    for row in result:
        cantones.append({
            'id': row.id,
            'provincia_id': row.provincia_id,
            'dpa': row.dpa,
            'nombre': row.nombre,
            'abreviatura': row.abreviatura,
            'estado': row.estado,
            'creador': row.creador,
            'creacion': row.creacion.isoformat() if row.creacion else None,
            'modificador': row.modificador,
            'modificacion': row.modificacion.isoformat() if row.modificacion else None
        })
    return jsonify(cantones)

@cantones_bp.route('/api/cantones', methods=['POST'])
def create_canton():
    data = request.get_json()
    now = datetime.now(timezone.utc)
    
    query = db.text("""
        INSERT INTO cantones (provincia_id, dpa, nombre, abreviatura, estado, creador, creacion, modificador, modificacion)
        VALUES (:provincia_id, :dpa, :nombre, :abreviatura, :estado, :creador, :creacion, :modificador, :modificacion)
        RETURNING id
    """)
    
    result = db.session.execute(query, {
        'provincia_id': data['provincia_id'],
        'dpa': data['dpa'],
        'nombre': data['nombre'],
        'abreviatura': data.get('abreviatura', ''),
        'estado': data.get('estado', 'Activo'),
        'creador': data.get('creador', 'Sistema'),
        'creacion': now,
        'modificador': data.get('creador', 'Sistema'),
        'modificacion': now
    })
    
    canton_id = result.fetchone()[0]
    db.session.commit()
    
    canton = db.session.execute(
        db.text("SELECT * FROM cantones WHERE id = :id"), 
        {'id': canton_id}
    ).fetchone()
    
    return jsonify({
        'id': canton.id,
        'provincia_id': canton.provincia_id,
        'dpa': canton.dpa,
        'nombre': canton.nombre,
        'abreviatura': canton.abreviatura,
        'estado': canton.estado,
        'creador': canton.creador,
        'creacion': canton.creacion.isoformat() if canton.creacion else None,
        'modificador': canton.modificador,
        'modificacion': canton.modificacion.isoformat() if canton.modificacion else None
    }), 201

@cantones_bp.route('/api/cantones/<int:id>', methods=['GET'])
def get_canton(id):
    result = db.session.execute(
        db.text("SELECT * FROM cantones WHERE id = :id"), 
        {'id': id}
    )
    canton = result.fetchone()
    
    if not canton:
        return jsonify({'error': 'Cantón no encontrado'}), 404
    
    return jsonify({
        'id': canton.id,
        'provincia_id': canton.provincia_id,
        'dpa': canton.dpa,
        'nombre': canton.nombre,
        'abreviatura': canton.abreviatura,
        'estado': canton.estado,
        'creador': canton.creador,
        'creacion': canton.creacion.isoformat() if canton.creacion else None,
        'modificador': canton.modificador,
        'modificacion': canton.modificacion.isoformat() if canton.modificacion else None
    })

@cantones_bp.route('/api/cantones/<int:id>', methods=['PUT'])
def update_canton(id):
    data = request.get_json()
    now = datetime.now(timezone.utc)
    
    query = db.text("""
        UPDATE cantones 
        SET provincia_id = :provincia_id, 
            dpa = :dpa, 
            nombre = :nombre, 
            abreviatura = :abreviatura, 
            estado = :estado, 
            modificador = :modificador, 
            modificacion = :modificacion
        WHERE id = :id
    """)
    
    result = db.session.execute(query, {
        'id': id,
        'provincia_id': data.get('provincia_id'),
        'dpa': data.get('dpa'),
        'nombre': data.get('nombre'),
        'abreviatura': data.get('abreviatura'),
        'estado': data.get('estado'),
        'modificador': data.get('modificador', 'Sistema'),
        'modificacion': now
    })
    
    if result.rowcount == 0:
        return jsonify({'error': 'Cantón no encontrado'}), 404
    
    db.session.commit()
    
    canton = db.session.execute(
        db.text("SELECT * FROM cantones WHERE id = :id"), 
        {'id': id}
    ).fetchone()
    
    return jsonify({
        'id': canton.id,
        'provincia_id': canton.provincia_id,
        'dpa': canton.dpa,
        'nombre': canton.nombre,
        'abreviatura': canton.abreviatura,
        'estado': canton.estado,
        'creador': canton.creador,
        'creacion': canton.creacion.isoformat() if canton.creacion else None,
        'modificador': canton.modificador,
        'modificacion': canton.modificacion.isoformat() if canton.modificacion else None
    })

@cantones_bp.route('/api/cantones/<int:id>', methods=['DELETE'])
def delete_canton(id):
    result = db.session.execute(
        db.text("DELETE FROM cantones WHERE id = :id"), 
        {'id': id}
    )
    
    if result.rowcount == 0:
        return jsonify({'error': 'Cantón no encontrado'}), 404
    
    db.session.commit()
    return jsonify({'mensaje': 'Cantón eliminado correctamente'})