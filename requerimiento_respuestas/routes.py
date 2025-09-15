from flask import request, jsonify
from requerimiento_respuestas import requerimiento_respuestas_bp
from models import db
from datetime import datetime, timezone

@requerimiento_respuestas_bp.route('/api/requerimiento-respuestas', methods=['GET'])
def get_requerimiento_respuestas():
    """Listar respuestas de requerimientos
    ---
    tags:
      - Requerimiento Respuestas
    responses:
      200:
        description: Lista de respuestas de requerimientos
        schema:
          type: array
          items:
            type: object
            properties:
              id: {type: integer}
              requerimiento_id: {type: integer}
              respuesta_estado_id: {type: integer}
              observaciones: {type: string}
              activo: {type: boolean}
              creador: {type: string}
              creacion: {type: string}
              modificador: {type: string}
              modificacion: {type: string}
    """
    result = db.session.execute(db.text("SELECT * FROM requerimiento_respuestas"))
    respuestas = []
    for row in result:
        respuestas.append({
            'id': row.id,
            'requerimiento_id': row.requerimiento_id,
            'respuesta_estado_id': row.respuesta_estado_id,
            'observaciones': row.observaciones,
            'activo': row.activo,
            'creador': row.creador,
            'creacion': row.creacion.isoformat() if row.creacion else None,
            'modificador': row.modificador,
            'modificacion': row.modificacion.isoformat() if row.modificacion else None
        })
    return jsonify(respuestas)

@requerimiento_respuestas_bp.route('/api/requerimiento-respuestas', methods=['POST'])
def create_requerimiento_respuesta():
    """Crear respuesta de requerimiento
    ---
    tags:
      - Requerimiento Respuestas
    consumes:
      - application/json
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          required: [requerimiento_id, respuesta_estado_id]
          properties:
            requerimiento_id: {type: integer}
            respuesta_estado_id: {type: integer}
            observaciones: {type: string}
            activo: {type: boolean}
            creador: {type: string}
    responses:
      201:
        description: Respuesta de requerimiento creada
    """
    data = request.get_json()
    now = datetime.now(timezone.utc)
    
    query = db.text("""
        INSERT INTO requerimiento_respuestas (
            requerimiento_id, respuesta_estado_id, observaciones, activo,
            creador, creacion, modificador, modificacion
        )
        VALUES (
            :requerimiento_id, :respuesta_estado_id, :observaciones, :activo,
            :creador, :creacion, :modificador, :modificacion
        )
        RETURNING id
    """)
    
    result = db.session.execute(query, {
        'requerimiento_id': data['requerimiento_id'],
        'respuesta_estado_id': data['respuesta_estado_id'],
        'observaciones': data.get('observaciones'),
        'activo': data.get('activo', True),
        'creador': data.get('creador', 'Sistema'),
        'creacion': now,
        'modificador': data.get('creador', 'Sistema'),
        'modificacion': now
    })
    
    respuesta_id = result.fetchone()[0]
    db.session.commit()
    
    respuesta = db.session.execute(
        db.text("SELECT * FROM requerimiento_respuestas WHERE id = :id"), 
        {'id': respuesta_id}
    ).fetchone()
    
    return jsonify({
        'id': respuesta.id,
        'requerimiento_id': respuesta.requerimiento_id,
        'respuesta_estado_id': respuesta.respuesta_estado_id,
        'observaciones': respuesta.observaciones,
        'activo': respuesta.activo,
        'creador': respuesta.creador,
        'creacion': respuesta.creacion.isoformat() if respuesta.creacion else None,
        'modificador': respuesta.modificador,
        'modificacion': respuesta.modificacion.isoformat() if respuesta.modificacion else None
    }), 201

@requerimiento_respuestas_bp.route('/api/requerimiento-respuestas/<int:id>', methods=['GET'])
def get_requerimiento_respuesta(id):
    """Obtener respuesta de requerimiento por ID
    ---
    tags:
      - Requerimiento Respuestas
    parameters:
      - name: id
        in: path
        type: integer
        required: true
    responses:
      200:
        description: Respuesta de requerimiento
      404:
        description: No encontrada
    """
    result = db.session.execute(
        db.text("SELECT * FROM requerimiento_respuestas WHERE id = :id"), 
        {'id': id}
    )
    respuesta = result.fetchone()
    
    if not respuesta:
        return jsonify({'error': 'Respuesta no encontrada'}), 404
    
    return jsonify({
        'id': respuesta.id,
        'requerimiento_id': respuesta.requerimiento_id,
        'respuesta_estado_id': respuesta.respuesta_estado_id,
        'observaciones': respuesta.observaciones,
        'activo': respuesta.activo,
        'creador': respuesta.creador,
        'creacion': respuesta.creacion.isoformat() if respuesta.creacion else None,
        'modificador': respuesta.modificador,
        'modificacion': respuesta.modificacion.isoformat() if respuesta.modificacion else None
    })

@requerimiento_respuestas_bp.route('/api/requerimiento-respuestas/<int:id>', methods=['PUT'])
def update_requerimiento_respuesta(id):
    """Actualizar respuesta de requerimiento
    ---
    tags:
      - Requerimiento Respuestas
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
            requerimiento_id: {type: integer}
            respuesta_estado_id: {type: integer}
            observaciones: {type: string}
            activo: {type: boolean}
            modificador: {type: string}
    responses:
      200:
        description: Respuesta de requerimiento actualizada
      404:
        description: No encontrada
    """
    data = request.get_json()
    now = datetime.now(timezone.utc)
    
    query = db.text("""
        UPDATE requerimiento_respuestas 
        SET requerimiento_id = :requerimiento_id, 
            respuesta_estado_id = :respuesta_estado_id, 
            observaciones = :observaciones, 
            activo = :activo, 
            modificador = :modificador, 
            modificacion = :modificacion
        WHERE id = :id
    """)
    
    result = db.session.execute(query, {
        'id': id,
        'requerimiento_id': data.get('requerimiento_id'),
        'respuesta_estado_id': data.get('respuesta_estado_id'),
        'observaciones': data.get('observaciones'),
        'activo': data.get('activo'),
        'modificador': data.get('modificador', 'Sistema'),
        'modificacion': now
    })
    
    if result.rowcount == 0:
        return jsonify({'error': 'Respuesta no encontrada'}), 404
    
    db.session.commit()
    
    respuesta = db.session.execute(
        db.text("SELECT * FROM requerimiento_respuestas WHERE id = :id"), 
        {'id': id}
    ).fetchone()
    
    return jsonify({
        'id': respuesta.id,
        'requerimiento_id': respuesta.requerimiento_id,
        'respuesta_estado_id': respuesta.respuesta_estado_id,
        'observaciones': respuesta.observaciones,
        'activo': respuesta.activo,
        'creador': respuesta.creador,
        'creacion': respuesta.creacion.isoformat() if respuesta.creacion else None,
        'modificador': respuesta.modificador,
        'modificacion': respuesta.modificacion.isoformat() if respuesta.modificacion else None
    })

@requerimiento_respuestas_bp.route('/api/requerimiento-respuestas/<int:id>', methods=['DELETE'])
def delete_requerimiento_respuesta(id):
    """Eliminar respuesta de requerimiento
    ---
    tags:
      - Requerimiento Respuestas
    parameters:
      - name: id
        in: path
        type: integer
        required: true
    responses:
      200:
        description: Eliminada
      404:
        description: No encontrada
    """
    result = db.session.execute(
        db.text("DELETE FROM requerimiento_respuestas WHERE id = :id"), 
        {'id': id}
    )
    
    if result.rowcount == 0:
        return jsonify({'error': 'Respuesta no encontrada'}), 404
    
    db.session.commit()
    return jsonify({'mensaje': 'Respuesta eliminada correctamente'})
