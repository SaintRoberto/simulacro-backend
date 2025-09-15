from flask import request, jsonify
from respuesta_estados import respuesta_estados_bp
from models import db
from datetime import datetime, timezone

@respuesta_estados_bp.route('/api/respuesta-estados', methods=['GET'])
def get_respuesta_estados():
    """Listar estados de respuesta
    ---
    tags:
      - Respuesta Estados
    responses:
      200:
        description: Lista de estados de respuesta
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
    result = db.session.execute(db.text("SELECT * FROM respuesta_estados"))
    estados = []
    for row in result:
        estados.append({
            'id': row.id,
            'nombre': row.nombre,
            'descripcion': row.descripcion,
            'activo': row.activo,
            'creador': row.creador,
            'creacion': row.creacion.isoformat() if row.creacion else None,
            'modificador': row.modificador,
            'modificacion': row.modificacion.isoformat() if row.modificacion else None
        })
    return jsonify(estados)

@respuesta_estados_bp.route('/api/respuesta-estados', methods=['POST'])
def create_respuesta_estado():
    """Crear estado de respuesta
    ---
    tags:
      - Respuesta Estados
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
        description: Estado de respuesta creado
    """
    data = request.get_json()
    now = datetime.now(timezone.utc)
    
    query = db.text("""
        INSERT INTO respuesta_estados (nombre, descripcion, activo, creador, creacion, modificador, modificacion)
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
        db.text("SELECT * FROM respuesta_estados WHERE id = :id"), 
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

@respuesta_estados_bp.route('/api/respuesta-estados/<int:id>', methods=['GET'])
def get_respuesta_estado(id):
    """Obtener estado de respuesta por ID
    ---
    tags:
      - Respuesta Estados
    parameters:
      - name: id
        in: path
        type: integer
        required: true
    responses:
      200:
        description: Estado de respuesta
      404:
        description: No encontrado
    """
    result = db.session.execute(
        db.text("SELECT * FROM respuesta_estados WHERE id = :id"), 
        {'id': id}
    )
    estado = result.fetchone()
    
    if not estado:
        return jsonify({'error': 'Estado no encontrado'}), 404
    
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

@respuesta_estados_bp.route('/api/respuesta-estados/<int:id>', methods=['PUT'])
def update_respuesta_estado(id):
    """Actualizar estado de respuesta
    ---
    tags:
      - Respuesta Estados
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
        description: Estado de respuesta actualizado
      404:
        description: No encontrado
    """
    data = request.get_json()
    now = datetime.now(timezone.utc)
    
    query = db.text("""
        UPDATE respuesta_estados 
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
        return jsonify({'error': 'Estado no encontrado'}), 404
    
    db.session.commit()
    
    estado = db.session.execute(
        db.text("SELECT * FROM respuesta_estados WHERE id = :id"), 
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

@respuesta_estados_bp.route('/api/respuesta-estados/<int:id>', methods=['DELETE'])
def delete_respuesta_estado(id):
    """Eliminar estado de respuesta
    ---
    tags:
      - Respuesta Estados
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
        db.text("DELETE FROM respuesta_estados WHERE id = :id"), 
        {'id': id}
    )
    
    if result.rowcount == 0:
        return jsonify({'error': 'Estado no encontrado'}), 404
    
    db.session.commit()
    return jsonify({'mensaje': 'Estado eliminado correctamente'})
