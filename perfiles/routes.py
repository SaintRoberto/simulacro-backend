from flask import request, jsonify
from perfiles import perfiles_bp
from models import db
from datetime import datetime, timezone

@perfiles_bp.route('/api/perfiles', methods=['GET'])
def get_perfiles():
    result = db.session.execute(db.text("SELECT * FROM perfiles"))
    perfiles = []
    for row in result:
        perfiles.append({
            'id': row.id,
            'nombre': row.nombre,
            'descripcion': row.descripcion,
            'estado': row.estado,
            'creador': row.creador,
            'creacion': row.creacion.isoformat() if row.creacion else None,
            'modificador': row.modificador,
            'modificacion': row.modificacion.isoformat() if row.modificacion else None
        })
    return jsonify(perfiles)

@perfiles_bp.route('/api/perfiles', methods=['POST'])
def create_perfil():
    data = request.get_json()
    now = datetime.now(timezone.utc)
    
    query = db.text("""
        INSERT INTO perfiles (nombre, descripcion, estado, creador, creacion, modificador, modificacion)
        VALUES (:nombre, :descripcion, :estado, :creador, :creacion, :modificador, :modificacion)
        RETURNING id
    """)
    
    result = db.session.execute(query, {
        'nombre': data['nombre'],
        'descripcion': data.get('descripcion', ''),
        'estado': data.get('estado', 'Activo'),
        'creador': data.get('creador', 'Sistema'),
        'creacion': now,
        'modificador': data.get('creador', 'Sistema'),
        'modificacion': now
    })
    
    perfil_id = result.fetchone()[0]
    db.session.commit()
    
    perfil = db.session.execute(
        db.text("SELECT * FROM perfiles WHERE id = :id"), 
        {'id': perfil_id}
    ).fetchone()
    
    return jsonify({
        'id': perfil.id,
        'nombre': perfil.nombre,
        'descripcion': perfil.descripcion,
        'estado': perfil.estado,
        'creador': perfil.creador,
        'creacion': perfil.creacion.isoformat() if perfil.creacion else None,
        'modificador': perfil.modificador,
        'modificacion': perfil.modificacion.isoformat() if perfil.modificacion else None
    }), 201

@perfiles_bp.route('/api/perfiles/<int:id>', methods=['GET'])
def get_perfil(id):
    result = db.session.execute(
        db.text("SELECT * FROM perfiles WHERE id = :id"), 
        {'id': id}
    )
    perfil = result.fetchone()
    
    if not perfil:
        return jsonify({'error': 'Perfil no encontrado'}), 404
    
    return jsonify({
        'id': perfil.id,
        'nombre': perfil.nombre,
        'descripcion': perfil.descripcion,
        'estado': perfil.estado,
        'creador': perfil.creador,
        'creacion': perfil.creacion.isoformat() if perfil.creacion else None,
        'modificador': perfil.modificador,
        'modificacion': perfil.modificacion.isoformat() if perfil.modificacion else None
    })

@perfiles_bp.route('/api/perfiles/<int:id>', methods=['PUT'])
def update_perfil(id):
    data = request.get_json()
    now = datetime.now(timezone.utc)
    
    query = db.text("""
        UPDATE perfiles 
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
        return jsonify({'error': 'Perfil no encontrado'}), 404
    
    db.session.commit()
    
    perfil = db.session.execute(
        db.text("SELECT * FROM perfiles WHERE id = :id"), 
        {'id': id}
    ).fetchone()
    
    return jsonify({
        'id': perfil.id,
        'nombre': perfil.nombre,
        'descripcion': perfil.descripcion,
        'estado': perfil.estado,
        'creador': perfil.creador,
        'creacion': perfil.creacion.isoformat() if perfil.creacion else None,
        'modificador': perfil.modificador,
        'modificacion': perfil.modificacion.isoformat() if perfil.modificacion else None
    })

@perfiles_bp.route('/api/perfiles/<int:id>', methods=['DELETE'])
def delete_perfil(id):
    result = db.session.execute(
        db.text("DELETE FROM perfiles WHERE id = :id"), 
        {'id': id}
    )
    
    if result.rowcount == 0:
        return jsonify({'error': 'Perfil no encontrado'}), 404
    
    db.session.commit()
    return jsonify({'mensaje': 'Perfil eliminado correctamente'})
