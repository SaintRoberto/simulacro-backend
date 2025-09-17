from flask import request, jsonify
from recurso_tipos import recurso_tipos_bp
from models import db
from datetime import datetime, timezone

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
              nombre: {type: string}
              descripcion: {type: string}
              activo: {type: boolean}
              creador: {type: string}
              creacion: {type: string}
              modificador: {type: string}
              modificacion: {type: string}
    """
    result = db.session.execute(db.text("SELECT * FROM recurso_tipos"))
    tipos = []
    for row in result:
        tipos.append({
            'id': row.id,
            'nombre': row.nombre,
            'descripcion': row.descripcion,
            'activo': row.activo,
            'creador': row.creador,
            'creacion': row.creacion.isoformat() if row.creacion else None,
            'modificador': row.modificador,
            'modificacion': row.modificacion.isoformat() if row.modificacion else None
        })
    return jsonify(tipos)

@recurso_tipos_bp.route('/api/recurso-tipos', methods=['POST'])
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
          required: [nombre]
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
        INSERT INTO recurso_tipos (recurso_grupo_id, nombre, descripcion, activo, creador, creacion, modificador, modificacion)
        VALUES (:recurso_grupo_id, :nombre, :descripcion, :activo, :creador, :creacion, :modificador, :modificacion)
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
    
    tipo_id = result.fetchone()[0]
    db.session.commit()
    
    tipo = db.session.execute(
        db.text("SELECT * FROM recurso_tipos WHERE id = :id"), 
        {'id': tipo_id}
    ).fetchone()
    
    return jsonify({
        'id': tipo.id,
        'nombre': tipo.nombre,
        'descripcion': tipo.descripcion,
        'activo': tipo.activo,
        'creador': tipo.creador,
        'creacion': tipo.creacion.isoformat() if tipo.creacion else None,
        'modificador': tipo.modificador,
        'modificacion': tipo.modificacion.isoformat() if tipo.modificacion else None
    }), 201

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
      404:
        description: No encontrado
    """
    result = db.session.execute(
        db.text("SELECT * FROM recurso_tipos WHERE id = :id"), 
        {'id': id}
    )
    tipo = result.fetchone()
    
    if not tipo:
        return jsonify({'error': 'Tipo no encontrado'}), 404
    
    return jsonify({
        'id': tipo.id,
        'nombre': tipo.nombre,
        'descripcion': tipo.descripcion,
        'activo': tipo.activo,
        'creador': tipo.creador,
        'creacion': tipo.creacion.isoformat() if tipo.creacion else None,
        'modificador': tipo.modificador,
        'modificacion': tipo.modificacion.isoformat() if tipo.modificacion else None
    })

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
    
    if result.rowcount == 0:
        return jsonify({'error': 'Tipo no encontrado'}), 404
    
    db.session.commit()
    
    tipo = db.session.execute(
        db.text("SELECT * FROM recurso_tipos WHERE id = :id"), 
        {'id': id}
    ).fetchone()
    
    return jsonify({
        'id': tipo.id,
        'nombre': tipo.nombre,
        'descripcion': tipo.descripcion,
        'activo': tipo.activo,
        'creador': tipo.creador,
        'creacion': tipo.creacion.isoformat() if tipo.creacion else None,
        'modificador': tipo.modificador,
        'modificacion': tipo.modificacion.isoformat() if tipo.modificacion else None
    })

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
    
    if result.rowcount == 0:
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
    params = {'grupo_id': grupo_id}
    query = db.text("""SELECT id, nombre, descripcion, costo, complemento FROM recurso_tipos WHERE recurso_grupo_id = :grupo_id""")
    result = db.session.execute(query, params)
    tipos = []
    if not result:
        return jsonify({'error': 'Tipos de recursos por el grupo de recursos seleccionado no encontrados'}), 404
    for row in result:
        tipos.append({
            'id': row.id,
            'nombre': row.nombre,
            'descripcion': row.descripcion,
            'costo': row.costo,
            'complemento': row.complemento
        })
    return jsonify(tipos) 
