from flask import request, jsonify
from parroquias import parroquias_bp
from models import db
from datetime import datetime, timezone

@parroquias_bp.route('/api/parroquias', methods=['GET'])
def get_parroquias():
    result = db.session.execute(db.text("SELECT * FROM parroquias"))
    parroquias = []
    for row in result:
        parroquias.append({
            'id': row.id,
            'provincia_id': row.provincia_id,
            'canton_id': row.canton_id,
            'dpa': row.dpa,
            'nombre': row.nombre,
            'abreviatura': row.abreviatura,
            'activo': row.activo,
            'creador': row.creador,
            'creacion': row.creacion.isoformat() if row.creacion else None,
            'modificador': row.modificador,
            'modificacion': row.modificacion.isoformat() if row.modificacion else None
        })
    return jsonify(parroquias)

@parroquias_bp.route('/api/parroquias', methods=['POST'])
def create_parroquia():
    data = request.get_json()
    now = datetime.now(timezone.utc)
    
    query = db.text("""
        INSERT INTO parroquias (provincia_id, canton_id, dpa, nombre, abreviatura, activo, creador, creacion, modificador, modificacion)
        VALUES (:provincia_id, :canton_id, :dpa, :nombre, :abreviatura, :activo, :creador, :creacion, :modificador, :modificacion)
        RETURNING id
    """)
    
    result = db.session.execute(query, {
        'provincia_id': data['provincia_id'],
        'canton_id': data['canton_id'],
        'dpa': data.get('dpa'),
        'nombre': data['nombre'],
        'abreviatura': data.get('abreviatura'),
        'activo': data.get('activo', True),
        'creador': data.get('creador', 'Sistema'),
        'creacion': now,
        'modificador': data.get('creador', 'Sistema'),
        'modificacion': now
    })
    
    parroquia_id = result.fetchone()[0]
    db.session.commit()
    
    parroquia = db.session.execute(
        db.text("SELECT * FROM parroquias WHERE id = :id"), 
        {'id': parroquia_id}
    ).fetchone()
    
    return jsonify({
        'id': parroquia.id,
        'provincia_id': parroquia.provincia_id,
        'canton_id': parroquia.canton_id,
        'dpa': parroquia.dpa,
        'nombre': parroquia.nombre,
        'abreviatura': parroquia.abreviatura,
        'activo': parroquia.activo,
        'creador': parroquia.creador,
        'creacion': parroquia.creacion.isoformat() if parroquia.creacion else None,
        'modificador': parroquia.modificador,
        'modificacion': parroquia.modificacion.isoformat() if parroquia.modificacion else None
    }), 201

@parroquias_bp.route('/api/parroquias/<int:id>', methods=['GET'])
def get_parroquia(id):
    result = db.session.execute(
        db.text("SELECT * FROM parroquias WHERE id = :id"), 
        {'id': id}
    )
    parroquia = result.fetchone()
    
    if not parroquia:
        return jsonify({'error': 'Parroquia no encontrada'}), 404
    
    return jsonify({
        'id': parroquia.id,
        'provincia_id': parroquia.provincia_id,
        'canton_id': parroquia.canton_id,
        'dpa': parroquia.dpa,
        'nombre': parroquia.nombre,
        'abreviatura': parroquia.abreviatura,
        'activo': parroquia.activo,
        'creador': parroquia.creador,
        'creacion': parroquia.creacion.isoformat() if parroquia.creacion else None,
        'modificador': parroquia.modificador,
        'modificacion': parroquia.modificacion.isoformat() if parroquia.modificacion else None
    })

@parroquias_bp.route('/api/parroquias/<int:id>', methods=['PUT'])
def update_parroquia(id):
    data = request.get_json()
    now = datetime.now(timezone.utc)
    
    query = db.text("""
        UPDATE parroquias 
        SET provincia_id = :provincia_id, 
            canton_id = :canton_id, 
            dpa = :dpa, 
            nombre = :nombre, 
            abreviatura = :abreviatura, 
            activo = :activo, 
            modificador = :modificador, 
            modificacion = :modificacion
        WHERE id = :id
    """)
    
    result = db.session.execute(query, {
        'id': id,
        'provincia_id': data.get('provincia_id'),
        'canton_id': data.get('canton_id'),
        'dpa': data.get('dpa'),
        'nombre': data.get('nombre'),
        'abreviatura': data.get('abreviatura'),
        'activo': data.get('activo'),
        'modificador': data.get('modificador', 'Sistema'),
        'modificacion': now
    })
    
    if result.rowcount == 0:
        return jsonify({'error': 'Parroquia no encontrada'}), 404
    
    db.session.commit()
    
    parroquia = db.session.execute(
        db.text("SELECT * FROM parroquias WHERE id = :id"), 
        {'id': id}
    ).fetchone()
    
    return jsonify({
        'id': parroquia.id,
        'provincia_id': parroquia.provincia_id,
        'canton_id': parroquia.canton_id,
        'dpa': parroquia.dpa,
        'nombre': parroquia.nombre,
        'abreviatura': parroquia.abreviatura,
        'activo': parroquia.activo,
        'creador': parroquia.creador,
        'creacion': parroquia.creacion.isoformat() if parroquia.creacion else None,
        'modificador': parroquia.modificador,
        'modificacion': parroquia.modificacion.isoformat() if parroquia.modificacion else None
    })

@parroquias_bp.route('/api/parroquias/<int:id>', methods=['DELETE'])
def delete_parroquia(id):
    result = db.session.execute(
        db.text("DELETE FROM parroquias WHERE id = :id"), 
        {'id': id}
    )
    
    if result.rowcount == 0:
        return jsonify({'error': 'Parroquia no encontrada'}), 404
    
    db.session.commit()
    return jsonify({'mensaje': 'Parroquia eliminada correctamente'})