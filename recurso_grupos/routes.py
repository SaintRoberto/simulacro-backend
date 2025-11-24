from flask import request, jsonify
from recurso_grupos import recurso_grupos_bp
from models import db
from datetime import datetime, timezone

from utils.db_helpers import check_row_or_abort
@recurso_grupos_bp.route('/api/recurso_grupos', methods=['GET'])
def get_recurso_grupos():
    """Listar grupos de recursos
    ---
    tags:
      - Recurso Grupos
    responses:
      200:
        description: Lista de grupos de recursos
        schema:
          type: array
          items:
            type: object
            properties:
              id: {type: integer}
              nombre: {type: string}
              descripcion: {type: string}
              activo: {type: boolean}
              creador: {type: string}
              creacion: {type: string}
              modificador: {type: string}
              modificacion: {type: string}
    """
    result = db.session.execute(db.text("SELECT * FROM recurso_grupos"))
    grupos = []
    for row in result:
        grupos.append({
            'id': row.id,
            'nombre': row.nombre,
            'descripcion': row.descripcion,
            'activo': row.activo,
            'creador': row.creador,
            'creacion': row.creacion.isoformat() if row.creacion else None,
            'modificador': row.modificador,
            'modificacion': row.modificacion.isoformat() if row.modificacion else None
        })
    return jsonify(grupos)


@recurso_grupos_bp.route('/api/recurso_grupos/categoria/<int:recurso_categoria_id>', methods=['GET'])
def get_recurso_grupos_by_categoria(recurso_categoria_id):
    """Listar grupos de recursos por categoría
    ---
    tags:
      - Recurso Grupos
    parameters:
      - name: recurso_categoria_id
        in: path
        type: integer
        required: true
    responses:
      200:
        description: Lista de grupos de recursos filtrados por categoría
        schema:
          type: array
          items:
            type: object
            properties:
              id: {type: integer}
              nombre: {type: string}
              descripcion: {type: string}
              activo: {type: boolean}
              creador: {type: string}
              creacion: {type: string}
              modificador: {type: string}
              modificacion: {type: string}
    """
    query = db.text("""
        SELECT *
        FROM recurso_grupos
        WHERE recurso_categoria_id = :recurso_categoria_id
    """)

    result = db.session.execute(query, {'recurso_categoria_id': recurso_categoria_id})
    grupos = []
    for row in result:
        grupos.append({
            'id': row.id,
            'nombre': row.nombre,
            'descripcion': row.descripcion,
            'activo': row.activo,
            'creador': row.creador,
            'creacion': row.creacion.isoformat() if row.creacion else None,
            'modificador': row.modificador,
            'modificacion': row.modificacion.isoformat() if row.modificacion else None
        })

    return jsonify(grupos)

@recurso_grupos_bp.route('/api/recurso_grupos', methods=['POST'])
def create_recurso_grupo():
    """Crear grupo de recurso
    ---
    tags:
      - Recurso Grupos
    consumes:
      - application/json
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          required: [nombre]
          properties:
            nombre: {type: string}
            descripcion: {type: string}
            activo: {type: boolean}
            creador: {type: string}
    responses:
      201:
        description: Grupo de recurso creado
    """
    data = request.get_json()
    now = datetime.now(timezone.utc)
    
    query = db.text("""
        INSERT INTO recurso_grupos (nombre, descripcion, activo, creador, creacion, modificador, modificacion)
        VALUES (:nombre, :descripcion, :activo, :creador, :creacion, :modificador, :modificacion)
        RETURNING id
    """)
    
    result = db.session.execute(query, {
        'nombre': data['nombre'],
        'descripcion': data.get('descripcion'),
        'activo': data.get('activo', True),
        'creador': data.get('creador', 'Sistema'),
        'creacion': now,
        'modificador': data.get('creador', 'Sistema'),
        'modificacion': now
    })
    
    row = result.fetchone()
    if row is None:
        return jsonify({'error': 'Not found'}), 404
    grupo_id = row[0]
    db.session.commit()
    
    grupo = db.session.execute(
        db.text("SELECT * FROM recurso_grupos WHERE id = :id"), 
        {'id': grupo_id}
    ).fetchone()
    
    return jsonify({
        'id': grupo.id,
        'nombre': grupo.nombre,
        'descripcion': grupo.descripcion,
        'activo': grupo.activo,
        'creador': grupo.creador,
        'creacion': grupo.creacion.isoformat() if grupo.creacion else None,
        'modificador': grupo.modificador,
        'modificacion': grupo.modificacion.isoformat() if grupo.modificacion else None
    }), 201

@recurso_grupos_bp.route('/api/recurso_grupos/<int:id>', methods=['GET'])
def get_recurso_grupo(id):
    """Obtener grupo de recurso por ID
    ---
    tags:
      - Recurso Grupos
    parameters:
      - name: id
        in: path
        type: integer
        required: true
    responses:
      200:
        description: Grupo de recurso
      404:
        description: No encontrado
    """
    result = db.session.execute(
        db.text("SELECT * FROM recurso_grupos WHERE id = :id"), 
        {'id': id}
    )
    grupo = result.fetchone()
    
    if not grupo:
        return jsonify({'error': 'Grupo no encontrado'}), 404
    
    return jsonify({
        'id': grupo.id,
        'nombre': grupo.nombre,
        'descripcion': grupo.descripcion,
        'activo': grupo.activo,
        'creador': grupo.creador,
        'creacion': grupo.creacion.isoformat() if grupo.creacion else None,
        'modificador': grupo.modificador,
        'modificacion': grupo.modificacion.isoformat() if grupo.modificacion else None
    })

@recurso_grupos_bp.route('/api/recurso_grupos/<int:id>', methods=['PUT'])
def update_recurso_grupo(id):
    """Actualizar grupo de recurso
    ---
    tags:
      - Recurso Grupos
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
            nombre: {type: string}
            descripcion: {type: string}
            activo: {type: boolean}
            modificador: {type: string}
    responses:
      200:
        description: Grupo de recurso actualizado
      404:
        description: No encontrado
    """
    data = request.get_json()
    now = datetime.now(timezone.utc)
    
    query = db.text("""
        UPDATE recurso_grupos 
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
        return jsonify({'error': 'Grupo no encontrado'}), 404
    
    db.session.commit()
    
    grupo = db.session.execute(
        db.text("SELECT * FROM recurso_grupos WHERE id = :id"), 
        {'id': id}
    ).fetchone()
    
    return jsonify({
        'id': grupo.id,
        'nombre': grupo.nombre,
        'descripcion': grupo.descripcion,
        'activo': grupo.activo,
        'creador': grupo.creador,
        'creacion': grupo.creacion.isoformat() if grupo.creacion else None,
        'modificador': grupo.modificador,
        'modificacion': grupo.modificacion.isoformat() if grupo.modificacion else None
    })

@recurso_grupos_bp.route('/api/recurso_grupos/<int:id>', methods=['DELETE'])
def delete_recurso_grupo(id):
    """Eliminar grupo de recurso
    ---
    tags:
      - Recurso Grupos
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
        db.text("DELETE FROM recurso_grupos WHERE id = :id"), 
        {'id': id}
    )
    
    if getattr(result, 'rowcount', 0) == 0:
        return jsonify({'error': 'Grupo no encontrado'}), 404
    
    db.session.commit()
    return jsonify({'mensaje': 'Grupo eliminado correctamente'})
