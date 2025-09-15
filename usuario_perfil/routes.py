from flask import request, jsonify
from usuario_perfil import usuario_perfil_bp
from models import db
from datetime import datetime, timezone

@usuario_perfil_bp.route('/api/usuario-perfil', methods=['GET'])
def get_usuario_perfil():
    result = db.session.execute(db.text("SELECT * FROM usuario_perfil"))
    relaciones = []
    for row in result:
        relaciones.append({
            'id': row.id,
            'usuario_id': row.usuario_id,
            'perfil_id': row.perfil_id,
            'activo': row.activo,
            'creador': row.creador,
            'creacion': row.creacion.isoformat() if row.creacion else None,
            'modificador': row.modificador,
            'modificacion': row.modificacion.isoformat() if row.modificacion else None
        })
    return jsonify(relaciones)

@usuario_perfil_bp.route('/api/usuario-perfil', methods=['POST'])
def create_usuario_perfil():
    data = request.get_json()
    now = datetime.now(timezone.utc)
    
    query = db.text("""
        INSERT INTO usuario_perfil (usuario_id, perfil_id, activo, creador, creacion, modificador, modificacion)
        VALUES (:usuario_id, :perfil_id, :activo, :creador, :creacion, :modificador, :modificacion)
        RETURNING id
    """)
    
    result = db.session.execute(query, {
        'usuario_id': data['usuario_id'],
        'perfil_id': data['perfil_id'],
        'activo': data.get('activo', True),
        'creador': data.get('creador', 'Sistema'),
        'creacion': now,
        'modificador': data.get('creador', 'Sistema'),
        'modificacion': now
    })
    
    relacion_id = result.fetchone()[0]
    db.session.commit()
    
    relacion = db.session.execute(
        db.text("SELECT * FROM usuario_perfil WHERE id = :id"), 
        {'id': relacion_id}
    ).fetchone()
    
    return jsonify({
        'id': relacion.id,
        'usuario_id': relacion.usuario_id,
        'perfil_id': relacion.perfil_id,
        'activo': relacion.activo,
        'creador': relacion.creador,
        'creacion': relacion.creacion.isoformat() if relacion.creacion else None,
        'modificador': relacion.modificador,
        'modificacion': relacion.modificacion.isoformat() if relacion.modificacion else None
    }), 201

@usuario_perfil_bp.route('/api/usuario-perfil/<int:id>', methods=['GET'])
def get_usuario_perfil_by_id(id):
    result = db.session.execute(
        db.text("SELECT * FROM usuario_perfil WHERE id = :id"), 
        {'id': id}
    )
    relacion = result.fetchone()
    
    if not relacion:
        return jsonify({'error': 'Relación no encontrada'}), 404
    
    return jsonify({
        'id': relacion.id,
        'usuario_id': relacion.usuario_id,
        'perfil_id': relacion.perfil_id,
        'activo': relacion.activo,
        'creador': relacion.creador,
        'creacion': relacion.creacion.isoformat() if relacion.creacion else None,
        'modificador': relacion.modificador,
        'modificacion': relacion.modificacion.isoformat() if relacion.modificacion else None
    })

@usuario_perfil_bp.route('/api/usuario-perfil/<int:id>', methods=['PUT'])
def update_usuario_perfil(id):
    data = request.get_json()
    now = datetime.now(timezone.utc)
    
    query = db.text("""
        UPDATE usuario_perfil 
        SET usuario_id = :usuario_id, 
            perfil_id = :perfil_id, 
            activo = :activo, 
            modificador = :modificador, 
            modificacion = :modificacion
        WHERE id = :id
    """)
    
    result = db.session.execute(query, {
        'id': id,
        'usuario_id': data.get('usuario_id'),
        'perfil_id': data.get('perfil_id'),
        'activo': data.get('activo'),
        'modificador': data.get('modificador', 'Sistema'),
        'modificacion': now
    })
    
    if result.rowcount == 0:
        return jsonify({'error': 'Relación no encontrada'}), 404
    
    db.session.commit()
    
    relacion = db.session.execute(
        db.text("SELECT * FROM usuario_perfil WHERE id = :id"), 
        {'id': id}
    ).fetchone()
    
    return jsonify({
        'id': relacion.id,
        'usuario_id': relacion.usuario_id,
        'perfil_id': relacion.perfil_id,
        'activo': relacion.activo,
        'creador': relacion.creador,
        'creacion': relacion.creacion.isoformat() if relacion.creacion else None,
        'modificador': relacion.modificador,
        'modificacion': relacion.modificacion.isoformat() if relacion.modificacion else None
    })

@usuario_perfil_bp.route('/api/usuario-perfil/<int:id>', methods=['DELETE'])
def delete_usuario_perfil(id):
    result = db.session.execute(
        db.text("DELETE FROM usuario_perfil WHERE id = :id"), 
        {'id': id}
    )
    
    if result.rowcount == 0:
        return jsonify({'error': 'Relación no encontrada'}), 404
    
    db.session.commit()
    return jsonify({'mensaje': 'Relación eliminada correctamente'})
