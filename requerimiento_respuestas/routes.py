from flask import request, jsonify
from requerimiento_respuestas import requerimiento_respuestas_bp
from models import db
from datetime import datetime, timezone


def _is_estado_finalizado(respuesta_estado_id):
    return respuesta_estado_id == 3


def _is_recurso_retorna(requerimiento_recurso_id):
    row = db.session.execute(
        db.text("""
            SELECT COALESCE(rt.retorna, false) AS retorna
            FROM requerimiento_recursos rr
            INNER JOIN recurso_tipos rt ON rr.recurso_tipo_id = rt.id
            WHERE rr.id = :requerimiento_recurso_id
        """),
        {'requerimiento_recurso_id': requerimiento_recurso_id}
    ).fetchone()
    return bool(row.retorna) if row is not None else False


def _serialize_requerimiento_respuesta(row):
    return {
        'id': row.id,
        'requerimiento_recurso_id': row.requerimiento_recurso_id,
        'cantidad_asignada': row.cantidad_asignada,
        'situacion_actual': row.situacion_actual,
        'porcentaje_avance': row.porcentaje_avance,
        'respuesta_estado_id': row.respuesta_estado_id,
        'responsable': row.responsable,
        'respuesta_fecha': row.respuesta_fecha.isoformat() if row.respuesta_fecha else None,
        'en_uso': row.en_uso,
        'activo': row.activo,
        'creador': row.creador,
        'creacion': row.creacion.isoformat() if row.creacion else None,
        'modificador': row.modificador,
        'modificacion': row.modificacion.isoformat() if row.modificacion else None
    }


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
              requerimiento_recurso_id: {type: integer}
              cantidad_asignada: {type: integer}
              situacion_actual: {type: string}
              porcentaje_avance: {type: integer}
              respuesta_estado_id: {type: integer}
              responsable: {type: string}
              respuesta_fecha: {type: string}
              en_uso: {type: integer}
              activo: {type: boolean}
              creador: {type: string}
              creacion: {type: string}
              modificador: {type: string}
              modificacion: {type: string}
    """
    result = db.session.execute(db.text("SELECT * FROM requerimiento_respuestas ORDER BY id DESC"))
    return jsonify([_serialize_requerimiento_respuesta(row) for row in result])


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
          required: [requerimiento_recurso_id, respuesta_estado_id]
          properties:
            requerimiento_recurso_id: {type: integer}
            cantidad_asignada: {type: integer}
            situacion_actual: {type: string}
            porcentaje_avance: {type: integer}
            respuesta_estado_id: {type: integer}
            responsable: {type: string}
            respuesta_fecha: {type: string}
            en_uso: {type: integer}
            activo: {type: boolean}
            creador: {type: string}
            modificador: {type: string}
            modificacion: {type: string}
    responses:
      201:
        description: Respuesta de requerimiento creada
        schema:
          type: object
          properties:
            id: {type: integer}
            requerimiento_recurso_id: {type: integer}
            cantidad_asignada: {type: integer}
            situacion_actual: {type: string}
            porcentaje_avance: {type: integer}
            respuesta_estado_id: {type: integer}
            responsable: {type: string}
            respuesta_fecha: {type: string}
            en_uso: {type: integer}
            activo: {type: boolean}
            creador: {type: string}
            creacion: {type: string}
            modificador: {type: string}
            modificacion: {type: string}
    """
    data = request.get_json() or {}
    required_fields = ['requerimiento_recurso_id', 'respuesta_estado_id']
    missing_fields = [field for field in required_fields if field not in data]
    if missing_fields:
        return jsonify({'error': f"Campos requeridos faltantes: {', '.join(missing_fields)}"}), 400

    now = datetime.now(timezone.utc)

    query = db.text("""
        INSERT INTO requerimiento_respuestas (
            requerimiento_recurso_id, cantidad_asignada, situacion_actual, porcentaje_avance,
            respuesta_estado_id, responsable, respuesta_fecha, en_uso, activo, creador, creacion,
            modificador, modificacion
        )
        VALUES (
            :requerimiento_recurso_id, :cantidad_asignada, :situacion_actual, :porcentaje_avance,
            :respuesta_estado_id, :responsable, :respuesta_fecha, :en_uso, :activo, :creador, :creacion,
            :modificador, :modificacion
        )
        RETURNING id
    """)

    result = db.session.execute(query, {
        'requerimiento_recurso_id': data['requerimiento_recurso_id'],
        'cantidad_asignada': data.get('cantidad_asignada', 1),
        'situacion_actual': data.get('situacion_actual'),
        'porcentaje_avance': data.get('porcentaje_avance', 0),
        'respuesta_estado_id': data['respuesta_estado_id'],
        'responsable': data.get('responsable'),
        'respuesta_fecha': data.get('respuesta_fecha', now),
        'en_uso': data.get('en_uso', 1),
        'activo': data.get('activo', True),
        'creador': data.get('creador', 'Sistema'),
        'creacion': now,
        'modificador': data.get('modificador', data.get('creador', 'Sistema')),
        'modificacion': data.get('modificacion', now)
    })

    row = result.fetchone()
    if row is None:
        db.session.rollback()
        return jsonify({'error': 'No se pudo crear la respuesta'}), 500

    respuesta_id = row[0]
    db.session.commit()

    respuesta = db.session.execute(
        db.text("SELECT * FROM requerimiento_respuestas WHERE id = :id"),
        {'id': respuesta_id}
    ).fetchone()
    if respuesta is None:
        return jsonify({'error': 'Respuesta no encontrada despues de crear'}), 500

    return jsonify(_serialize_requerimiento_respuesta(respuesta)), 201


@requerimiento_respuestas_bp.route('/api/requerimiento-respuestas/<int:requerimiento_recurso_id>', methods=['GET'])
def get_requerimiento_respuesta(requerimiento_recurso_id):
    """Obtener el historico de respuestas del recurso del requerimiento seleccionado
    ---
    tags:
      - Requerimiento Respuestas
    parameters:
      - name: requerimiento_recurso_id
        in: path
        type: integer
        required: true
    responses:
      200:
        description: Historico de respuestas de requerimiento
        schema:
          type: array
          items:
            type: object
            properties:
              id: {type: integer}
              requerimiento_recurso_id: {type: integer}
              cantidad_asignada: {type: integer}
              situacion_actual: {type: string}
              porcentaje_avance: {type: integer}
              respuesta_estado_id: {type: integer}
              respuesta_estado_nombre: {type: string}
              responsable: {type: string}
              respuesta_fecha: {type: string}
              en_uso: {type: integer}
              activo: {type: boolean}
      404:
        description: No encontrada
    """
    params = {'requerimiento_recurso_id': requerimiento_recurso_id}
    query = db.text("""
        SELECT r.id, r.requerimiento_recurso_id, r.cantidad_asignada, r.situacion_actual,
               r.porcentaje_avance, r.respuesta_estado_id, e.nombre AS respuesta_estado_nombre,
               r.responsable, r.respuesta_fecha, r.en_uso, r.activo
        FROM public.requerimiento_respuestas r
        INNER JOIN public.respuesta_estados e ON r.respuesta_estado_id = e.id
        WHERE r.requerimiento_recurso_id = :requerimiento_recurso_id
        ORDER BY r.id DESC
    """)
    result = db.session.execute(query, params)
    respuestas = []

    if not result:
        return jsonify({'error': 'Respuestas de requerimiento no encontradas'}), 404
    for row in result:
        respuestas.append({
            'id': row.id,
            'requerimiento_recurso_id': row.requerimiento_recurso_id,
            'cantidad_asignada': row.cantidad_asignada,
            'situacion_actual': row.situacion_actual,
            'porcentaje_avance': row.porcentaje_avance,
            'respuesta_estado_id': row.respuesta_estado_id,
            'respuesta_estado_nombre': row.respuesta_estado_nombre,
            'responsable': row.responsable,
            'respuesta_fecha': row.respuesta_fecha.isoformat() if row.respuesta_fecha else None,
            'en_uso': row.en_uso,
            'activo': row.activo
        })
    return jsonify(respuestas)


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
            requerimiento_recurso_id: {type: integer}
            cantidad_asignada: {type: integer}
            situacion_actual: {type: string}
            porcentaje_avance: {type: integer}
            respuesta_estado_id: {type: integer}
            responsable: {type: string}
            respuesta_fecha: {type: string}
            en_uso: {type: integer}
            activo: {type: boolean}
            modificador: {type: string}
            modificacion: {type: string}
    responses:
      200:
        description: Respuesta de requerimiento actualizada
      404:
        description: No encontrada
    """
    data = request.get_json() or {}
    now = datetime.now(timezone.utc)

    actual = db.session.execute(
        db.text("SELECT * FROM requerimiento_respuestas WHERE id = :id"),
        {'id': id}
    ).fetchone()
    if actual is None:
        return jsonify({'error': 'Respuesta no encontrada'}), 404

    params = {
        'id': id,
        'requerimiento_recurso_id': data.get('requerimiento_recurso_id', actual.requerimiento_recurso_id),
        'cantidad_asignada': data.get('cantidad_asignada', actual.cantidad_asignada),
        'situacion_actual': data.get('situacion_actual', actual.situacion_actual),
        'porcentaje_avance': data.get('porcentaje_avance', actual.porcentaje_avance),
        'respuesta_estado_id': data.get('respuesta_estado_id', actual.respuesta_estado_id),
        'responsable': data.get('responsable', actual.responsable),
        'respuesta_fecha': data.get('respuesta_fecha', actual.respuesta_fecha),
        'en_uso': data.get('en_uso', actual.en_uso),
        'activo': data.get('activo', actual.activo),
        'modificador': data.get('modificador', 'Sistema'),
        'modificacion': data.get('modificacion', now)
    }

    if _is_recurso_retorna(params['requerimiento_recurso_id']) and _is_estado_finalizado(
        params['respuesta_estado_id']
    ):
        params['en_uso'] = 0

    query = db.text("""
        UPDATE requerimiento_respuestas
        SET requerimiento_recurso_id = :requerimiento_recurso_id,
            cantidad_asignada = :cantidad_asignada,
            situacion_actual = :situacion_actual,
            porcentaje_avance = :porcentaje_avance,
            respuesta_estado_id = :respuesta_estado_id,
            responsable = :responsable,
            respuesta_fecha = :respuesta_fecha,
            en_uso = :en_uso,
            activo = :activo,
            modificador = :modificador,
            modificacion = :modificacion
        WHERE id = :id
    """)

    db.session.execute(query, params)
    db.session.commit()

    respuesta = db.session.execute(
        db.text("SELECT * FROM requerimiento_respuestas WHERE id = :id"),
        {'id': id}
    ).fetchone()
    if respuesta is None:
        return jsonify({'error': 'Respuesta no encontrada'}), 404

    return jsonify(_serialize_requerimiento_respuesta(respuesta))


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

    if getattr(result, 'rowcount', 0) == 0:
        return jsonify({'error': 'Respuesta no encontrada'}), 404

    db.session.commit()
    return jsonify({'mensaje': 'Respuesta eliminada correctamente'})
