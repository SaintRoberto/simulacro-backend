from flask import request, jsonify
from requerimiento_estados import requerimiento_estados_bp
from models import db
from datetime import datetime, timezone

@requerimiento_estados_bp.route('/api/requerimiento_estados', methods=['GET'])
def get_requerimiento_estados():
    """
    Obtener lista de todos los estados de requerimiento
    ---
    tags:
      - Requerimiento Estados
    responses:
      200:
        description: Lista de estados de requerimiento obtenida exitosamente
        schema:
          type: array
          items:
            type: object
            properties:
              id:
                type: integer
                description: ID del estado
              nombre:
                type: string
                description: Nombre del estado
              descripcion:
                type: string
                description: Descripción del estado
              activo:
                type: boolean
                description: Estado activo/inactivo
              creador:
                type: string
                description: Usuario que creó el registro
              creacion:
                type: string
                format: date-time
                description: Fecha de creación
              modificador:
                type: string
                description: Usuario que modificó el registro
              modificacion:
                type: string
                format: date-time
                description: Fecha de modificación
        examples:
          application/json: [
            {
              "id": 1,
              "nombre": "Pendiente",
              "descripcion": "Estado inicial del requerimiento",
              "activo": true,
              "creador": "admin",
              "creacion": "2023-01-01T00:00:00",
              "modificador": "admin",
              "modificacion": "2023-01-01T00:00:00"
            }
          ]
    """
    result = db.session.execute(db.text("SELECT * FROM requerimiento_estados"))
    requerimiento_estados = []
    for row in result:
        requerimiento_estados.append({
            'id': row.id,
            'nombre': row.nombre,
            'descripcion': row.descripcion,
            'activo': row.activo,
            'creador': row.creador,
            'creacion': row.creacion.isoformat() if row.creacion else None,
            'modificador': row.modificador,
            'modificacion': row.modificacion.isoformat() if row.modificacion else None
        })
    return jsonify(requerimiento_estados)

@requerimiento_estados_bp.route('/api/requerimiento_estados', methods=['POST'])
def create_requerimiento_estado():
    """
    Crear un nuevo estado de requerimiento
    ---
    tags:
      - Requerimiento Estados
    parameters:
      - name: body
        in: body
        required: true
        schema:
          type: object
          properties:
            nombre:
              type: string
              description: Nombre del estado
              required: true
            descripcion:
              type: string
              description: Descripción del estado
            activo:
              type: boolean
              description: Estado activo/inactivo
              default: true
            creador:
              type: string
              description: Usuario que crea el registro
              default: "Sistema"
        examples:
          application/json: {
            "nombre": "Pendiente",
            "descripcion": "Estado inicial del requerimiento",
            "activo": true,
            "creador": "admin"
          }
    responses:
      201:
        description: Estado de requerimiento creado exitosamente
        schema:
          type: object
          properties:
            id:
              type: integer
              description: ID del estado creado
            nombre:
              type: string
              description: Nombre del estado
            descripcion:
              type: string
              description: Descripción del estado
            activo:
              type: boolean
              description: Estado activo/inactivo
            creador:
              type: string
              description: Usuario que creó el registro
            creacion:
              type: string
              format: date-time
              description: Fecha de creación
            modificador:
              type: string
              description: Usuario que modificó el registro
            modificacion:
              type: string
              format: date-time
              description: Fecha de modificación
        examples:
          application/json: {
            "id": 1,
            "nombre": "Pendiente",
            "descripcion": "Estado inicial del requerimiento",
            "activo": true,
            "creador": "admin",
            "creacion": "2023-01-01T00:00:00",
            "modificador": "admin",
            "modificacion": "2023-01-01T00:00:00"
          }
      400:
        description: Datos inválidos
        examples:
          application/json: {"error": "Datos requeridos faltantes"}
    """
    data = request.get_json()
    now = datetime.now(timezone.utc)
    
    query = db.text("""
        INSERT INTO requerimiento_estados (nombre, descripcion, activo, creador, creacion, modificador, modificacion)
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
    
    estado_id = result.fetchone()[0]
    db.session.commit()
    
    estado = db.session.execute(
        db.text("SELECT * FROM requerimiento_estados WHERE id = :id"), 
        {'id': estado_id}
    ).fetchone()
    
    return jsonify({
        'id': estado.id,
        'nombre': estado.nombre,
        'descripcion': estado.descripcion,
        'activo': estado.activo,
        'creador': estado.creador,
        'creacion': estado.creacion.isoformat() if estado.creacion else None,
        'modificador': estado.modificador,
        'modificacion': estado.modificacion.isoformat() if estado.modificacion else None
    }), 201

@requerimiento_estados_bp.route('/api/requerimiento_estados/<int:id>', methods=['GET'])
def get_requerimiento_estado(id):
    """
    Obtener un estado de requerimiento específico por ID
    ---
    tags:
      - Requerimiento Estados
    parameters:
      - name: id
        in: path
        type: integer
        required: true
        description: ID del estado de requerimiento
    responses:
      200:
        description: Estado de requerimiento encontrado exitosamente
        schema:
          type: object
          properties:
            id:
              type: integer
              description: ID del estado
            nombre:
              type: string
              description: Nombre del estado
            descripcion:
              type: string
              description: Descripción del estado
            activo:
              type: boolean
              description: Estado activo/inactivo
            creador:
              type: string
              description: Usuario que creó el registro
            creacion:
              type: string
              format: date-time
              description: Fecha de creación
            modificador:
              type: string
              description: Usuario que modificó el registro
            modificacion:
              type: string
              format: date-time
              description: Fecha de modificación
        examples:
          application/json: {
            "id": 1,
            "nombre": "Pendiente",
            "descripcion": "Estado inicial del requerimiento",
            "activo": true,
            "creador": "admin",
            "creacion": "2023-01-01T00:00:00",
            "modificador": "admin",
            "modificacion": "2023-01-01T00:00:00"
          }
      404:
        description: Estado de requerimiento no encontrado
        examples:
          application/json: {"error": "Estado de requerimiento no encontrado"}
    """
    result = db.session.execute(
        db.text("SELECT * FROM requerimiento_estados WHERE id = :id"), 
        {'id': id}
    )
    estado = result.fetchone()
    
    if not estado:
        return jsonify({'error': 'Estado de requerimiento no encontrado'}), 404
    
    return jsonify({
        'id': estado.id,
        'nombre': estado.nombre,
        'descripcion': estado.descripcion,
        'activo': estado.activo,
        'creador': estado.creador,
        'creacion': estado.creacion.isoformat() if estado.creacion else None,
        'modificador': estado.modificador,
        'modificacion': estado.modificacion.isoformat() if estado.modificacion else None
    })

@requerimiento_estados_bp.route('/api/requerimiento_estados/<int:id>', methods=['PUT'])
def update_requerimiento_estado(id):
    """
    Actualizar un estado de requerimiento existente
    ---
    tags:
      - Requerimiento Estados
    parameters:
      - name: id
        in: path
        type: integer
        required: true
        description: ID del estado de requerimiento a actualizar
      - name: body
        in: body
        required: true
        schema:
          type: object
          properties:
            nombre:
              type: string
              description: Nombre del estado
            descripcion:
              type: string
              description: Descripción del estado
            activo:
              type: boolean
              description: Estado activo/inactivo
            modificador:
              type: string
              description: Usuario que modifica el registro
              default: "Sistema"
        examples:
          application/json: {
            "nombre": "En Progreso",
            "descripcion": "Estado cuando el requerimiento está siendo procesado",
            "activo": true,
            "modificador": "admin"
          }
    responses:
      200:
        description: Estado de requerimiento actualizado exitosamente
        schema:
          type: object
          properties:
            id:
              type: integer
              description: ID del estado
            nombre:
              type: string
              description: Nombre del estado
            descripcion:
              type: string
              description: Descripción del estado
            activo:
              type: boolean
              description: Estado activo/inactivo
            creador:
              type: string
              description: Usuario que creó el registro
            creacion:
              type: string
              format: date-time
              description: Fecha de creación
            modificador:
              type: string
              description: Usuario que modificó el registro
            modificacion:
              type: string
              format: date-time
              description: Fecha de modificación
        examples:
          application/json: {
            "id": 1,
            "nombre": "En Progreso",
            "descripcion": "Estado cuando el requerimiento está siendo procesado",
            "activo": true,
            "creador": "admin",
            "creacion": "2023-01-01T00:00:00",
            "modificador": "admin",
            "modificacion": "2023-01-01T12:00:00"
          }
      404:
        description: Estado de requerimiento no encontrado
        examples:
          application/json: {"error": "Estado de requerimiento no encontrado"}
    """
    data = request.get_json()
    now = datetime.now(timezone.utc)
    
    query = db.text("""
        UPDATE requerimiento_estados 
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
        return jsonify({'error': 'Estado de requerimiento no encontrado'}), 404
    
    db.session.commit()
    
    estado = db.session.execute(
        db.text("SELECT * FROM requerimiento_estados WHERE id = :id"), 
        {'id': id}
    ).fetchone()
    
    return jsonify({
        'id': estado.id,
        'nombre': estado.nombre,
        'descripcion': estado.descripcion,
        'activo': estado.activo,
        'creador': estado.creador,
        'creacion': estado.creacion.isoformat() if estado.creacion else None,
        'modificador': estado.modificador,
        'modificacion': estado.modificacion.isoformat() if estado.modificacion else None
    })

@requerimiento_estados_bp.route('/api/requerimiento_estados/<int:id>', methods=['DELETE'])
def delete_requerimiento_estado(id):
    """
    Eliminar un estado de requerimiento
    ---
    tags:
      - Requerimiento Estados
    parameters:
      - name: id
        in: path
        type: integer
        required: true
        description: ID del estado de requerimiento a eliminar
    responses:
      200:
        description: Estado de requerimiento eliminado exitosamente
        schema:
          type: object
          properties:
            mensaje:
              type: string
              description: Mensaje de confirmación
        examples:
          application/json: {"mensaje": "Estado de requerimiento eliminado correctamente"}
      404:
        description: Estado de requerimiento no encontrado
        examples:
          application/json: {"error": "Estado de requerimiento no encontrado"}
    """
    result = db.session.execute(
        db.text("DELETE FROM requerimiento_estados WHERE id = :id"), 
        {'id': id}
    )
    
    if result.rowcount == 0:
        return jsonify({'error': 'Estado de requerimiento no encontrado'}), 404
    
    db.session.commit()
    return jsonify({'mensaje': 'Estado de requerimiento eliminado correctamente'})