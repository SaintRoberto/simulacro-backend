from flask import request, jsonify
from usuarios import usuarios_bp
from models import db
from datetime import datetime, timezone

@usuarios_bp.route('/api/usuarios', methods=['GET'])
def get_usuarios():
    """Listar usuarios
    ---
    tags:
      - Usuarios
    responses:
      200:
        description: Lista de usuarios
        schema:
          type: array
          items:
            type: object
            properties:
              id: {type: integer}
              institucion_id: {type: integer}
              usuario: {type: string}
              descripcion: {type: string}
              celular: {type: string}
              correo: {type: string}
              activo: {type: boolean}
              aprobado: {type: boolean}
              creador: {type: string}
              creacion: {type: string}
              modificador: {type: string}
              modificacion: {type: string}
    """
    result = db.session.execute(db.text("SELECT * FROM usuarios"))
    usuarios = []
    for row in result:
        usuarios.append({
            'id': row.id,
            'institucion_id': row.institucion_id,
            'usuario': row.usuario,
            'descripcion': row.descripcion,
            'celular': row.celular,
            'correo': row.correo,
            'activo': row.activo,
            'aprobado': row.aprobado,
            'creador': row.creador,
            'creacion': row.creacion.isoformat() if row.creacion else None,
            'modificador': row.modificador,
            'modificacion': row.modificacion.isoformat() if row.modificacion else None
        })
    return jsonify(usuarios)

@usuarios_bp.route('/api/usuarios', methods=['POST'])
def create_usuario():
    """Crear usuario
    ---
    tags:
      - Usuarios
    consumes:
      - application/json
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          required: [institucion_id, usuario, clave]
          properties:
            institucion_id: {type: integer}
            usuario: {type: string}
            clave: {type: string}
            descripcion: {type: string}
            celular: {type: string}
            correo: {type: string}
            activo: {type: boolean}
            aprobado: {type: boolean}
            creador: {type: string}
    responses:
      201:
        description: Usuario creado
    """
    data = request.get_json()
    now = datetime.now(timezone.utc)
    
    query = db.text("""
        INSERT INTO usuarios (
            institucion_id, usuario, clave, descripcion, celular, correo,
            activo, aprobado, creador, creacion, modificador, modificacion
        )
        VALUES (
            :institucion_id, :usuario, :clave, :descripcion, :celular, :correo,
            :activo, :aprobado, :creador, :creacion, :modificador, :modificacion
        )
        RETURNING id
    """)
    
    result = db.session.execute(query, {
        'institucion_id': data['institucion_id'],
        'usuario': data['usuario'],
        'clave': data['clave'],
        'descripcion': data.get('descripcion', ''),
        'celular': data.get('celular'),
        'correo': data.get('correo'),
        'activo': data.get('activo', True),
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
        'descripcion': usuario.descripcion,
        'celular': usuario.celular,
        'correo': usuario.correo,
        'activo': usuario.activo,
        'aprobado': usuario.aprobado,
        'creador': usuario.creador,
        'creacion': usuario.creacion.isoformat() if usuario.creacion else None,
        'modificador': usuario.modificador,
        'modificacion': usuario.modificacion.isoformat() if usuario.modificacion else None
    }), 201

@usuarios_bp.route('/api/usuarios/<int:id>', methods=['GET'])
def get_usuario(id):
    """Obtener usuario por ID
    ---
    tags:
      - Usuarios
    parameters:
      - name: id
        in: path
        type: integer
        required: true
    responses:
      200:
        description: Usuario
      404:
        description: No encontrado
    """
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
        'descripcion': usuario.descripcion,
        'celular': usuario.celular,
        'correo': usuario.correo,
        'activo': usuario.activo,
        'aprobado': usuario.aprobado,
        'creador': usuario.creador,
        'creacion': usuario.creacion.isoformat() if usuario.creacion else None,
        'modificador': usuario.modificador,
        'modificacion': usuario.modificacion.isoformat() if usuario.modificacion else None
    })

@usuarios_bp.route('/api/usuarios/<int:id>', methods=['PUT'])
def update_usuario(id):
    """Actualizar usuario
    ---
    tags:
      - Usuarios
    consumes:
      - application/json
    parameters:
      - name: id
        in: path
        type: integer
        required: true
      - in: body
        name: body
        required: true
        schema:
          type: object
          properties:
            institucion_id: {type: integer}
            usuario: {type: string}
            clave: {type: string}
            descripcion: {type: string}
            celular: {type: string}
            correo: {type: string}
            activo: {type: boolean}
            aprobado: {type: boolean}
            modificador: {type: string}
    responses:
      200:
        description: Usuario actualizado
      404:
        description: No encontrado
    """
    data = request.get_json()
    now = datetime.now(timezone.utc)
    
    update_fields = []
    params = {'id': id, 'modificador': data.get('modificador', 'Sistema'), 'modificacion': now}
    
    for field in ['institucion_id','usuario','clave','descripcion','celular','correo','activo','aprobado']:
        if field in data:
            update_fields.append(f"{field} = :{field}")
            params[field] = data[field]
    
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
        'descripcion': usuario.descripcion,
        'celular': usuario.celular,
        'correo': usuario.correo,
        'activo': usuario.activo,
        'aprobado': usuario.aprobado,
        'creador': usuario.creador,
        'creacion': usuario.creacion.isoformat() if usuario.creacion else None,
        'modificador': usuario.modificador,
        'modificacion': usuario.modificacion.isoformat() if usuario.modificacion else None
    })

@usuarios_bp.route('/api/usuarios/<int:id>', methods=['DELETE'])
def delete_usuario(id):
    """Eliminar usuario
    ---
    tags:
      - Usuarios
    parameters:
      - name: id
        in: path
        type: integer
        required: true
    responses:
      200:
        description: Eliminado
      404:
        description: No encontrado
    """
    result = db.session.execute(
        db.text("DELETE FROM usuarios WHERE id = :id"), 
        {'id': id}
    )
    
    if result.rowcount == 0:
        return jsonify({'error': 'Usuario no encontrado'}), 404
    
    db.session.commit()
    return jsonify({'mensaje': 'Usuario eliminado correctamente'})
