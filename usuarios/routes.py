from flask import request, jsonify
from usuarios import usuarios_bp
from models import db
from datetime import datetime, timezone

@usuarios_bp.route('/api/usuarios', methods=['GET'])
def get_usuarios():
    result = db.session.execute(db.text("SELECT * FROM usuarios"))
    usuarios = []
    for row in result:
        usuarios.append({
            'id': row.id,
            'institucion_id': row.institucion_id,
            'usuario': row.usuario,
            'correo': row.correo,
            'nombres': row.nombres,
            'apellidos': row.apellidos,
            'cedula': row.cedula,
            'celular': row.celular,
            'estado': row.estado,
            'aprobado': row.aprobado,
            'creador': row.creador,
            'creacion': row.creacion.isoformat() if row.creacion else None,
            'modificador': row.modificador,
            'modificacion': row.modificacion.isoformat() if row.modificacion else None
        })
    return jsonify(usuarios)

@usuarios_bp.route('/api/usuarios', methods=['POST'])
def create_usuario():
    data = request.get_json()
    now = datetime.now(timezone.utc)
    
    query = db.text("""
        INSERT INTO usuarios (institucion_id, usuario, contrasena, correo, nombres, apellidos, cedula, celular, estado, aprobado, creador, creacion, modificador, modificacion)
        VALUES (:institucion_id, :usuario, :contrasena, :correo, :nombres, :apellidos, :cedula, :celular, :estado, :aprobado, :creador, :creacion, :modificador, :modificacion)
        RETURNING id
    """)
    
    result = db.session.execute(query, {
        'institucion_id': data['institucion_id'],
        'usuario': data['usuario'],
        'contrasena': data['contrasena'],
        'correo': data['correo'],
        'nombres': data['nombres'],
        'apellidos': data['apellidos'],
        'cedula': data['cedula'],
        'celular': data.get('celular', ''),
        'estado': data.get('estado', 'Activo'),
        'aprobado': data.get('aprobado', False),
        'creador': data.get('creador', 'Sistema'),
        'creacion': now,
        'modificador': data.get('creador', 'Sistema'),
        'modificacion': now
    })
    
    usuario_id = result.fetchone()[0]
    db.session.commit()
    
    usuario = db.session.execute(
        db.text("SELECT * FROM usuarios WHERE id = :id"), 
        {'id': usuario_id}
    ).fetchone()
    
    return jsonify({
        'id': usuario.id,
        'institucion_id': usuario.institucion_id,
        'usuario': usuario.usuario,
        'correo': usuario.correo,
        'nombres': usuario.nombres,
        'apellidos': usuario.apellidos,
        'cedula': usuario.cedula,
        'celular': usuario.celular,
        'estado': usuario.estado,
        'aprobado': usuario.aprobado,
        'creador': usuario.creador,
        'creacion': usuario.creacion.isoformat() if usuario.creacion else None,
        'modificador': usuario.modificador,
        'modificacion': usuario.modificacion.isoformat() if usuario.modificacion else None
    }), 201

@usuarios_bp.route('/api/usuarios/<int:id>', methods=['GET'])
def get_usuario(id):
    result = db.session.execute(
        db.text("SELECT * FROM usuarios WHERE id = :id"), 
        {'id': id}
    )
    usuario = result.fetchone()
    
    if not usuario:
        return jsonify({'error': 'Usuario no encontrado'}), 404
    
    return jsonify({
        'id': usuario.id,
        'institucion_id': usuario.institucion_id,
        'usuario': usuario.usuario,
        'correo': usuario.correo,
        'nombres': usuario.nombres,
        'apellidos': usuario.apellidos,
        'cedula': usuario.cedula,
        'celular': usuario.celular,
        'estado': usuario.estado,
        'aprobado': usuario.aprobado,
        'creador': usuario.creador,
        'creacion': usuario.creacion.isoformat() if usuario.creacion else None,
        'modificador': usuario.modificador,
        'modificacion': usuario.modificacion.isoformat() if usuario.modificacion else None
    })

@usuarios_bp.route('/api/usuarios/<int:id>', methods=['PUT'])
def update_usuario(id):
    data = request.get_json()
    now = datetime.now(timezone.utc)
    
    # Construir query dinámicamente
    update_fields = []
    params = {'id': id, 'modificador': data.get('modificador', 'Sistema'), 'modificacion': now}
    
    if 'institucion_id' in data:
        update_fields.append('institucion_id = :institucion_id')
        params['institucion_id'] = data['institucion_id']
    if 'usuario' in data:
        update_fields.append('usuario = :usuario')
        params['usuario'] = data['usuario']
    if 'correo' in data:
        update_fields.append('correo = :correo')
        params['correo'] = data['correo']
    if 'nombres' in data:
        update_fields.append('nombres = :nombres')
        params['nombres'] = data['nombres']
    if 'apellidos' in data:
        update_fields.append('apellidos = :apellidos')
        params['apellidos'] = data['apellidos']
    if 'cedula' in data:
        update_fields.append('cedula = :cedula')
        params['cedula'] = data['cedula']
    if 'celular' in data:
        update_fields.append('celular = :celular')
        params['celular'] = data['celular']
    if 'estado' in data:
        update_fields.append('estado = :estado')
        params['estado'] = data['estado']
    if 'aprobado' in data:
        update_fields.append('aprobado = :aprobado')
        params['aprobado'] = data['aprobado']
    if 'contrasena' in data:
        update_fields.append('contrasena = :contrasena')
        params['contrasena'] = data['contrasena']
    
    update_fields.append('modificador = :modificador')
    update_fields.append('modificacion = :modificacion')
    
    query = db.text(f"""
        UPDATE usuarios 
        SET {', '.join(update_fields)}
        WHERE id = :id
    """)
    
    result = db.session.execute(query, params)
    
    if result.rowcount == 0:
        return jsonify({'error': 'Usuario no encontrado'}), 404
    
    db.session.commit()
    
    usuario = db.session.execute(
        db.text("SELECT * FROM usuarios WHERE id = :id"), 
        {'id': id}
    ).fetchone()
    
    return jsonify({
        'id': usuario.id,
        'institucion_id': usuario.institucion_id,
        'usuario': usuario.usuario,
        'correo': usuario.correo,
        'nombres': usuario.nombres,
        'apellidos': usuario.apellidos,
        'cedula': usuario.cedula,
        'celular': usuario.celular,
        'estado': usuario.estado,
        'aprobado': usuario.aprobado,
        'creador': usuario.creador,
        'creacion': usuario.creacion.isoformat() if usuario.creacion else None,
        'modificador': usuario.modificador,
        'modificacion': usuario.modificacion.isoformat() if usuario.modificacion else None
    })

@usuarios_bp.route('/api/usuarios/<int:id>', methods=['DELETE'])
def delete_usuario(id):
    result = db.session.execute(
        db.text("DELETE FROM usuarios WHERE id = :id"), 
        {'id': id}
    )
    
    if result.rowcount == 0:
        return jsonify({'error': 'Usuario no encontrado'}), 404
    
    db.session.commit()
    return jsonify({'mensaje': 'Usuario eliminado correctamente'})
