from flask import request, jsonify
from requerimiento_huella_logs import requerimiento_huella_logs_bp
from models import db
from datetime import datetime, timezone


def _serialize_requerimiento_huella_log(row):
    return {
        'id': row.id,
        'requerimiento_recurso_id': row.requerimiento_recurso_id,
        'requerimiento_numero': row.requerimiento_numero,
        'usuario_emisor_id': row.usuario_emisor_id,
        'usuario_receptor_id': row.usuario_receptor_id,
        'recurso_grupo_id': row.recurso_grupo_id,
        'recurso_tipo_id': row.recurso_tipo_id,
        'recurso_inventario_id': row.recurso_inventario_id,
        'cantidad_solicitada': row.cantidad_solicitada,
        'cantidad_asignada': row.cantidad_asignada,
        'requerimiento_estado_id': row.requerimiento_estado_id,
        'porcentaje_avance': row.porcentaje_avance,
        'respuesta_estado_id': row.respuesta_estado_id,
        'respuesta_fecha': row.respuesta_fecha.isoformat() if row.respuesta_fecha else None,
        'requerimiento_accion_log_id': row.requerimiento_accion_log_id,
        'log_creador': row.log_creador,
        'log_creacion': row.log_creacion.isoformat() if row.log_creacion else None
    }


@requerimiento_huella_logs_bp.route('/api/requerimiento-huella-logs', methods=['GET'])
def get_requerimiento_huella_logs():
    """Listar logs de huella de requerimientos
    ---
    tags:
      - Requerimiento Huella Logs
    responses:
      200:
        description: Lista de logs
        schema:
          type: array
          items:
            type: object
            properties:
              id: {type: integer}
              requerimiento_recurso_id: {type: integer}
              requerimiento_numero: {type: string}
              usuario_emisor_id: {type: integer}
              usuario_receptor_id: {type: integer}
              recurso_grupo_id: {type: integer}
              recurso_tipo_id: {type: integer}
              recurso_inventario_id: {type: integer}
              cantidad_solicitada: {type: integer}
              cantidad_asignada: {type: integer}
              requerimiento_estado_id: {type: integer}
              porcentaje_avance: {type: integer}
              respuesta_estado_id: {type: integer}
              respuesta_fecha: {type: string}
              requerimiento_accion_log_id: {type: integer}
              log_creador: {type: string}
              log_creacion: {type: string}
    """
    result = db.session.execute(
        db.text("SELECT * FROM requerimiento_huella_logs ORDER BY id DESC")
    )
    return jsonify([_serialize_requerimiento_huella_log(row) for row in result])


@requerimiento_huella_logs_bp.route('/api/requerimiento-huella-logs/<int:id>', methods=['GET'])
def get_requerimiento_huella_log_by_id(id):
    """Obtener log de huella de requerimiento por ID
    ---
    tags:
      - Requerimiento Huella Logs
    parameters:
      - name: id
        in: path
        type: integer
        required: true
    responses:
      200:
        description: Log encontrado
      404:
        description: Log no encontrado
    """
    row = db.session.execute(
        db.text("SELECT * FROM requerimiento_huella_logs WHERE id = :id"),
        {'id': id}
    ).fetchone()
    if row is None:
        return jsonify({'error': 'Log no encontrado'}), 404
    return jsonify(_serialize_requerimiento_huella_log(row))


@requerimiento_huella_logs_bp.route(
    '/api/requerimiento-huella-logs/requerimiento-recurso/<int:requerimiento_recurso_id>',
    methods=['GET']
)
def get_requerimiento_huella_log_by_requerimiento_recurso_id(requerimiento_recurso_id):
    """Obtener logs de huella por requerimiento_recurso_id
    ---
    tags:
      - Requerimiento Huella Logs
    parameters:
      - name: requerimiento_recurso_id
        in: path
        type: integer
        required: true
    responses:
      200:
        description: Lista de logs del requerimiento recurso
        schema:
          type: array
          items:
            type: object
            properties:
              id: {type: integer}
              requerimiento_recurso_id: {type: integer}
              requerimiento_numero: {type: string}
              usuario_emisor_id: {type: integer}
              usuario_receptor_id: {type: integer}
              recurso_grupo_id: {type: integer}
              recurso_tipo_id: {type: integer}
              recurso_inventario_id: {type: integer}
              cantidad_solicitada: {type: integer}
              cantidad_asignada: {type: integer}
              requerimiento_estado_id: {type: integer}
              porcentaje_avance: {type: integer}
              respuesta_estado_id: {type: integer}
              respuesta_fecha: {type: string}
              requerimiento_accion_log_id: {type: integer}
              log_creador: {type: string}
              log_creacion: {type: string}
    """
    result = db.session.execute(
        db.text("""
            SELECT *
            FROM requerimiento_huella_logs
            WHERE requerimiento_recurso_id = :requerimiento_recurso_id
            ORDER BY id DESC
        """),
        {'requerimiento_recurso_id': requerimiento_recurso_id}
    )
    return jsonify([_serialize_requerimiento_huella_log(row) for row in result])


@requerimiento_huella_logs_bp.route('/api/requerimiento-huella-logs', methods=['POST'])
def create_requerimiento_huella_log():
    """Crear log de huella de requerimiento
    ---
    tags:
      - Requerimiento Huella Logs
    consumes:
      - application/json
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          required:
            - usuario_receptor_id
            - recurso_grupo_id
            - recurso_tipo_id
            - recurso_inventario_id
            - requerimiento_estado_id
            - respuesta_estado_id
            - requerimiento_accion_log_id
          properties:
            requerimiento_recurso_id: {type: integer}
            requerimiento_numero: {type: string}
            usuario_emisor_id: {type: integer}
            usuario_receptor_id: {type: integer}
            recurso_grupo_id: {type: integer}
            recurso_tipo_id: {type: integer}
            recurso_inventario_id: {type: integer}
            cantidad_solicitada: {type: integer}
            cantidad_asignada: {type: integer}
            requerimiento_estado_id: {type: integer}
            porcentaje_avance: {type: integer}
            respuesta_estado_id: {type: integer}
            respuesta_fecha: {type: string}
            requerimiento_accion_log_id: {type: integer}
            log_creador: {type: string}
    responses:
      201:
        description: Log creado
      400:
        description: Campos faltantes
    """
    data = request.get_json() or {}
    required_fields = [
        'usuario_receptor_id',
        'recurso_grupo_id',
        'recurso_tipo_id',
        'recurso_inventario_id',
        'requerimiento_estado_id',
        'respuesta_estado_id',
        'requerimiento_accion_log_id'
    ]
    missing_fields = [field for field in required_fields if data.get(field) is None]
    if missing_fields:
        return jsonify({'error': f"Campos requeridos faltantes: {', '.join(missing_fields)}"}), 400

    now = datetime.now(timezone.utc)
    query = db.text("""
        INSERT INTO requerimiento_huella_logs (
            requerimiento_recurso_id, requerimiento_numero, usuario_emisor_id, usuario_receptor_id,
            recurso_grupo_id, recurso_tipo_id, recurso_inventario_id, cantidad_solicitada, cantidad_asignada,
            requerimiento_estado_id, porcentaje_avance, respuesta_estado_id, respuesta_fecha,
            requerimiento_accion_log_id, log_creador, log_creacion
        )
        VALUES (
            :requerimiento_recurso_id, :requerimiento_numero, :usuario_emisor_id, :usuario_receptor_id,
            :recurso_grupo_id, :recurso_tipo_id, :recurso_inventario_id, :cantidad_solicitada, :cantidad_asignada,
            :requerimiento_estado_id, :porcentaje_avance, :respuesta_estado_id, :respuesta_fecha,
            :requerimiento_accion_log_id, :log_creador, :log_creacion
        )
        RETURNING id
    """)
    result = db.session.execute(query, {
        'requerimiento_recurso_id': data.get('requerimiento_recurso_id'),
        'requerimiento_numero': data.get('requerimiento_numero'),
        'usuario_emisor_id': data.get('usuario_emisor_id'),
        'usuario_receptor_id': data['usuario_receptor_id'],
        'recurso_grupo_id': data['recurso_grupo_id'],
        'recurso_tipo_id': data['recurso_tipo_id'],
        'recurso_inventario_id': data['recurso_inventario_id'],
        'cantidad_solicitada': data.get('cantidad_solicitada', 1),
        'cantidad_asignada': data.get('cantidad_asignada', 1),
        'requerimiento_estado_id': data['requerimiento_estado_id'],
        'porcentaje_avance': data.get('porcentaje_avance', 0),
        'respuesta_estado_id': data['respuesta_estado_id'],
        'respuesta_fecha': data.get('respuesta_fecha', now),
        'requerimiento_accion_log_id': data['requerimiento_accion_log_id'],
        'log_creador': data.get('log_creador', 'Sistema'),
        'log_creacion': data.get('log_creacion', now)
    })

    row = result.fetchone()
    if row is None:
        db.session.rollback()
        return jsonify({'error': 'No se pudo crear el log'}), 500

    log_id = row[0]
    db.session.commit()

    created = db.session.execute(
        db.text("SELECT * FROM requerimiento_huella_logs WHERE id = :id"),
        {'id': log_id}
    ).fetchone()
    if created is None:
        return jsonify({'error': 'Log no encontrado despues de crear'}), 500

    return jsonify(_serialize_requerimiento_huella_log(created)), 201


@requerimiento_huella_logs_bp.route('/api/requerimiento-huella-logs/<int:id>', methods=['PUT'])
def update_requerimiento_huella_log(id):
    """Actualizar log de huella de requerimiento
    ---
    tags:
      - Requerimiento Huella Logs
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
            requerimiento_recurso_id: {type: integer}
            requerimiento_numero: {type: string}
            usuario_emisor_id: {type: integer}
            usuario_receptor_id: {type: integer}
            recurso_grupo_id: {type: integer}
            recurso_tipo_id: {type: integer}
            recurso_inventario_id: {type: integer}
            cantidad_solicitada: {type: integer}
            cantidad_asignada: {type: integer}
            requerimiento_estado_id: {type: integer}
            porcentaje_avance: {type: integer}
            respuesta_estado_id: {type: integer}
            respuesta_fecha: {type: string}
            requerimiento_accion_log_id: {type: integer}
            log_creador: {type: string}
            log_creacion: {type: string}
    responses:
      200:
        description: Log actualizado
      404:
        description: Log no encontrado
    """
    data = request.get_json() or {}
    actual = db.session.execute(
        db.text("SELECT * FROM requerimiento_huella_logs WHERE id = :id"),
        {'id': id}
    ).fetchone()
    if actual is None:
        return jsonify({'error': 'Log no encontrado'}), 404

    params = {
        'id': id,
        'requerimiento_recurso_id': data.get('requerimiento_recurso_id', actual.requerimiento_recurso_id),
        'requerimiento_numero': data.get('requerimiento_numero', actual.requerimiento_numero),
        'usuario_emisor_id': data.get('usuario_emisor_id', actual.usuario_emisor_id),
        'usuario_receptor_id': data.get('usuario_receptor_id', actual.usuario_receptor_id),
        'recurso_grupo_id': data.get('recurso_grupo_id', actual.recurso_grupo_id),
        'recurso_tipo_id': data.get('recurso_tipo_id', actual.recurso_tipo_id),
        'recurso_inventario_id': data.get('recurso_inventario_id', actual.recurso_inventario_id),
        'cantidad_solicitada': data.get('cantidad_solicitada', actual.cantidad_solicitada),
        'cantidad_asignada': data.get('cantidad_asignada', actual.cantidad_asignada),
        'requerimiento_estado_id': data.get('requerimiento_estado_id', actual.requerimiento_estado_id),
        'porcentaje_avance': data.get('porcentaje_avance', actual.porcentaje_avance),
        'respuesta_estado_id': data.get('respuesta_estado_id', actual.respuesta_estado_id),
        'respuesta_fecha': data.get('respuesta_fecha', actual.respuesta_fecha),
        'requerimiento_accion_log_id': data.get(
            'requerimiento_accion_log_id',
            actual.requerimiento_accion_log_id
        ),
        'log_creador': data.get('log_creador', actual.log_creador),
        'log_creacion': data.get('log_creacion', actual.log_creacion)
    }

    query = db.text("""
        UPDATE requerimiento_huella_logs
        SET requerimiento_recurso_id = :requerimiento_recurso_id,
            requerimiento_numero = :requerimiento_numero,
            usuario_emisor_id = :usuario_emisor_id,
            usuario_receptor_id = :usuario_receptor_id,
            recurso_grupo_id = :recurso_grupo_id,
            recurso_tipo_id = :recurso_tipo_id,
            recurso_inventario_id = :recurso_inventario_id,
            cantidad_solicitada = :cantidad_solicitada,
            cantidad_asignada = :cantidad_asignada,
            requerimiento_estado_id = :requerimiento_estado_id,
            porcentaje_avance = :porcentaje_avance,
            respuesta_estado_id = :respuesta_estado_id,
            respuesta_fecha = :respuesta_fecha,
            requerimiento_accion_log_id = :requerimiento_accion_log_id,
            log_creador = :log_creador,
            log_creacion = :log_creacion
        WHERE id = :id
    """)
    db.session.execute(query, params)
    db.session.commit()

    updated = db.session.execute(
        db.text("SELECT * FROM requerimiento_huella_logs WHERE id = :id"),
        {'id': id}
    ).fetchone()
    if updated is None:
        return jsonify({'error': 'Log no encontrado despues de actualizar'}), 500

    return jsonify(_serialize_requerimiento_huella_log(updated))


@requerimiento_huella_logs_bp.route('/api/requerimiento-huella-logs/<int:id>', methods=['DELETE'])
def delete_requerimiento_huella_log(id):
    """Eliminar log de huella de requerimiento
    ---
    tags:
      - Requerimiento Huella Logs
    parameters:
      - name: id
        in: path
        type: integer
        required: true
    responses:
      200:
        description: Log eliminado
      404:
        description: Log no encontrado
    """
    result = db.session.execute(
        db.text("DELETE FROM requerimiento_huella_logs WHERE id = :id"),
        {'id': id}
    )
    if getattr(result, 'rowcount', 0) == 0:
        return jsonify({'error': 'Log no encontrado'}), 404

    db.session.commit()
    return jsonify({'mensaje': 'Log eliminado correctamente'})
