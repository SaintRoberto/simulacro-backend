from flask import request, jsonify
from provincias import provincias_bp
from models import db
from datetime import datetime, timezone

@provincias_bp.route('/api/provincias', methods=['GET'])
def get_provincias():
    result = db.session.execute(db.text("SELECT * FROM provincias"))
    provincias = []
    for row in result:
        provincias.append({
            'id': row.id,
            'dpa': row.dpa,
            'nombre': row.nombre,
            'abreviatura': row.abreviatura,
            'estado': row.estado,
            'creador': row.creador,
            'creacion': row.creacion.isoformat() if row.creacion else None,
            'modificador': row.modificador,
            'modificacion': row.modificacion.isoformat() if row.modificacion else None
        })
    return jsonify(provincias)

@provincias_bp.route('/api/provincias', methods=['POST'])
def create_provincia():
    data = request.get_json()
    now = datetime.now(timezone.utc)
    
    query = db.text("""
        INSERT INTO provincias (dpa, nombre, abreviatura, estado, creador, creacion, modificador, modificacion)
        VALUES (:dpa, :nombre, :abreviatura, :estado, :creador, :creacion, :modificador, :modificacion)
        RETURNING id
    """)
    
    result = db.session.execute(query, {
        'dpa': data['dpa'],
        'nombre': data['nombre'],
        'abreviatura': data.get('abreviatura', ''),
        'estado': data.get('estado', 'Activo'),
        'creador': data.get('creador', 'Sistema'),
        'creacion': now,
        'modificador': data.get('creador', 'Sistema'),
        'modificacion': now
    })
    
    provincia_id = result.fetchone()[0]
    db.session.commit()
    
    provincia = db.session.execute(
        db.text("SELECT * FROM provincias WHERE id = :id"), 
        {'id': provincia_id}
    ).fetchone()
    
    return jsonify({
        'id': provincia.id,
        'dpa': provincia.dpa,
        'nombre': provincia.nombre,
        'abreviatura': provincia.abreviatura,
        'estado': provincia.estado,
        'creador': provincia.creador,
        'creacion': provincia.creacion.isoformat() if provincia.creacion else None,
        'modificador': provincia.modificador,
        'modificacion': provincia.modificacion.isoformat() if provincia.modificacion else None
    }), 201

@provincias_bp.route('/api/provincias/<int:id>', methods=['GET'])
def get_provincia(id):
    result = db.session.execute(
        db.text("SELECT * FROM provincias WHERE id = :id"), 
        {'id': id}
    )
    provincia = result.fetchone()
    
    if not provincia:
        return jsonify({'error': 'Provincia no encontrada'}), 404
    
    return jsonify({
        'id': provincia.id,
        'dpa': provincia.dpa,
        'nombre': provincia.nombre,
        'abreviatura': provincia.abreviatura,
        'estado': provincia.estado,
        'creador': provincia.creador,
        'creacion': provincia.creacion.isoformat() if provincia.creacion else None,
        'modificador': provincia.modificador,
        'modificacion': provincia.modificacion.isoformat() if provincia.modificacion else None
    })

@provincias_bp.route('/api/provincias/<int:id>', methods=['PUT'])
def update_provincia(id):
    data = request.get_json()
    now = datetime.now(timezone.utc)
    
    query = db.text("""
        UPDATE provincias 
        SET dpa = :dpa, 
            nombre = :nombre, 
            abreviatura = :abreviatura, 
            estado = :estado, 
            modificador = :modificador, 
            modificacion = :modificacion
        WHERE id = :id
    """)
    
    result = db.session.execute(query, {
        'id': id,
        'dpa': data.get('dpa'),
        'nombre': data.get('nombre'),
        'abreviatura': data.get('abreviatura'),
        'estado': data.get('estado'),
        'modificador': data.get('modificador', 'Sistema'),
        'modificacion': now
    })
    
    if result.rowcount == 0:
        return jsonify({'error': 'Provincia no encontrada'}), 404
    
    db.session.commit()
    
    provincia = db.session.execute(
        db.text("SELECT * FROM provincias WHERE id = :id"), 
        {'id': id}
    ).fetchone()
    
    return jsonify({
        'id': provincia.id,
        'dpa': provincia.dpa,
        'nombre': provincia.nombre,
        'abreviatura': provincia.abreviatura,
        'estado': provincia.estado,
        'creador': provincia.creador,
        'creacion': provincia.creacion.isoformat() if provincia.creacion else None,
        'modificador': provincia.modificador,
        'modificacion': provincia.modificacion.isoformat() if provincia.modificacion else None
    })

@provincias_bp.route('/api/provincias/<int:id>', methods=['DELETE'])
def delete_provincia(id):
    result = db.session.execute(
        db.text("DELETE FROM provincias WHERE id = :id"), 
        {'id': id}
    )
    
    if result.rowcount == 0:
        return jsonify({'error': 'Provincia no encontrada'}), 404
    
    db.session.commit()
    return jsonify({'mensaje': 'Provincia eliminada correctamente'})