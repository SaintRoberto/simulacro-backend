from flask import request, jsonify
from usuarios import usuarios_bp
from models import db
from datetime import datetime, timezone
from schemas import UsuarioCreateSchema, UsuarioUpdateSchema, LoginSchema, UsuarioResponseSchema
from marshmallow import ValidationError
from auth import hash_password, verify_password, generate_token
from typing import cast, Dict, Any

from utils.db_helpers import check_row_or_abort
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
    response_schema = UsuarioResponseSchema()
    for row in result:
        # Use schema for safe output encoding
        safe_data = cast(Dict[str, Any], response_schema.dump({
            'id': row.id,
            'institucion_id': row.institucion_id,
            'usuario': row.usuario,
            'correo': row.correo,
            'celular': row.celular,
            'activo': row.activo,
            'aprobado': row.aprobado,
            'creador': row.creador,
            'creacion': row.creacion,
            'modificador': row.modificador,
            'modificacion': row.modificacion
        }))
        usuarios.append(safe_data)
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

    # Validate input
    schema = UsuarioCreateSchema()
    try:
        validated_data = cast(Dict[str, Any], schema.load(data))
    except ValidationError as err:
        return jsonify({'error': 'Validation failed', 'details': err.messages}), 400

    # Hash the password before storing
    hashed = hash_password(validated_data['clave'])
    
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
        'institucion_id': validated_data['institucion_id'],
        'usuario': validated_data['usuario'],
        'clave': hashed,
        'descripcion': validated_data.get('descripcion', ''),
        'celular': validated_data.get('celular'),
        'correo': validated_data.get('correo'),
        'activo': validated_data.get('activo', True),
        'aprobado': validated_data.get('aprobado', False),
        'creador': validated_data.get('creador', 'Sistema'),
        'creacion': now,
        'modificador': validated_data.get('creador', 'Sistema'),
        'modificacion': now
    })
    
    row = result.fetchone()
    if row is None:
        return jsonify({'error': 'Failed to create usuario'}), 500
    usuario_id = row[0]
    db.session.commit()
    
    usuario = db.session.execute(
        db.text("SELECT * FROM usuarios WHERE id = :id"),
        {'id': usuario_id}
    ).fetchone()
    assert usuario is not None
    
    # Use schema for safe output encoding
    response_schema = UsuarioResponseSchema()
    safe_data = cast(Dict[str, Any], response_schema.dump({
        'id': usuario.id,
        'institucion_id': usuario.institucion_id,
        'usuario': usuario.usuario,
        'correo': usuario.correo,
        'celular': usuario.celular,
        'activo': usuario.activo,
        'aprobado': usuario.aprobado,
        'creador': usuario.creador,
        'creacion': usuario.creacion,
        'modificador': usuario.modificador,
        'modificacion': usuario.modificacion
    }))
    return jsonify(safe_data), 201

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

    # Use schema for safe output encoding
    response_schema = UsuarioResponseSchema()
    safe_data = cast(Dict[str, Any], response_schema.dump({
        'id': usuario.id,
        'institucion_id': usuario.institucion_id,
        'usuario': usuario.usuario,
        'correo': usuario.correo,
        'celular': usuario.celular,
        'activo': usuario.activo,
        'aprobado': usuario.aprobado,
        'creador': usuario.creador,
        'creacion': usuario.creacion,
        'modificador': usuario.modificador,
        'modificacion': usuario.modificacion
    }))
    return jsonify(safe_data)

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

    # Validate input
    schema = UsuarioUpdateSchema()
    try:
        validated_data = cast(Dict[str, Any], schema.load(data))
    except ValidationError as err:
        return jsonify({'error': 'Validation failed', 'details': err.messages}), 400

    update_fields = []
    params = {'id': id, 'modificador': validated_data.get('modificador', 'Sistema'), 'modificacion': now}
    
    for field in ['institucion_id','usuario','clave','descripcion','celular','correo','activo','aprobado']:
        if field in validated_data and validated_data[field] is not None:
            if field == 'clave':
                # Hash the password if it's being updated
                params[field] = hash_password(validated_data[field])
            else:
                params[field] = validated_data[field]
            update_fields.append(f"{field} = :{field}")
    
    update_fields.append('modificador = :modificador')
    update_fields.append('modificacion = :modificacion')
    
    query = db.text(f"""
        UPDATE usuarios 
        SET {', '.join(update_fields)}
        WHERE id = :id
    """)
    
    result = db.session.execute(query, params)

    rowcount = getattr(result, 'rowcount', 0)
    if rowcount == 0:
        return jsonify({'error': 'Usuario no encontrado'}), 404
    
    db.session.commit()
    
    usuario = db.session.execute(
        db.text("SELECT * FROM usuarios WHERE id = :id"),
        {'id': id}
    ).fetchone()
    assert usuario is not None
    
    # Use schema for safe output encoding
    response_schema = UsuarioResponseSchema()
    safe_data = cast(Dict[str, Any], response_schema.dump({
        'id': usuario.id,
        'institucion_id': usuario.institucion_id,
        'usuario': usuario.usuario,
        'correo': usuario.correo,
        'celular': usuario.celular,
        'activo': usuario.activo,
        'aprobado': usuario.aprobado,
        'creador': usuario.creador,
        'creacion': usuario.creacion,
        'modificador': usuario.modificador,
        'modificacion': usuario.modificacion
    }))
    return jsonify(safe_data)

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

    rowcount = getattr(result, 'rowcount', 0)
    if rowcount == 0:
        return jsonify({'error': 'Usuario no encontrado'}), 404
    
    db.session.commit()
    return jsonify({'mensaje': 'Usuario eliminado correctamente'})

@usuarios_bp.route('/api/usuarios/<int:usuario_id>/datos-login', methods=['GET'])
def get_datos_login(usuario_id):
    """Obtener datos de login por usuario ID
    ---
    tags:
      - Usuarios
    parameters:
      - name: usuario_id
        in: path
        type: integer
        required: true
    responses:
      200:
        description: Datos de login
      404:
        description: No encontrado
    """
    query = db.text("""
      SELECT u.usuario usuario_login
      , u.id usuario_id
      , u.descripcion usuario_descripcion
      , ux.coe_id
      , c.siglas coe_abreviatura
      , ux.perfil_id
      , pf.nombre perfil_nombre
      , ux.provincia_id
      , COALESCE(p.nombre,'--') provincia_nombre
      , ux.canton_id
      , COALESCE(k.nombre,'--') canton_nombre
      , ux.mesa_id
      , m.nombre mesa_nombre
      , m.siglas mesa_siglas
      , g.id mesa_grupo_id
      , g.nombre mesa_grupo_nombre
      FROM public.usuarios u 
      INNER JOIN public.usuario_perfil_coe_dpa_mesa ux ON u.id = ux.usuario_id
      INNER JOIN public.perfiles pf ON ux.perfil_id = pf.id
      INNER JOIN public.coes c ON ux.coe_id = c.id
      LEFT JOIN public.provincias p ON ux.provincia_id = p.id
      LEFT JOIN public.cantones k ON ux.provincia_id = k.provincia_id AND ux.canton_id = k.id
      INNER JOIN public.mesas m ON ux.mesa_id = m.id
      LEFT JOIN public.mesa_grupos g ON m.mesa_grupo_id = g.id
      WHERE u.id = :usuario_id
    """)
    result = db.session.execute(query, {'usuario_id': usuario_id})
    row = result.fetchone()
    if not row:
        return jsonify({'error': 'Datos de login no encontrados'}), 404
    return jsonify({
        'usuario_login': row.usuario_login,
        'usuario_id': row.usuario_id,
        'usuario_descripcion': row.usuario_descripcion, 
        'coe_id': row.coe_id,
        'coe_abreviatura': row.coe_abreviatura,
        'perfil_id': row.perfil_id,
        'perfil_nombre': row.perfil_nombre,
        'provincia_id': row.provincia_id,
        'provincia_nombre': row.provincia_nombre,
        'canton_id': row.canton_id,
        'canton_nombre': row.canton_nombre,
        'mesa_id': row.mesa_id,
        'mesa_nombre': row.mesa_nombre,
        'mesa_siglas': row.mesa_siglas,
        'mesa_grupo_id': row.mesa_grupo_id,
        'mesa_grupo_nombre': row.mesa_grupo_nombre
    })

# Las opciones CORS preflight son manejadas por la configuración global de CORS

@usuarios_bp.route('/api/usuarios/login', methods=['POST'])
def login_usuario():
   
    data = request.get_json()
    if not data:
        return jsonify({'error': 'Datos requeridos'}), 400

    # Validate input
    schema = LoginSchema()
    try:
        validated_data = cast(Dict[str, Any], schema.load(data))
    except ValidationError as err:
        return jsonify({'error': 'Validation failed', 'details': err.messages}), 400
    
    # Validar credenciales en tabla usuarios (compare hashed password)
    query_usuario = db.text("""
        SELECT id, usuario, descripcion, clave
        FROM usuarios
        WHERE usuario = :usuario AND activo = true
    """)
    result_usuario = db.session.execute(query_usuario, {
        'usuario': validated_data['usuario']
    })
    usuario_row = result_usuario.fetchone()
    check_row_or_abort(usuario_row, 'Not found', 404)
    
    if usuario_row and verify_password(validated_data['clave'], usuario_row.clave):
        # Build token payload; include roles later (example: fetch perfiles)
        payload = {
            'user_id': usuario_row.id,
            'usuario': usuario_row.usuario,
            # 'roles': ['user'],  # optionally fetch real roles from DB
        }
        token = generate_token(payload)
        # Use schema for safe output encoding
        response_schema = UsuarioResponseSchema()
        safe_data = cast(Dict[str, Any], response_schema.dump({
            'id': usuario_row.id,
            'usuario': usuario_row.usuario,
            'descripcion': usuario_row.descripcion
        }))
        return jsonify({
            'success': True,
            'token': token,
            **safe_data
        }), 200
    else:
        return jsonify({'success': False}), 200
