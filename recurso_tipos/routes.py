from flask import request, jsonify
from flask_sqlalchemy import query
from recurso_tipos import recurso_tipos_bp
from models import db
from datetime import datetime, timezone

from utils.db_helpers import check_row_or_abort
@recurso_tipos_bp.route('/api/recurso-tipos', methods=['GET'])
def get_recurso_tipos():
    """Listar tipos de recursos
    ---
    tags:
      - Recurso Tipos
    responses:
      200:
        description: Lista de tipos de recursos
        schema:
          type: array
          items:
            type: object
            properties:
              id: {type: integer}
              recurso_categoria_id: {type: integer}
              recurso_grupo_id: {type: integer}
              nombre: {type: string}
              descripcion: {type: string}
              activo: {type: boolean}
              creador: {type: string}
              creacion: {type: string}
              modificador: {type: string}
              modificacion: {type: string}
    """
    query = db.text("""
      SELECT g.recurso_categoria_id, g.id AS recurso_grupo_id, g.nombre AS recurso_grupo_nombre, t.*
      FROM public.recurso_tipos t
      INNER JOIN public.recurso_grupos g ON t.recurso_grupo_id = g.id
      ORDER BY t.id ASC 
    """)

    result = db.session.execute(query)
    tipos = []
    for row in result:
        tipos.append({
            'id': row.id,
            'recurso_categoria_id': getattr(row, 'recurso_categoria_id', None),
            'recurso_grupo_id': getattr(row, 'recurso_grupo_id', None),
            'recurso_grupo_nombre': getattr(row, 'recurso_grupo_nombre', None), 
            'nombre': row.nombre,
            'descripcion': row.descripcion,
            'activo': row.activo,
            'creador': row.creador,
            'creacion': row.creacion.isoformat() if row.creacion else None,
            'modificador': row.modificador,
            'modificacion': row.modificacion.isoformat() if row.modificacion else None
        })
    return jsonify(tipos)

@recurso_tipos_bp.route('/api/recurso-tipos/categoria/<int:categoria_id>', methods=['GET'])
def get_recurso_tipos_by_categoria(categoria_id):
    """Listar tipos de recursos por categoría
    ---
    tags:
      - Recurso Tipos
    parameters:
      - name: categoria_id
        in: path
        type: integer
        required: true
    responses:
      200:
        description: Lista de tipos de recursos filtrados por categoría
        schema:
          type: array
          items:
            type: object
            properties:
              id: {type: integer}
              recurso_categoria_id: {type: integer}
              recurso_grupo_id: {type: integer}
              nombre: {type: string}
              descripcion: {type: string}
              activo: {type: boolean}
              creador: {type: string}
              creacion: {type: string}
              modificador: {type: string}
              modificacion: {type: string}
    """
    query = db.text("""
      SELECT g.recurso_categoria_id, t.*
      FROM public.recurso_tipos t
      INNER JOIN public.recurso_grupos g ON t.recurso_grupo_id = g.id     
      WHERE g.recurso_categoria_id = :categoria_id
      ORDER BY t.id ASC 
    """)

    result = db.session.execute(query, {'categoria_id': categoria_id})
    tipos = []
    for row in result:
        tipos.append({
            'id': row.id,
            'recurso_categoria_id': getattr(row, 'recurso_categoria_id', None),
            'recurso_grupo_id': getattr(row, 'recurso_grupo_id', None),
            'nombre': row.nombre,
            'descripcion': row.descripcion,
            'activo': row.activo,
            'creador': row.creador,
            'creacion': row.creacion.isoformat() if row.creacion else None,
            'modificador': row.modificador,
            'modificacion': row.modificacion.isoformat() if row.modificacion else None
        })

    return jsonify(tipos)

@recurso_tipos_bp.route('/api/recurso_tipos', methods=['POST'])
def create_recurso_tipo():
    """Crear tipo de recurso
    ---
    tags:
      - Recurso Tipos
    consumes:
      - application/json
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          required: [recurso_grupo_id, nombre]
          properties:
            recurso_grupo_id: {type: integer}
            nombre: {type: string}
            descripcion: {type: string}
            activo: {type: boolean}
            creador: {type: string}
    responses:
      201:
        description: Tipo de recurso creado
    """
    data = request.get_json()
    now = datetime.now(timezone.utc)
    
    query = db.text("""
        INSERT INTO recurso_tipos (
            recurso_grupo_id,
            nombre, descripcion, activo,
            creador, creacion, modificador, modificacion
        )
        VALUES (
            :recurso_grupo_id,
            :nombre, :descripcion, :activo,
            :creador, :creacion, :modificador, :modificacion
        )
        RETURNING id
    """)
    
    result = db.session.execute(query, {
        'recurso_grupo_id': data['recurso_grupo_id'],
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
    tipo_id = row[0]
    db.session.commit()
    
    query = db.text("""
      SELECT g.recurso_categoria_id, t.*
      FROM public.recurso_tipos t
      INNER JOIN public.recurso_grupos g ON t.recurso_grupo_id = g.id     
      WHERE t.id = :id
      ORDER BY t.id ASC 
    """)

    result = db.session.execute(query, {'id': id})
    tipos = []
    for row in result:
        tipos.append({
            'id': row.id,
            'recurso_categoria_id': getattr(row, 'recurso_categoria_id', None),
            'recurso_grupo_id': getattr(row, 'recurso_grupo_id', None),
            'nombre': row.nombre,
            'descripcion': row.descripcion,
            'activo': row.activo,
            'creador': row.creador,
            'creacion': row.creacion.isoformat() if row.creacion else None,
            'modificador': row.modificador,
            'modificacion': row.modificacion.isoformat() if row.modificacion else None
        })

    return jsonify(tipos), 201

@recurso_tipos_bp.route('/api/recurso-tipos/<int:id>', methods=['GET'])
def get_recurso_tipo(id):
    """Obtener tipo de recurso por ID
    ---
    tags:
      - Recurso Tipos
    parameters:
      - name: id
        in: path
        type: integer
        required: true
    responses:
      200:
        description: Tipo de recurso
        schema:
          type: object
          properties:
            id: {type: integer}
            recurso_categoria_id: {type: integer}
            recurso_grupo_id: {type: integer}
            nombre: {type: string}
            descripcion: {type: string}
            activo: {type: boolean}
            creador: {type: string}
            creacion: {type: string}
            modificador: {type: string}
            modificacion: {type: string}
      404:
        description: No encontrado
    """
    query = db.text("""
      SELECT g.recurso_categoria_id, t.*
      FROM public.recurso_tipos t
      INNER JOIN public.recurso_grupos g ON t.recurso_grupo_id = g.id     
      WHERE t.id = :id
      ORDER BY t.id ASC 
    """)

    result = db.session.execute(query, {'id': id})
    tipos = []
    for row in result:
        tipos.append({
            'id': row.id,
            'recurso_categoria_id': getattr(row, 'recurso_categoria_id', None),
            'recurso_grupo_id': getattr(row, 'recurso_grupo_id', None),
            'nombre': row.nombre,
            'descripcion': row.descripcion,
            'activo': row.activo,
            'creador': row.creador,
            'creacion': row.creacion.isoformat() if row.creacion else None,
            'modificador': row.modificador,
            'modificacion': row.modificacion.isoformat() if row.modificacion else None
        })

    return jsonify(tipos)

@recurso_tipos_bp.route('/api/recurso-tipos/<int:id>', methods=['PUT'])
def update_recurso_tipo(id):
    """Actualizar tipo de recurso
    ---
    tags:
      - Recurso Tipos
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
            recurso_categoria_id: {type: integer}
            recurso_grupo_id: {type: integer}
            nombre: {type: string}
            descripcion: {type: string}
            activo: {type: boolean}
            modificador: {type: string}
    responses:
      200:
        description: Tipo de recurso actualizado
      404:
        description: No encontrado
    """
    data = request.get_json()
    now = datetime.now(timezone.utc)
    
    query = db.text("""
        UPDATE recurso_tipos 
        SET recurso_categoria_id = :recurso_categoria_id,
            recurso_grupo_id      = :recurso_grupo_id,
            nombre                = :nombre,
            descripcion           = :descripcion,
            activo                = :activo,
            modificador           = :modificador,
            modificacion          = :modificacion
        WHERE id = :id
    """)
    
    result = db.session.execute(query, {
        'id': id,
        'recurso_categoria_id': data.get('recurso_categoria_id'),
        'recurso_grupo_id': data.get('recurso_grupo_id'),
        'nombre': data.get('nombre'),
        'descripcion': data.get('descripcion'),
        'activo': data.get('activo'),
        'modificador': data.get('modificador', 'Sistema'),
        'modificacion': now
    })
    
    if getattr(result, 'rowcount', 0) == 0:
        return jsonify({'error': 'Tipo no encontrado'}), 404
    
    db.session.commit()
    
    query = db.text("""
      SELECT g.recurso_categoria_id, t.*
      FROM public.recurso_tipos t
      INNER JOIN public.recurso_grupos g ON t.recurso_grupo_id = g.id     
      WHERE t.id = :id
      ORDER BY t.id ASC 
    """)

    result = db.session.execute(query, {'id': id})
    tipos = []
    for row in result:
        tipos.append({
            'id': row.id,
            'recurso_categoria_id': getattr(row, 'recurso_categoria_id', None),
            'recurso_grupo_id': getattr(row, 'recurso_grupo_id', None),
            'nombre': row.nombre,
            'descripcion': row.descripcion,
            'activo': row.activo,
            'creador': row.creador,
            'creacion': row.creacion.isoformat() if row.creacion else None,
            'modificador': row.modificador,
            'modificacion': row.modificacion.isoformat() if row.modificacion else None
        })

    return jsonify(tipos), 200

@recurso_tipos_bp.route('/api/recurso-tipos/<int:id>', methods=['DELETE'])
def delete_recurso_tipo(id):
    """Eliminar tipo de recurso
    ---
    tags:
      - Recurso Tipos
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
        db.text("DELETE FROM recurso_tipos WHERE id = :id"), 
        {'id': id}
    )
    
    if getattr(result, 'rowcount', 0) == 0:
        return jsonify({'error': 'Tipo no encontrado'}), 404
    
    db.session.commit()
    return jsonify({'mensaje': 'Tipo eliminado correctamente'})

@recurso_tipos_bp.route('/api/recurso-tipos/grupo/<int:grupo_id>', methods=['GET'])
def get_recurso_tipos_by_grupo(grupo_id):
    """Obtener tipos de recursos por el grupo de recursos seleccionado
    ---
    tags:
      - Recurso Tipos
    parameters:
      - name: grupo_id
        in: path
        type: integer
        required: true
    responses:
      200:
        description: Tipos de recursos por el grupo de recursos seleccionado 
        schema:
          type: array
          items:
            type: object
            properties:
              id: {type: integer}
              nombre: {type: string}
              descripcion: {type: string}
              costo: {type: string}
              complemento: {type: string}
    """
    query = db.text("""
      SELECT g.recurso_categoria_id, t.*
      FROM public.recurso_tipos t
      INNER JOIN public.recurso_grupos g ON t.recurso_grupo_id = g.id     
      WHERE t.recurso_grupo_id = :grupo_id
      ORDER BY t.id ASC 
    """)

    result = db.session.execute(query, {'grupo_id': grupo_id})
    tipos = []
    for row in result:
        tipos.append({
            'id': row.id,
            'recurso_categoria_id': getattr(row, 'recurso_categoria_id', None),
            'recurso_grupo_id': getattr(row, 'recurso_grupo_id', None),
            'nombre': row.nombre,
            'descripcion': row.descripcion,
            'activo': row.activo,
            'creador': row.creador,
            'creacion': row.creacion.isoformat() if row.creacion else None,
            'modificador': row.modificador,
            'modificacion': row.modificacion.isoformat() if row.modificacion else None
        })

    return jsonify(tipos), 200
