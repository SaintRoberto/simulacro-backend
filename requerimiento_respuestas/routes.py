from flask import request, jsonify
from requerimiento_respuestas import requerimiento_respuestas_bp
from models import db
from datetime import datetime, timezone


def _is_estado_finalizado(respuesta_estado_id):
    return respuesta_estado_id == 3


def _is_recurso_retorna(recurso_inventario_id):
    row = db.session.execute(
        db.text("""
            SELECT COALESCE(rt.retorna, false) AS retorna
            FROM recursos_inventario ri
            INNER JOIN recurso_tipos rt ON ri.recurso_tipo_id = rt.id
            WHERE ri.id = :recurso_inventario_id
        """),
        {'recurso_inventario_id': recurso_inventario_id}
    ).fetchone()
    return bool(row.retorna) if row is not None else False


def _normalize_factor(value, default=1):
    if value is None:
        return default
    if isinstance(value, bool):
        return 1 if value else 0
    if isinstance(value, (int, float)):
        return 1 if int(value) != 0 else 0
    if isinstance(value, str):
        lowered = value.strip().lower()
        if lowered in ('true', 't', 'yes', 'y', 'si', '1'):
            return 1
        if lowered in ('false', 'f', 'no', 'n', '0'):
            return 0
        try:
            return 1 if int(lowered) != 0 else 0
        except ValueError:
            return default
    return default


def _resolve_factor_by_estado(recurso_inventario_id, respuesta_estado_id, factor):
    normalized_factor = _normalize_factor(factor, default=1)
    if _is_recurso_retorna(recurso_inventario_id) and _is_estado_finalizado(respuesta_estado_id):
        return 0
    return normalized_factor


def _serialize_requerimiento_respuesta(row):
    return {
        'id': row.id,
        'requerimiento_recurso_id': row.requerimiento_recurso_id,
        'recurso_inventario_id': row.recurso_inventario_id,
        'cantidad_asignada': row.cantidad_asignada,
        'situacion_actual': row.situacion_actual,
        'porcentaje_avance': row.porcentaje_avance,
        'respuesta_estado_id': row.respuesta_estado_id,
        'responsable': row.responsable,
        'respuesta_fecha': row.respuesta_fecha.isoformat() if row.respuesta_fecha else None,
        'factor': row.factor,
        'activo': row.activo,
        'creador': row.creador,
        'creacion': row.creacion.isoformat() if row.creacion else None,
        'modificador': row.modificador,
        'modificacion': row.modificacion.isoformat() if row.modificacion else None
    }


@requerimiento_respuestas_bp.route('/api/requerimiento-respuestas', methods=['GET'])
def get_requerimiento_respuestas():
    """Listar todas las respuestas de requerimientos.
    ---
    tags:
      - Requerimiento Respuestas
    summary: Listar respuestas de requerimientos
    description: Devuelve todas las respuestas registradas en `requerimiento_respuestas`, ordenadas por `id` descendente.
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
              recurso_inventario_id: {type: integer}
              cantidad_asignada: {type: integer}
              situacion_actual: {type: string}
              porcentaje_avance: {type: integer}
              respuesta_estado_id: {type: integer}
              responsable: {type: string}
              respuesta_fecha: {type: string}
              factor: {type: integer}
              activo: {type: boolean}
              creador: {type: string}
              creacion: {type: string}
              modificador: {type: string}
              modificacion: {type: string}
    """
    result = db.session.execute(db.text("SELECT * FROM requerimiento_respuestas ORDER BY id DESC"))
    return jsonify([_serialize_requerimiento_respuesta(row) for row in result])


@requerimiento_respuestas_bp.route('/api/requerimiento-respuestas/<int:id>', methods=['GET'])
def get_requerimiento_respuesta_by_id(id):
    """Obtener una respuesta de requerimiento por ID.
    ---
    tags:
      - Requerimiento Respuestas
    summary: Obtener respuesta por ID
    description: Devuelve una sola respuesta de requerimiento identificada por `id`.
    parameters:
      - name: id
        in: path
        type: integer
        required: true
    responses:
      200:
        description: Respuesta de requerimiento encontrada
        schema:
          type: object
          properties:
            id: {type: integer}
            requerimiento_recurso_id: {type: integer}
            recurso_inventario_id: {type: integer}
            cantidad_asignada: {type: integer}
            situacion_actual: {type: string}
            porcentaje_avance: {type: integer}
            respuesta_estado_id: {type: integer}
            responsable: {type: string}
            respuesta_fecha: {type: string}
            factor: {type: integer}
            activo: {type: boolean}
            creador: {type: string}
            creacion: {type: string}
            modificador: {type: string}
            modificacion: {type: string}
      404:
        description: Respuesta de requerimiento no encontrada
    """
    row = db.session.execute(
        db.text("SELECT * FROM requerimiento_respuestas WHERE id = :id"),
        {'id': id}
    ).fetchone()
    if row is None:
        return jsonify({'error': 'Respuesta de requerimiento no encontrada'}), 404
    return jsonify(_serialize_requerimiento_respuesta(row)) 


@requerimiento_respuestas_bp.route('/api/requerimiento-respuestas', methods=['POST'])
def create_requerimiento_respuesta():
    """Crear una nueva respuesta de requerimiento.
    ---
    tags:
      - Requerimiento Respuestas
    summary: Crear respuesta de requerimiento
    description: Inserta una respuesta de requerimiento. Si el recurso inventario retorna y el estado de la respuesta es finalizado, el campo `factor` se ajusta a `0`.
    consumes:
      - application/json
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          required: [requerimiento_recurso_id, recurso_inventario_id, respuesta_estado_id]
          properties:
            requerimiento_recurso_id: {type: integer}
            recurso_inventario_id: {type: integer}
            cantidad_asignada: {type: integer}
            situacion_actual: {type: string}
            porcentaje_avance: {type: integer}
            respuesta_estado_id: {type: integer}
            responsable: {type: string}
            respuesta_fecha: {type: string}
            factor: {type: integer}
            activo: {type: boolean}
            creador: {type: string}
            modificador: {type: string}
            modificacion: {type: string}
    responses:
      201:
        description: Respuesta de requerimiento creada correctamente
        schema:
          type: object
          properties:
            id: {type: integer}
            requerimiento_recurso_id: {type: integer}
            recurso_inventario_id: {type: integer}
            cantidad_asignada: {type: integer}
            situacion_actual: {type: string}
            porcentaje_avance: {type: integer}
            respuesta_estado_id: {type: integer}
            responsable: {type: string}
            respuesta_fecha: {type: string}
            factor: {type: integer}
            activo: {type: boolean}
            creador: {type: string}
            creacion: {type: string}
            modificador: {type: string}
            modificacion: {type: string}
      400:
        description: Campos requeridos faltantes o datos inválidos
      500:
        description: Error inesperado al crear la respuesta
    """
    data = request.get_json() or {}
    required_fields = ['requerimiento_recurso_id', 'recurso_inventario_id', 'respuesta_estado_id']
    missing_fields = [field for field in required_fields if field not in data]
    if missing_fields:
        return jsonify({'error': f"Campos requeridos faltantes: {', '.join(missing_fields)}"}), 400

    now = datetime.now(timezone.utc)
    factor = _resolve_factor_by_estado(
        data['recurso_inventario_id'],
        data['respuesta_estado_id'],
        data.get('factor', 1)
    )

    query = db.text("""
        INSERT INTO requerimiento_respuestas (
            requerimiento_recurso_id, recurso_inventario_id, cantidad_asignada, situacion_actual, porcentaje_avance,
            respuesta_estado_id, responsable, respuesta_fecha, factor, activo, creador, creacion,
            modificador, modificacion
        )
        VALUES (
            :requerimiento_recurso_id, :recurso_inventario_id, :cantidad_asignada, :situacion_actual, :porcentaje_avance,
            :respuesta_estado_id, :responsable, :respuesta_fecha, :factor, :activo, :creador, :creacion,
            :modificador, :modificacion
        )
        RETURNING id
    """)

    result = db.session.execute(query, {
        'requerimiento_recurso_id': data['requerimiento_recurso_id'],
        'recurso_inventario_id': data['recurso_inventario_id'],
        'cantidad_asignada': data.get('cantidad_asignada', 1),
        'situacion_actual': data.get('situacion_actual'),
        'porcentaje_avance': data.get('porcentaje_avance', 0),
        'respuesta_estado_id': data['respuesta_estado_id'],
        'responsable': data.get('responsable'),
        'respuesta_fecha': data.get('respuesta_fecha', now),
        'factor': factor,
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
    """Obtener el histórico de respuestas de un requerimiento recurso.
    ---
    tags:
      - Requerimiento Respuestas
    summary: Obtener historial de respuestas
    description: Devuelve todas las respuestas asociadas a `requerimiento_recurso_id`, ordenadas por `id` descendente.
    parameters:
      - name: requerimiento_recurso_id
        in: path
        type: integer
        required: true
    responses:
      200:
        description: Histórico de respuestas de requerimiento
        schema:
          type: array
          items:
            type: object
            properties:
              id: {type: integer}
              requerimiento_recurso_id: {type: integer}
              recurso_inventario_id: {type: integer}
              cantidad_asignada: {type: integer}
              situacion_actual: {type: string}
              porcentaje_avance: {type: integer}
              respuesta_estado_id: {type: integer}
              respuesta_estado_nombre: {type: string}
              responsable: {type: string}
              respuesta_fecha: {type: string}
              factor: {type: integer}
              activo: {type: boolean}
      404:
        description: Respuesta de requerimiento no encontrada
    """
    params = {'requerimiento_recurso_id': requerimiento_recurso_id}
    query = db.text("""
        SELECT r.id, r.requerimiento_recurso_id, r.recurso_inventario_id, r.cantidad_asignada, r.situacion_actual,
               r.porcentaje_avance, r.respuesta_estado_id, e.nombre AS respuesta_estado_nombre,
               r.responsable, r.respuesta_fecha, r.factor, r.activo
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
            'recurso_inventario_id': row.recurso_inventario_id,
            'cantidad_asignada': row.cantidad_asignada,
            'situacion_actual': row.situacion_actual,
            'porcentaje_avance': row.porcentaje_avance,
            'respuesta_estado_id': row.respuesta_estado_id,
            'respuesta_estado_nombre': row.respuesta_estado_nombre,
            'responsable': row.responsable,
            'respuesta_fecha': row.respuesta_fecha.isoformat() if row.respuesta_fecha else None,
            'factor': row.factor,
            'activo': row.activo
        })
    return jsonify(respuestas)


@requerimiento_respuestas_bp.route('/api/requerimiento-respuestas/<int:id>', methods=['PUT'])
def update_requerimiento_respuesta(id):
    """Actualizar completamente una respuesta de requerimiento.
    ---
    tags:
      - Requerimiento Respuestas
    summary: Actualizar respuesta de requerimiento
    description: Actualiza una respuesta de requerimiento por `id`. Si el recurso inventario retorna y el estado finaliza, el campo `factor` se ajusta a `0`.
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
            recurso_inventario_id: {type: integer}
            cantidad_asignada: {type: integer}
            situacion_actual: {type: string}
            porcentaje_avance: {type: integer}
            respuesta_estado_id: {type: integer}
            responsable: {type: string}
            respuesta_fecha: {type: string}
            factor: {type: integer}
            activo: {type: boolean}
            modificador: {type: string}
            modificacion: {type: string}
    responses:
      200:
        description: Respuesta de requerimiento actualizada correctamente
      404:
        description: Respuesta de requerimiento no encontrada
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
        'recurso_inventario_id': data.get('recurso_inventario_id', actual.recurso_inventario_id),
        'cantidad_asignada': data.get('cantidad_asignada', actual.cantidad_asignada),
        'situacion_actual': data.get('situacion_actual', actual.situacion_actual),
        'porcentaje_avance': data.get('porcentaje_avance', actual.porcentaje_avance),
        'respuesta_estado_id': data.get('respuesta_estado_id', actual.respuesta_estado_id),
        'responsable': data.get('responsable', actual.responsable),
        'respuesta_fecha': data.get('respuesta_fecha', actual.respuesta_fecha),
        'factor': data.get('factor', actual.factor),
        'activo': data.get('activo', actual.activo),
        'modificador': data.get('modificador', 'Sistema'),
        'modificacion': data.get('modificacion', now)
    }

    params['factor'] = _resolve_factor_by_estado(
        params['recurso_inventario_id'],
        params['respuesta_estado_id'],
        params['factor']
    )

    query = db.text("""
        UPDATE requerimiento_respuestas
        SET requerimiento_recurso_id = :requerimiento_recurso_id,
            recurso_inventario_id = :recurso_inventario_id,
            cantidad_asignada = :cantidad_asignada,
            situacion_actual = :situacion_actual,
            porcentaje_avance = :porcentaje_avance,
            respuesta_estado_id = :respuesta_estado_id,
            responsable = :responsable,
            respuesta_fecha = :respuesta_fecha,
            factor = :factor,
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


@requerimiento_respuestas_bp.route(
    '/api/requerimiento-respuestas/<int:requerimiento_respuesta_id>/libera-inventario/<int:recurso_inventario_id>',
    methods=['PATCH']
)
def patch_libera_inventario_by_requerimiento_respuesta_id_by_recurso_inventario_id(
    requerimiento_respuesta_id,
    recurso_inventario_id,
):
    """Liberar inventario asociado a una respuesta de requerimiento.
    ---
    tags:
      - Requerimiento Respuestas
    summary: Liberar inventario de una respuesta
    description: Consulta si el recurso inventario retorna. Si `retorna = true`, deja `factor = 0` en la respuesta indicada. Si `retorna = false`, no modifica el registro.
    parameters:
      - name: requerimiento_respuesta_id
        in: path
        type: integer
        required: true
      - name: recurso_inventario_id
        in: path
        type: integer
        required: true
    responses:
      200:
        description: Inventario liberado o sin cambios
        schema:
          type: object
          properties:
            id: {type: integer}
            requerimiento_recurso_id: {type: integer}
            recurso_inventario_id: {type: integer}
            factor: {type: integer}
            inventario_liberado: {type: boolean}
      404:
        description: Respuesta no encontrada
      400:
        description: El recurso_inventario_id no coincide con la respuesta indicada
    """
    actual = db.session.execute(
        db.text("""
            SELECT id, recurso_inventario_id, factor
            FROM requerimiento_respuestas
            WHERE id = :requerimiento_respuesta_id
        """),
        {'requerimiento_respuesta_id': requerimiento_respuesta_id}
    ).fetchone()
    if actual is None:
        return jsonify({'error': 'Respuesta no encontrada'}), 404

    if actual.recurso_inventario_id != recurso_inventario_id:
        return jsonify({
            'error': 'El recurso_inventario_id no coincide con la respuesta indicada'
        }), 400

    retorna_row = db.session.execute(
        db.text("""
            SELECT COALESCE(rt.retorna, false) AS retorna
            FROM recursos_inventario ri
            INNER JOIN recurso_tipos rt ON ri.recurso_tipo_id = rt.id
            WHERE ri.id = :recurso_inventario_id
        """),
        {'recurso_inventario_id': recurso_inventario_id}
    ).fetchone()
    retorna = bool(retorna_row.retorna) if retorna_row is not None else False

    if retorna and actual.factor != 0:
        now = datetime.now(timezone.utc)
        db.session.execute(
            db.text("""
                UPDATE requerimiento_respuestas
                SET factor = 0,
                    modificacion = :modificacion
                WHERE id = :requerimiento_respuesta_id
            """),
            {
                'requerimiento_respuesta_id': requerimiento_respuesta_id,
                'modificacion': now
            }
        )
        db.session.commit()

    respuesta = db.session.execute(
        db.text("SELECT * FROM requerimiento_respuestas WHERE id = :requerimiento_respuesta_id"),
        {'requerimiento_respuesta_id': requerimiento_respuesta_id}
    ).fetchone()
    if respuesta is None:
        return jsonify({'error': 'Respuesta no encontrada despues de actualizar'}), 500

    return jsonify({
        'id': respuesta.id,
        'requerimiento_recurso_id': respuesta.requerimiento_recurso_id,
        'recurso_inventario_id': respuesta.recurso_inventario_id,
        'factor': respuesta.factor,
        'inventario_liberado': retorna and respuesta.factor == 0
    }), 200


@requerimiento_respuestas_bp.route('/api/requerimiento-respuestas/<int:id>', methods=['DELETE'])
def delete_requerimiento_respuesta(id):
    """Eliminar una respuesta de requerimiento.
    ---
    tags:
      - Requerimiento Respuestas
    summary: Eliminar respuesta de requerimiento
    description: Elimina físicamente una respuesta de requerimiento por `id`.
    parameters:
      - name: id
        in: path
        type: integer
        required: true
    responses:
      200:
        description: Respuesta eliminada correctamente
      404:
        description: Respuesta de requerimiento no encontrada
    """
    result = db.session.execute(
        db.text("DELETE FROM requerimiento_respuestas WHERE id = :id"),
        {'id': id}
    )

    if getattr(result, 'rowcount', 0) == 0:
        return jsonify({'error': 'Respuesta no encontrada'}), 404

    db.session.commit()
    return jsonify({'mensaje': 'Respuesta eliminada correctamente'})


@requerimiento_respuestas_bp.route('/api/requerimiento-respuesta/<int:id>/requerimiento-recurso/<int:requerimiento_recurso_id>', methods=['PATCH'])
def patch_requerimiento_respuesta_cantidad(id, requerimiento_recurso_id):
    """Actualizar cantidad asignada de respuesta de requerimiento
    ---
    tags:
      - Requerimiento Respuestas
    parameters:
      - name: id
        in: path
        type: integer
        required: true      
      - name: requerimiento_recurso_id
        in: path
        type: integer
        required: true
      - in: body
        name: body
        required: true
        schema:
          type: object
          required: [cantidad_asignadal]
          properties:
            cantidad_asignada: {type: integer}
            
    responses:
      200:
        description: Cantidad actualizada
      404:
        description: No encontrada
    """
    data = request.get_json() or {}
    if 'cantidad_asignada' not in data:
        return jsonify({'error': 'Campo cantidad_asignada es requerido'}), 400

    result = db.session.execute(
        db.text("""
            UPDATE requerimiento_respuestas
            SET cantidad_asignada = :cantidad_asignada
            WHERE requerimiento_recurso_id = :requerimiento_recurso_id
            AND id = :id
        """),
        {'cantidad_asignada': data['cantidad_asignada'], 'requerimiento_recurso_id': requerimiento_recurso_id, 'id': id}
    )

    if getattr(result, 'rowcount', 0) == 0:
        return jsonify({'error': 'Respuesta no encontrada para el requerimiento_recurso_id dado'}), 404

    db.session.commit()
    return jsonify({'mensaje': 'Cantidad asignada actualizada correctamente'})