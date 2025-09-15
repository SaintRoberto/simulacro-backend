from flask import request, jsonify
from mesa_grupos import mesa_grupos_bp
from models import db
from datetime import datetime, timezone

@mesa_grupos_bp.route('/api/mesa-grupos', methods=['GET'])
def get_mesa_grupos():
    result = db.session.execute(db.text("SELECT * FROM mesa_grupos"))
    grupos = []
    for row in result:
        grupos.append({
            'id': row.id,
            'nombre': row.nombre,
            'abreviatura': row.abreviatura,
            'descripcion': row.descripcion,
            'activo': row.activo,
            'creador': row.creador,
            'creacion': row.creacion.isoformat() if row.creacion else None,
            'modificador': row.modificador,
            'modificacion': row.modificacion.isoformat() if row.modificacion else None
        })
    return jsonify(grupos)

@mesa_grupos_bp.route('/api/mesa-grupos', methods=['POST'])
def create_mesa_grupo():
    data = request.get_json()
    now = datetime.now(timezone.utc)
    
    query = db.text("""
        INSERT INTO mesa_grupos (nombre, abreviatura, descripcion, activo, creador, creacion, modificador, modificacion)
        VALUES (:nombre, :abreviatura, :descripcion, :activo, :creador, :creacion, :modificador, :modificacion)
        RETURNING id
    """)
    
    result = db.session.execute(query, {
        'nombre': data['nombre'],
        'abreviatura': data.get('abreviatura'),
        'descripcion': data.get('descripcion'),
        'activo': data.get('activo', True),
        'creador': data.get('creador', 'Sistema'),
        'creacion': now,
        'modificador': data.get('creador', 'Sistema'),
        'modificacion': now
    })
    
    grupo_id = result.fetchone()[0]
    db.session.commit()
    
    grupo = db.session.execute(
        db.text("SELECT * FROM mesa_grupos WHERE id = :id"), 
        {'id': grupo_id}
    ).fetchone()
    
    return jsonify({
        'id': grupo.id,
        'nombre': grupo.nombre,
        'abreviatura': grupo.abreviatura,
        'descripcion': grupo.descripcion,
        'activo': grupo.activo,
        'creador': grupo.creador,
        'creacion': grupo.creacion.isoformat() if grupo.creacion else None,
        'modificador': grupo.modificador,
        'modificacion': grupo.modificacion.isoformat() if grupo.modificacion else None
    }), 201

@mesa_grupos_bp.route('/api/mesa-grupos/<int:id>', methods=['GET'])
def get_mesa_grupo(id):
    result = db.session.execute(
        db.text("SELECT * FROM mesa_grupos WHERE id = :id"), 
        {'id': id}
    )
    grupo = result.fetchone()
    
    if not grupo:
        return jsonify({'error': 'Grupo no encontrado'}), 404
    
    return jsonify({
        'id': grupo.id,
        'nombre': grupo.nombre,
        'abreviatura': grupo.abreviatura,
        'descripcion': grupo.descripcion,
        'activo': grupo.activo,
        'creador': grupo.creador,
        'creacion': grupo.creacion.isoformat() if grupo.creacion else None,
        'modificador': grupo.modificador,
        'modificacion': grupo.modificacion.isoformat() if grupo.modificacion else None
    })

@mesa_grupos_bp.route('/api/mesa-grupos/<int:id>', methods=['PUT'])
def update_mesa_grupo(id):
    data = request.get_json()
    now = datetime.now(timezone.utc)
    
    query = db.text("""
        UPDATE mesa_grupos 
        SET nombre = :nombre, 
            abreviatura = :abreviatura, 
            descripcion = :descripcion, 
            activo = :activo, 
            modificador = :modificador, 
            modificacion = :modificacion
        WHERE id = :id
    """)
    
    result = db.session.execute(query, {
        'id': id,
        'nombre': data.get('nombre'),
        'abreviatura': data.get('abreviatura'),
        'descripcion': data.get('descripcion'),
        'activo': data.get('activo'),
        'modificador': data.get('modificador', 'Sistema'),
        'modificacion': now
    })
    
    if result.rowcount == 0:
        return jsonify({'error': 'Grupo no encontrado'}), 404
    
    db.session.commit()
    
    grupo = db.session.execute(
        db.text("SELECT * FROM mesa_grupos WHERE id = :id"), 
        {'id': id}
    ).fetchone()
    
    return jsonify({
        'id': grupo.id,
        'nombre': grupo.nombre,
        'abreviatura': grupo.abreviatura,
        'descripcion': grupo.descripcion,
        'activo': grupo.activo,
        'creador': grupo.creador,
        'creacion': grupo.creacion.isoformat() if grupo.creacion else None,
        'modificador': grupo.modificador,
        'modificacion': grupo.modificacion.isoformat() if grupo.modificacion else None
    })

@mesa_grupos_bp.route('/api/mesa-grupos/<int:id>', methods=['DELETE'])
def delete_mesa_grupo(id):
    result = db.session.execute(
        db.text("DELETE FROM mesa_grupos WHERE id = :id"), 
        {'id': id}
    )
    
    if result.rowcount == 0:
        return jsonify({'error': 'Grupo no encontrado'}), 404
    
    db.session.commit()
    return jsonify({'mensaje': 'Grupo eliminado correctamente'})
