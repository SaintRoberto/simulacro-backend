from flask import request, jsonify
from perfiles import perfiles_bp
from models import db
from datetime import datetime, timezone

from utils.db_helpers import check_row_or_abort
@perfiles_bp.route('/api/perfiles', methods=['GET'])
def get_perfiles():
    result = db.session.execute(db.text("SELECT * FROM perfiles"))
    perfiles = []
    for row in result:
        perfiles.append({
            'id': row.id,
            'nombre': row.nombre,
            'descripcion': row.descripcion,
            'activo': row.activo,
            'creador': row.creador,
            'creacion': row.creacion.isoformat() if row.creacion else None,
            'modificador': row.modificador,
            'modificacion': row.modificacion.isoformat() if row.modificacion else None
        })
    return jsonify(perfiles)

@perfiles_bp.route('/api/perfiles', methods=['POST'])
def create_perfil():
    data = request.get_json() or {}
    nombre = data.get('nombre')
    if not nombre:
        return jsonify({'error': 'El campo "nombre" es obligatorio'}), 400

    now = datetime.now(timezone.utc)
    
    query = db.text("""
        INSERT INTO perfiles (nombre, descripcion, activo, creador, creacion, modificador, modificacion)
        VALUES (:nombre, :descripcion, :activo, :creador, :creacion, :modificador, :modificacion)
        RETURNING id
    """)
    
    result = db.session.execute(query, {
        'nombre': nombre,
        'descripcion': data.get('descripcion', ''),
        'activo': data.get('activo', True),
        'creador': data.get('creador', 'Sistema'),
        'creacion': now,
        'modificador': data.get('modificador', data.get('creador', 'Sistema')),
        'modificacion': now
    })
    
    row = result.fetchone()
    if row is None:
        # insertion should normally return an id; if not, treat as server error
        return jsonify({'error': 'No se pudo crear el perfil'}), 500
    perfil_id = row[0]
    db.session.commit()
    
    perfil = db.session.execute(
        db.text("SELECT * FROM perfiles WHERE id = :id"),
        {'id': perfil_id}
    ).fetchone()
    
    if not perfil:
        # defensive check in case the record is not found after commit
        return jsonify({'error': 'Perfil no encontrado después de crear'}), 500
    
    return jsonify({
        'id': perfil.id,
        'nombre': perfil.nombre,
        'descripcion': perfil.descripcion,
        'activo': perfil.activo,
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
        'activo': perfil.activo,
        'creador': perfil.creador,
        'creacion': perfil.creacion.isoformat() if perfil.creacion else None,
        'modificador': perfil.modificador,
        'modificacion': perfil.modificacion.isoformat() if perfil.modificacion else None
    })

@perfiles_bp.route('/api/perfiles/<int:id>', methods=['PUT'])
def update_perfil(id):
    data = request.get_json() or {}
    now = datetime.now(timezone.utc)
    
    query = db.text("""
        UPDATE perfiles
        SET nombre = :nombre,
            descripcion = :descripcion,
            activo = :activo,
            modificador = :modificador,
            modificacion = :modificacion
        WHERE id = :id
    """)
    
    result = db.session.execute(query, {
        'id': id,
        'nombre': data.get('nombre'),
        'descripcion': data.get('descripcion'),
        'activo': data.get('activo'),
        'modificador': data.get('modificador', 'Sistema'),
        'modificacion': now
    })
    
    if getattr(result, 'rowcount', 0) == 0:
        return jsonify({'error': 'Perfil no encontrado'}), 404
    
    db.session.commit()
    
    perfil = db.session.execute(
        db.text("SELECT * FROM perfiles WHERE id = :id"),
        {'id': id}
    ).fetchone()
    
    if not perfil:
        # defensive check even though rowcount > 0, ensure we don't access attributes of None
        return jsonify({'error': 'Perfil no encontrado después de actualizar'}), 500
    
    return jsonify({
        'id': perfil.id,
        'nombre': perfil.nombre,
        'descripcion': perfil.descripcion,
        'activo': perfil.activo,
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
    
    if getattr(result, 'rowcount', 0) == 0:
        return jsonify({'error': 'Perfil no encontrado'}), 404
    
    db.session.commit()
    return jsonify({'mensaje': 'Perfil eliminado correctamente'})
