from flask import request, jsonify
from respuestas_avances import respuestas_avances_bp
from models import db
from datetime import datetime, timezone

@respuestas_avances_bp.route('/api/respuestas-avances', methods=['GET'])
def get_respuestas_avances():
    """Listar avances de respuestas
    ---
    tags:
      - Respuestas Avances
    responses:
      200:
        description: Lista de avances de respuestas
        schema:
          type: array
          items:
            type: object
            properties:
              id: {type: integer}
              requerimiento_respuesta_id: {type: integer}
              porcentaje_avance: {type: number}
              observaciones: {type: string}
              activo: {type: boolean}
              creador: {type: string}
              creacion: {type: string}
              modificador: {type: string}
              modificacion: {type: string}
    """
    result = db.session.execute(db.text("SELECT * FROM respuestas_avances"))
    avances = []
    for row in result:
        avances.append({
            'id': row.id,
            'requerimiento_respuesta_id': row.requerimiento_respuesta_id,
            'porcentaje_avance': float(row.porcentaje_avance) if row.porcentaje_avance else 0,
            'observaciones': row.observaciones,
            'activo': row.activo,
            'creador': row.creador,
            'creacion': row.creacion.isoformat() if row.creacion else None,
            'modificador': row.modificador,
            'modificacion': row.modificacion.isoformat() if row.modificacion else None
        })
    return jsonify(avances)

@respuestas_avances_bp.route('/api/respuestas-avances', methods=['POST'])
def create_respuesta_avance():
    """Crear avance de respuesta
    ---
    tags:
      - Respuestas Avances
    consumes:
      - application/json
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          required: [requerimiento_respuesta_id, porcentaje_avance]
          properties:
            requerimiento_respuesta_id: {type: integer}
            porcentaje_avance: {type: number}
            observaciones: {type: string}
            activo: {type: boolean}
            creador: {type: string}
    responses:
      201:
        description: Avance de respuesta creado
    """
    data = request.get_json()
    now = datetime.now(timezone.utc)
    
    query = db.text("""
        INSERT INTO respuestas_avances (
            requerimiento_respuesta_id, porcentaje_avance, observaciones, activo,
            creador, creacion, modificador, modificacion
        )
        VALUES (
            :requerimiento_respuesta_id, :porcentaje_avance, :observaciones, :activo,
            :creador, :creacion, :modificador, :modificacion
        )
        RETURNING id
    """)
    
    result = db.session.execute(query, {
        'requerimiento_respuesta_id': data['requerimiento_respuesta_id'],
        'porcentaje_avance': data['porcentaje_avance'],
        'observaciones': data.get('observaciones'),
        'activo': data.get('activo', True),
        'creador': data.get('creador', 'Sistema'),
        'creacion': now,
        'modificador': data.get('creador', 'Sistema'),
        'modificacion': now
    })
    
    avance_id = result.fetchone()[0]
    db.session.commit()
    
    avance = db.session.execute(
        db.text("SELECT * FROM respuestas_avances WHERE id = :id"), 
        {'id': avance_id}
    ).fetchone()
    
    return jsonify({
        'id': avance.id,
        'requerimiento_respuesta_id': avance.requerimiento_respuesta_id,
        'porcentaje_avance': float(avance.porcentaje_avance) if avance.porcentaje_avance else 0,
        'observaciones': avance.observaciones,
        'activo': avance.activo,
        'creador': avance.creador,
        'creacion': avance.creacion.isoformat() if avance.creacion else None,
        'modificador': avance.modificador,
        'modificacion': avance.modificacion.isoformat() if avance.modificacion else None
    }), 201

@respuestas_avances_bp.route('/api/respuestas-avances/<int:id>', methods=['GET'])
def get_respuesta_avance(id):
    """Obtener avance de respuesta por ID
    ---
    tags:
      - Respuestas Avances
    parameters:
      - name: id
        in: path
        type: integer
        required: true
    responses:
      200:
        description: Avance de respuesta
      404:
        description: No encontrado
    """
    result = db.session.execute(
        db.text("SELECT * FROM respuestas_avances WHERE id = :id"), 
        {'id': id}
    )
    avance = result.fetchone()
    
    if not avance:
        return jsonify({'error': 'Avance no encontrado'}), 404
    
    return jsonify({
        'id': avance.id,
        'requerimiento_respuesta_id': avance.requerimiento_respuesta_id,
        'porcentaje_avance': float(avance.porcentaje_avance) if avance.porcentaje_avance else 0,
        'observaciones': avance.observaciones,
        'activo': avance.activo,
        'creador': avance.creador,
        'creacion': avance.creacion.isoformat() if avance.creacion else None,
        'modificador': avance.modificador,
        'modificacion': avance.modificacion.isoformat() if avance.modificacion else None
    })

@respuestas_avances_bp.route('/api/respuestas-avances/<int:id>', methods=['PUT'])
def update_respuesta_avance(id):
    """Actualizar avance de respuesta
    ---
    tags:
      - Respuestas Avances
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
            requerimiento_respuesta_id: {type: integer}
            porcentaje_avance: {type: number}
            observaciones: {type: string}
            activo: {type: boolean}
            modificador: {type: string}
    responses:
      200:
        description: Avance de respuesta actualizado
      404:
        description: No encontrado
    """
    data = request.get_json()
    now = datetime.now(timezone.utc)
    
    query = db.text("""
        UPDATE respuestas_avances 
        SET requerimiento_respuesta_id = :requerimiento_respuesta_id, 
            porcentaje_avance = :porcentaje_avance, 
            observaciones = :observaciones, 
            activo = :activo, 
            modificador = :modificador, 
            modificacion = :modificacion
        WHERE id = :id
    """)
    
    result = db.session.execute(query, {
        'id': id,
        'requerimiento_respuesta_id': data.get('requerimiento_respuesta_id'),
        'porcentaje_avance': data.get('porcentaje_avance'),
        'observaciones': data.get('observaciones'),
        'activo': data.get('activo'),
        'modificador': data.get('modificador', 'Sistema'),
        'modificacion': now
    })
    
    if result.rowcount == 0:
        return jsonify({'error': 'Avance no encontrado'}), 404
    
    db.session.commit()
    
    avance = db.session.execute(
        db.text("SELECT * FROM respuestas_avances WHERE id = :id"), 
        {'id': id}
    ).fetchone()
    
    return jsonify({
        'id': avance.id,
        'requerimiento_respuesta_id': avance.requerimiento_respuesta_id,
        'porcentaje_avance': float(avance.porcentaje_avance) if avance.porcentaje_avance else 0,
        'observaciones': avance.observaciones,
        'activo': avance.activo,
        'creador': avance.creador,
        'creacion': avance.creacion.isoformat() if avance.creacion else None,
        'modificador': avance.modificador,
        'modificacion': avance.modificacion.isoformat() if avance.modificacion else None
    })

@respuestas_avances_bp.route('/api/respuestas-avances/<int:id>', methods=['DELETE'])
def delete_respuesta_avance(id):
    """Eliminar avance de respuesta
    ---
    tags:
      - Respuestas Avances
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
        db.text("DELETE FROM respuestas_avances WHERE id = :id"), 
        {'id': id}
    )
    
    if result.rowcount == 0:
        return jsonify({'error': 'Avance no encontrado'}), 404
    
    db.session.commit()
    return jsonify({'mensaje': 'Avance eliminado correctamente'})
