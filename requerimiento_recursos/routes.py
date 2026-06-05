from flask import request, jsonify, g
from requerimiento_recursos import requerimiento_recursos_bp
from models import db
from datetime import datetime, timezone


def _requerimiento_estado_existe(requerimiento_estado_id):
    estado = db.session.execute(
        db.text("""
            SELECT id
            FROM requerimiento_estados
            WHERE id = :id
        """),
        {'id': requerimiento_estado_id}
    ).fetchone()
    return estado is not None


def _serialize_requerimiento_recurso(row):
    row_mapping = getattr(row, '_mapping', {})

    def _get_optional(column_name):
        if column_name in row_mapping:
            return row_mapping[column_name]
        upper_column_name = column_name.upper()
        if upper_column_name in row_mapping:
            return row_mapping[upper_column_name]
        return None

    return {
        'id': row.id,
        'requerimiento_numero': row.requerimiento_numero,
        'requerimiento_id': row.requerimiento_id,
        'requerimiento_estado_id': row.requerimiento_estado_id,
        'usuario_receptor_id': row.usuario_receptor_id,
        "usuario_receptor": _get_optional('usuario_receptor'),
        'recurso_grupo_id': row.recurso_grupo_id,
        'grupo_recurso': _get_optional('grupo_recurso'),
        'recurso_tipo_id': row.recurso_tipo_id,
        'cantidad_solicitada': row.cantidad_solicitada,
        'costo': _to_float_optional(row.costo),
        'porcentaje_avance': getattr(row, 'porcentaje_avance', None),
        'especificaciones': row.especificaciones,
        'destino': row.destino,
        'detalle': row.detalle,
        'activo': row.activo,
        'creador': row.creador,
        'creacion': _to_iso_optional(row.creacion),
        'modificador': row.modificador,
        'modificacion': _to_iso_optional(row.modificacion),
        "usuario_emisor_id": row.usuario_emisor_id,
        "usuario_emisor": _get_optional('usuario_emisor'),
    }


def _resolve_authenticated_user():
    user = getattr(g, 'user', None)
    if not isinstance(user, dict):
        return None
    return user.get('usuario') or user.get('username') or user.get('user') or user.get('email')


def _to_float_optional(value):
    if value is None or value == '':
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        if isinstance(value, str):
            normalized_value = value.strip().replace(',', '.')
            if not normalized_value:
                return None
            try:
                return float(normalized_value)
            except (TypeError, ValueError):
                return None
        return None


def _to_iso_optional(value):
    if value is None or value == '':
        return None
    if hasattr(value, 'isoformat'):
        return value.isoformat()
    return str(value)


@requerimiento_recursos_bp.route('/api/requerimiento-recursos', methods=['GET'])
def get_requerimiento_recursos():
    """Listar todos los requerimientos de recursos.
    ---
    tags:
      - Requerimiento Recursos
    summary: Listar requerimientos de recursos
    description: Devuelve todos los registros de `requerimiento_recursos` ordenados por `id` descendente.
    responses:
      200:
        description: Lista de requerimiento recursos
        schema:
          type: array
          items:
            type: object
            properties:
              id: {type: integer}
              requerimiento_numero: {type: string}
              requerimiento_id: {type: integer}
              requerimiento_estado_id: {type: integer}
              usuario_receptor_id: {type: integer}
              recurso_grupo_id: {type: integer}
              recurso_tipo_id: {type: integer}
              cantidad_solicitada: {type: integer}
              costo: {type: number}
              especificaciones: {type: string}
              destino: {type: string}
              detalle: {type: string}
              activo: {type: boolean}
              creador: {type: string}
              creacion: {type: string}
              modificador: {type: string}
              modificacion: {type: string}
    """
    result = db.session.execute(db.text("SELECT * FROM requerimiento_recursos ORDER BY id DESC"))
    return jsonify([_serialize_requerimiento_recurso(row) for row in result])


@requerimiento_recursos_bp.route('/api/requerimiento-recursos', methods=['POST'])
def create_requerimiento_recurso():
    """Crear un requerimiento de recurso.
    ---
    tags:
      - Requerimiento Recursos
    summary: Crear requerimiento de recurso
    description: Inserta un nuevo requerimiento de recurso con los datos enviados en el cuerpo de la solicitud.
    consumes:
      - application/json
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          required: [requerimiento_id, usuario_receptor_id, recurso_grupo_id, recurso_tipo_id, requerimiento_estado_id, usuario_emisor_id]
          properties:
            requerimiento_numero: {type: string}
            requerimiento_id: {type: integer}
            requerimiento_estado_id: {type: integer}
            usuario_receptor_id: {type: integer}
            recurso_grupo_id: {type: integer}
            recurso_tipo_id: {type: integer}
            cantidad_solicitada: {type: integer}
            costo: {type: number}
            especificaciones: {type: string}
            destino: {type: string}
            detalle: {type: string}
            activo: {type: boolean}
            creador: {type: string}
            usuario_emisor_id: {type: integer}
    responses:
      201:
        description: Requerimiento de recurso creado correctamente
      400:
        description: Campos requeridos faltantes o requerimiento_estado_id inválido
      500:
        description: Error inesperado al crear el requerimiento
    """
    data = request.get_json() or {}
    required_fields = [
        'requerimiento_id',
        'usuario_receptor_id',
        'recurso_grupo_id',
        'recurso_tipo_id',
        'requerimiento_estado_id',
        'requerimiento_numero',
        'usuario_emisor_id'
    ]
    missing_fields = [field for field in required_fields if field not in data or data[field] is None]
    if missing_fields:
        return jsonify({'error': f"Campos requeridos faltantes: {', '.join(missing_fields)}"}), 400

    if not _requerimiento_estado_existe(data['requerimiento_estado_id']):
        return jsonify({'error': 'requerimiento_estado_id no existe en requerimiento_estados'}), 400

    now = datetime.now(timezone.utc)

    query = db.text("""
        INSERT INTO requerimiento_recursos (
            requerimiento_numero, requerimiento_id, usuario_receptor_id, recurso_grupo_id, recurso_tipo_id,
            cantidad_solicitada, costo, requerimiento_estado_id,
            especificaciones, destino, detalle, activo, creador, creacion, modificador, modificacion, usuario_emisor_id
        )
        VALUES (
            :requerimiento_numero, :requerimiento_id, :usuario_receptor_id, :recurso_grupo_id, :recurso_tipo_id,
            :cantidad_solicitada, :costo, :requerimiento_estado_id,
            :especificaciones, :destino, :detalle, :activo, :creador, :creacion, :modificador, :modificacion, :usuario_emisor_id
        )
        RETURNING id
    """)

    result = db.session.execute(query, {
        'requerimiento_numero': data.get('requerimiento_numero'),
        'requerimiento_id': data['requerimiento_id'],
        'usuario_receptor_id': data['usuario_receptor_id'],
        'recurso_grupo_id': data['recurso_grupo_id'],
        'recurso_tipo_id': data['recurso_tipo_id'],
        'cantidad_solicitada': data.get('cantidad_solicitada', data.get('cantidad', 1)),
        'costo': data.get('costo', 0),
        'requerimiento_estado_id': data['requerimiento_estado_id'],
        'especificaciones': data.get('especificaciones'),
        'destino': data.get('destino'),
        'detalle': data.get('detalle'),
        'activo': data.get('activo', True),
        'creador': data.get('creador', 'Sistema'),
        'creacion': now,
        'modificador': data.get('modificador', data.get('creador', 'Sistema')),
        'modificacion': data.get('modificacion'),
        'usuario_emisor_id': data['usuario_emisor_id']
    })

    row = result.fetchone()
    if row is None:
        db.session.rollback()
        return jsonify({'error': 'No se pudo crear el registro'}), 500

    relacion_id = row[0]
    db.session.commit()

    relacion = db.session.execute(
        db.text("SELECT * FROM requerimiento_recursos WHERE id = :id"),
        {'id': relacion_id}
    ).fetchone()
    if relacion is None:
        return jsonify({'error': 'Registro no encontrado despues de crear'}), 500

    return jsonify(_serialize_requerimiento_recurso(relacion)), 201


@requerimiento_recursos_bp.route('/api/requerimiento-recursos/<int:requerimiento_id>', methods=['GET'])
def get_requerimiento_recursos_by_requerimiento_id(requerimiento_id):
    """Obtener requerimientos de recursos por `requerimiento_id`.
    ---
    tags:
      - Requerimiento Recursos
    summary: Obtener requerimientos por requerimiento_id
    description: Devuelve todos los requerimientos asociados al identificador de requerimiento indicado.
    parameters:
      - name: requerimiento_id
        in: path
        type: integer
        required: true
    responses:
      200:
        description: Lista de requerimientos de recursos
      404:
        description: No se encontraron requerimientos para el `requerimiento_id` indicado
    """
    result = db.session.execute(
        db.text("""
            SELECT * FROM requerimiento_recursos
            WHERE requerimiento_id = :requerimiento_id
            ORDER BY id DESC
        """),
        {'requerimiento_id': requerimiento_id}
    )
    return jsonify([_serialize_requerimiento_recurso(row) for row in result])


@requerimiento_recursos_bp.route(
    '/api/requerimiento-recursos/usuario-receptor/<int:usuario_receptor_id>',
    methods=['GET']
)
def get_requerimiento_recursos_by_usuario_receptor(usuario_receptor_id):
    """Obtener requerimientos de recursos por usuario receptor.
    ---
    tags:
      - Requerimiento Recursos
    summary: Obtener requerimientos por usuario receptor
    description: Devuelve los requerimientos asignados al usuario receptor indicado.
    parameters:
      - name: usuario_receptor_id
        in: path
        type: integer
        required: true
        description: ID del usuario que inicia sesion
    responses:
      200:
        description: Lista de requerimientos recursos del usuario receptor
        schema:
          type: array
          items:
            type: object
            properties:
              id: {type: integer}
              requerimiento_numero: {type: string}
              requerimiento_id: {type: integer}
              requerimiento_estado_id: {type: integer}
              usuario_receptor_id: {type: integer}
              recurso_grupo_id: {type: integer}
              recurso_tipo_id: {type: integer}
              cantidad_solicitada: {type: integer}
              costo: {type: number}
              especificaciones: {type: string}
              destino: {type: string}
              detalle: {type: string}
              activo: {type: boolean}
              creador: {type: string}
              creacion: {type: string}
              modificador: {type: string}
              modificacion: {type: string}
              grupo_recurso: {type: string}
    """
    result = db.session.execute(
        db.text("""
                SELECT
                    RR.*,
                    G.NOMBRE AS GRUPO_RECURSO
                FROM
                    REQUERIMIENTO_RECURSOS RR
                    INNER JOIN RECURSO_GRUPOS G ON RR.RECURSO_GRUPO_ID = G.ID
                WHERE
                    RR.USUARIO_RECEPTOR_ID = :usuario_receptor_id
                    AND COALESCE(RR.ACTIVO, TRUE) = TRUE
                    AND RR.REQUERIMIENTO_ESTADO_ID <> 4
                ORDER BY
                    RR.ID DESC            
        """),
        {'usuario_receptor_id': usuario_receptor_id}
    )
    return jsonify([_serialize_requerimiento_recurso(row) for row in result])


@requerimiento_recursos_bp.route('/api/requerimiento-recursos/id/<int:id>', methods=['GET'])
def get_requerimiento_recurso(id):
    """Obtener un requerimiento de recurso por ID.
    ---
    tags:
      - Requerimiento Recursos
    summary: Obtener requerimiento por ID
    description: Devuelve el requerimiento de recurso identificado por `id`.
    parameters:
      - name: id
        in: path
        type: integer
        required: true
    responses:
      200:
        description: Requerimiento recurso
      404:
        description: No encontrado
    """
    relacion = db.session.execute(
        db.text("SELECT * FROM requerimiento_recursos WHERE id = :id"),
        {'id': id}
    ).fetchone()

    if not relacion:
        return jsonify({'error': 'Relacion no encontrada'}), 404

    return jsonify(_serialize_requerimiento_recurso(relacion))


@requerimiento_recursos_bp.route(
    '/api/requerimiento-recursos/recurso-inventario/<int:recurso_inventario_id>/pendiente',
    methods=['GET']
)
def get_recurso_inventario_pendiente(recurso_inventario_id):
    """Obtener la cantidad pendiente por despachar de un recurso de inventario.
    ---
    tags:
      - Requerimiento Recursos
    summary: Obtener cantidad pendiente por despachar
    description: Calcula la cantidad de un recurso de inventario que aún está pendiente por despachar.
    parameters:
      - name: recurso_inventario_id
        in: path
        type: integer
        required: true
        description: ID del recurso inventario
    responses:
      200:
        description: Cantidad pendiente por despachar del recurso inventario
        schema:
          type: object
          properties:
            recurso_inventario_id: {type: integer}
            recurso_tipo_id: {type: integer}
            cantidad_solicitada: {type: integer}
            cantidad_despachada: {type: integer}
            cantidad_pendiente: {type: integer}
      404:
        description: Recurso inventario no encontrado
    """
    query = db.text("""
        SELECT
            ri.id AS recurso_inventario_id,
            ri.recurso_tipo_id AS recurso_tipo_id,
            COALESCE(req.total_cantidad_solicitada, 0) AS cantidad_solicitada,
            COALESCE(resp.total_cantidad_despachada, 0) AS cantidad_despachada,
            COALESCE(req.total_cantidad_solicitada, 0) - COALESCE(resp.total_cantidad_despachada, 0) AS cantidad_pendiente
        FROM public.recursos_inventario ri
        LEFT JOIN (
            SELECT
                rr.recurso_tipo_id,
                COALESCE(SUM(COALESCE(rr.cantidad_solicitada, 0)), 0) AS total_cantidad_solicitada
            FROM public.requerimiento_recursos rr
            WHERE COALESCE(rr.activo, true) = true
            GROUP BY rr.recurso_tipo_id
        ) req ON req.recurso_tipo_id = ri.recurso_tipo_id
        LEFT JOIN (
            SELECT
                rresp.recurso_inventario_id,
                COALESCE(SUM(COALESCE(rresp.cantidad_asignada, 0) * COALESCE(rresp.factor, 1)), 0) AS total_cantidad_despachada
            FROM public.requerimiento_respuestas rresp
            WHERE COALESCE(rresp.activo, true) = true
            GROUP BY rresp.recurso_inventario_id
        ) resp ON resp.recurso_inventario_id = ri.id
        WHERE ri.id = :recurso_inventario_id
          AND COALESCE(ri.activo, true) = true
    """)
    row = db.session.execute(query, {'recurso_inventario_id': recurso_inventario_id}).fetchone()

    if row is None:
        return jsonify({'error': 'Recurso inventario no encontrado'}), 404

    return jsonify({
        'recurso_inventario_id': row.recurso_inventario_id,
        'recurso_tipo_id': row.recurso_tipo_id,
        'cantidad_solicitada': row.cantidad_solicitada,
        'cantidad_despachada': row.cantidad_despachada,
        'cantidad_pendiente': row.cantidad_pendiente
    })


@requerimiento_recursos_bp.route('/api/requerimiento-recursos/<int:id>', methods=['PUT'])
def update_requerimiento_recurso(id):
    """Actualizar un requerimiento de recurso.
    ---
    tags:
      - Requerimiento Recursos
    summary: Actualizar requerimiento de recurso
    description: Actualiza los campos editables de un requerimiento de recurso por `id`.
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
            requerimiento_numero: {type: string}
            requerimiento_id: {type: integer}
            requerimiento_estado_id: {type: integer}
            usuario_receptor_id: {type: integer}
            recurso_grupo_id: {type: integer}
            recurso_tipo_id: {type: integer}
            cantidad_solicitada: {type: integer}
            costo: {type: number}
            especificaciones: {type: string}
            destino: {type: string}
            detalle: {type: string}
            activo: {type: boolean}
            modificador: {type: string}
            modificacion: {type: string}
    responses:
      200:
        description: Requerimiento de recurso actualizado correctamente
      400:
        description: Campos inválidos o requerimiento_estado_id inexistente
      404:
        description: Requerimiento de recurso no encontrado
      500:
        description: Error inesperado al actualizar el requerimiento
    """
    data = request.get_json() or {}
    now = datetime.now(timezone.utc)

    actual = db.session.execute(
        db.text("SELECT * FROM requerimiento_recursos WHERE id = :id"),
        {'id': id}
    ).fetchone()
    if actual is None:
        return jsonify({'error': 'Relacion no encontrada'}), 404

    if 'requerimiento_estado_id' in data:
        if data['requerimiento_estado_id'] is None:
            return jsonify({'error': 'requerimiento_estado_id no puede ser null'}), 400
        if not _requerimiento_estado_existe(data['requerimiento_estado_id']):
            return jsonify({'error': 'requerimiento_estado_id no existe en requerimiento_estados'}), 400

    params = {
        'id': id,
        'requerimiento_numero': data.get('requerimiento_numero', actual.requerimiento_numero),
        'requerimiento_id': data.get('requerimiento_id', actual.requerimiento_id),
        'requerimiento_estado_id': data.get('requerimiento_estado_id', actual.requerimiento_estado_id),
        'usuario_receptor_id': data.get('usuario_receptor_id', actual.usuario_receptor_id),
        'recurso_grupo_id': data.get('recurso_grupo_id', actual.recurso_grupo_id),
        'recurso_tipo_id': data.get('recurso_tipo_id', actual.recurso_tipo_id),
        'cantidad_solicitada': data.get('cantidad_solicitada', data.get('cantidad', actual.cantidad_solicitada)),
        'costo': data.get('costo', actual.costo),
        'especificaciones': data.get('especificaciones', actual.especificaciones),
        'destino': data.get('destino', actual.destino),
        'detalle': data.get('detalle', actual.detalle),
        'activo': data.get('activo', actual.activo),
        'modificador': data.get('modificador', 'Sistema'),
        'modificacion': data.get('modificacion', now),
        'usuario_emisor_id': data.get('usuario_emisor_id', actual.usuario_emisor_id)
    }

    query = db.text("""
        UPDATE requerimiento_recursos
        SET requerimiento_numero = :requerimiento_numero,
            requerimiento_id = :requerimiento_id,
            requerimiento_estado_id = :requerimiento_estado_id,
            usuario_receptor_id = :usuario_receptor_id,
            recurso_grupo_id = :recurso_grupo_id,
            recurso_tipo_id = :recurso_tipo_id,
            cantidad_solicitada = :cantidad_solicitada,
            costo = :costo,
            especificaciones = :especificaciones,
            destino = :destino,
            detalle = :detalle,
            activo = :activo,
            modificador = :modificador,
            modificacion = :modificacion,
            usuario_emisor_id = :usuario_emisor_id
        WHERE id = :id
    """)

    db.session.execute(query, params)
    db.session.commit()

    relacion = db.session.execute(
        db.text("SELECT * FROM requerimiento_recursos WHERE id = :id"),
        {'id': id}
    ).fetchone()
    if relacion is None:
        return jsonify({'error': 'Relacion no encontrada despues de actualizar'}), 500

    return jsonify(_serialize_requerimiento_recurso(relacion))


@requerimiento_recursos_bp.route('/api/requerimiento-recursos/<int:id>', methods=['PATCH'])
def patch_requerimiento_recurso_estado(id):
    """Actualizar parcialmente el estado de un requerimiento de recurso.
    ---
    tags:
      - Requerimiento Recursos
    summary: Actualizar estado de requerimiento
    description: Cambia únicamente el estado del requerimiento y registra auditoría de modificación.
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
          required: [requerimiento_estado_id]
          properties:
            requerimiento_estado_id: {type: integer}
    responses:
      200:
        description: Estado de requerimiento actualizado correctamente
      400:
        description: Payload inválido o estado no permitido
      404:
        description: Requerimiento de recurso no encontrado
      409:
        description: Transicion de estado no permitida
      500:
        description: Error inesperado
    """
    try:
        data = request.get_json(silent=True)
        if not isinstance(data, dict):
            return jsonify({'error': 'Payload invalido, se esperaba un objeto JSON'}), 400

        allowed_fields = {'requerimiento_estado_id', 'modificador'}
        unexpected_fields = [field for field in data.keys() if field not in allowed_fields]
        if unexpected_fields:
            return jsonify({
                'error': f"Campos no permitidos para PATCH: {', '.join(unexpected_fields)}"
            }), 400

        if 'requerimiento_estado_id' not in data:
            return jsonify({'error': 'requerimiento_estado_id es requerido'}), 400

        new_estado = data.get('requerimiento_estado_id')
        if new_estado is None:
            return jsonify({'error': 'requerimiento_estado_id no puede ser null'}), 400
        if not isinstance(new_estado, int) or isinstance(new_estado, bool):
            return jsonify({'error': 'requerimiento_estado_id debe ser entero'}), 400
        if not _requerimiento_estado_existe(new_estado):
            return jsonify({'error': 'requerimiento_estado_id no existe en requerimiento_estados'}), 400

        actual = db.session.execute(
            db.text("""
                SELECT id, requerimiento_estado_id, modificador, modificacion
                FROM requerimiento_recursos
                WHERE id = :id
            """),
            {'id': id}
        ).fetchone()

        if actual is None:
            return jsonify({'error': 'Relacion no encontrada'}), 404

        now = datetime.now(timezone.utc)
        auth_user = _resolve_authenticated_user()
        modificador = auth_user or data.get('modificador') or actual.modificador or 'Sistema'

        db.session.execute(
            db.text("""
                UPDATE requerimiento_recursos
                SET requerimiento_estado_id = :requerimiento_estado_id,
                    modificacion = :modificacion,
                    modificador = :modificador
                WHERE id = :id
            """),
            {
                'id': id,
                'requerimiento_estado_id': new_estado,
                'modificacion': now,
                'modificador': modificador
            }
        )
        db.session.commit()

        updated = db.session.execute(
            db.text("""
                SELECT id, requerimiento_estado_id, modificacion, modificador
                FROM requerimiento_recursos
                WHERE id = :id
            """),
            {'id': id}
        ).fetchone()
        if updated is None:
            return jsonify({'error': 'Relacion no encontrada despues de actualizar'}), 500

        return jsonify({
            'id': updated.id,
            'requerimiento_estado_id': updated.requerimiento_estado_id,
            'modificacion': _to_iso_optional(updated.modificacion),
            'modificador': updated.modificador
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Error inesperado al actualizar estado', 'details': str(e)}), 500


@requerimiento_recursos_bp.route('/api/requerimiento-recursos/<int:id>/actualiza-estado-requerimiento', methods=['PATCH'])
def patch_actualiza_estado_requerimiento(id):
    """Actualizar el estado y el porcentaje de avance de un requerimiento.
    ---
    tags:
      - Requerimiento Recursos
    summary: Actualizar estado y avance
    description: Actualiza `requerimiento_estado_id` y `porcentaje_avance` del requerimiento, dejando trazabilidad de modificación.
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
          required: [requerimiento_estado_id, porcentaje_avance]
          properties:
            requerimiento_estado_id: {type: integer}
            porcentaje_avance: {type: integer}
            modificador: {type: string}
    responses:
      200:
        description: Estado y porcentaje de avance actualizados correctamente
      400:
        description: Payload inválido o datos fuera de rango
      404:
        description: Requerimiento de recurso no encontrado
      500:
        description: Error inesperado
    """
    try:
        data = request.get_json(silent=True)
        if not isinstance(data, dict):
            return jsonify({'error': 'Payload invalido, se esperaba un objeto JSON'}), 400

        allowed_fields = {'requerimiento_estado_id', 'porcentaje_avance', 'modificador'}
        unexpected_fields = [field for field in data.keys() if field not in allowed_fields]
        if unexpected_fields:
            return jsonify({
                'error': f"Campos no permitidos para PATCH: {', '.join(unexpected_fields)}"
            }), 400

        missing_fields = [field for field in ('requerimiento_estado_id', 'porcentaje_avance') if field not in data]
        if missing_fields:
            return jsonify({'error': f"Campos requeridos faltantes: {', '.join(missing_fields)}"}), 400

        new_estado = data.get('requerimiento_estado_id')
        if new_estado is None:
            return jsonify({'error': 'requerimiento_estado_id no puede ser null'}), 400
        if not isinstance(new_estado, int) or isinstance(new_estado, bool):
            return jsonify({'error': 'requerimiento_estado_id debe ser entero'}), 400
        if not _requerimiento_estado_existe(new_estado):
            return jsonify({'error': 'requerimiento_estado_id no existe en requerimiento_estados'}), 400

        porcentaje_avance = data.get('porcentaje_avance')
        if porcentaje_avance is None:
            return jsonify({'error': 'porcentaje_avance no puede ser null'}), 400
        if not isinstance(porcentaje_avance, int) or isinstance(porcentaje_avance, bool):
            return jsonify({'error': 'porcentaje_avance debe ser entero'}), 400
        if porcentaje_avance < 0 or porcentaje_avance > 100:
            return jsonify({'error': 'porcentaje_avance debe estar entre 0 y 100'}), 400

        actual = db.session.execute(
            db.text("""
                SELECT id, requerimiento_estado_id, porcentaje_avance, modificador, modificacion
                FROM requerimiento_recursos
                WHERE id = :id
            """),
            {'id': id}
        ).fetchone()

        if actual is None:
            return jsonify({'error': 'Relacion no encontrada'}), 404

        now = datetime.now(timezone.utc)
        auth_user = _resolve_authenticated_user()
        modificador = auth_user or data.get('modificador') or actual.modificador or 'Sistema'

        db.session.execute(
            db.text("""
                UPDATE requerimiento_recursos
                SET requerimiento_estado_id = :requerimiento_estado_id,
                    porcentaje_avance = :porcentaje_avance,
                    modificacion = :modificacion,
                    modificador = :modificador
                WHERE id = :id
            """),
            {
                'id': id,
                'requerimiento_estado_id': new_estado,
                'porcentaje_avance': porcentaje_avance,
                'modificacion': now,
                'modificador': modificador
            }
        )
        db.session.commit()

        updated = db.session.execute(
            db.text("""
                SELECT id, requerimiento_estado_id, porcentaje_avance, modificacion, modificador
                FROM requerimiento_recursos
                WHERE id = :id
            """),
            {'id': id}
        ).fetchone()
        if updated is None:
            return jsonify({'error': 'Relacion no encontrada despues de actualizar'}), 500

        return jsonify({
            'id': updated.id,
            'requerimiento_estado_id': updated.requerimiento_estado_id,
            'porcentaje_avance': updated.porcentaje_avance,
            'modificacion': _to_iso_optional(updated.modificacion),
            'modificador': updated.modificador
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Error inesperado al actualizar estado y avance', 'details': str(e)}), 500


@requerimiento_recursos_bp.route('/api/requerimiento-recursos/<int:id>/asignar-mesa-superior/<int:usuario_emisor_id>', methods=['PATCH'])
def patch_asignacion_mesa_superior(id,usuario_emisor_id):
    """Asignar un requerimiento a una mesa superior.
    ---
    tags:
      - Requerimiento Recursos
    summary: Asignar mesa superior
    description: Actualiza el usuario emisor asociado al requerimiento para reflejar la asignación a una mesa superior.
    parameters:
      - name: id
        in: path
        type: integer
        required: true
      - name: usuario_emisor_id
        in: path
        type: integer
        required: true
    responses:
      200:
        description: Asignación actualizada correctamente
      404:
        description: Requerimiento de recurso no encontrado
    """
    result = db.session.execute(
        db.text("""
            UPDATE requerimiento_recursos
            SET usuario_emisor_id = :usuario_emisor_id,
                requerimiento_estado_id = 5,
                porcentaje_avance = 0
            WHERE id = :id
        """),
        {'id': id, 'usuario_emisor_id': usuario_emisor_id}
    )

    if getattr(result, 'rowcount', 0) == 0:
        return jsonify({'error': 'Asignacion no encontrada'}), 404

    db.session.commit()
    return jsonify({'mensaje': 'Asignacion actualizada correctamente'})


@requerimiento_recursos_bp.route('/api/requerimiento-recursos/<int:id>', methods=['DELETE'])
def delete_requerimiento_recurso(id):
    """Eliminar un requerimiento de recurso.
    ---
    tags:
      - Requerimiento Recursos
    summary: Eliminar requerimiento de recurso
    description: Elimina físicamente el requerimiento de recurso identificado por `id`.
    parameters:
      - name: id
        in: path
        type: integer
        required: true
    responses:
      200:
        description: Requerimiento de recurso eliminado correctamente
      404:
        description: Requerimiento de recurso no encontrado
    """
    result = db.session.execute(
        db.text("DELETE FROM requerimiento_recursos WHERE id = :id"),
        {'id': id}
    )

    if getattr(result, 'rowcount', 0) == 0:
        return jsonify({'error': 'Relacion no encontrada'}), 404

    db.session.commit()
    return jsonify({'mensaje': 'Relacion eliminada correctamente'})

@requerimiento_recursos_bp.route('/api/requerimiento-recursos/deshabilitar-requerimiento/<int:id>', methods=['PATCH'])
def deshabilitar_requerimiento_recurso(id):
    """Deshabilitar un requerimiento de recurso sin eliminarlo.
    ---
    tags:
      - Requerimiento Recursos
    summary: Deshabilitar requerimiento de recurso
    description: Marca el requerimiento como inactivo para conservar su histórico.
    parameters:
      - name: id
        in: path
        type: integer
        required: true
    responses:
      200:
        description: Requerimiento de recurso deshabilitado correctamente
      404:
        description: Requerimiento de recurso no encontrado
    """
    result = db.session.execute(
        db.text("""
            UPDATE requerimiento_recursos
            SET activo = false
            WHERE id = :id
        """),
        {'id': id}
    )

    if getattr(result, 'rowcount', 0) == 0:
        return jsonify({'error': 'Relacion no encontrada'}), 404

    db.session.commit()
    return jsonify({'mensaje': 'Relacion deshabilitada correctamente'})


@requerimiento_recursos_bp.route('/api/requerimiento-recursos/usuario_emisor/<int:usuario_emisor_id>', methods=['GET'])
def get_requerimiento_recursos_by_usuario_emisor(usuario_emisor_id):
    """Obtener requerimientos de recursos por usuario emisor.
    ---
    tags:
      - Requerimiento Recursos
    summary: Obtener requerimientos por usuario emisor
    description: Devuelve los requerimientos emitidos por el usuario indicado.
    parameters:
      - name: usuario_emisor_id
        in: path
        type: integer
        required: true
        description: ID del usuario que inicia sesion
    responses:
      200:
        description: Lista de requerimientos recursos del usuario emisor
        schema:
          type: array
          items:
            type: object
            properties:
              id: {type: integer}
              requerimiento_numero: {type: string}
              requerimiento_id: {type: integer}
              requerimiento_estado_id: {type: integer}
              usuario_receptor_id: {type: integer}
              usuario_emisor_id: {type: integer}
              recurso_grupo_id: {type: integer}
              recurso_tipo_id: {type: integer}
              cantidad_solicitada: {type: integer}
              costo: {type: number}
              especificaciones: {type: string}
              destino: {type: string}
              detalle: {type: string}
              activo: {type: boolean}
              creador: {type: string}
              creacion: {type: string}
              modificador: {type: string}
              modificacion: {type: string}
              usuario_emisor: {type: string}
              usuario_receptor: {type: string}
    """
    result = db.session.execute(
        db.text("""
            SELECT
                rr.id AS id,
                rr.requerimiento_numero AS requerimiento_numero,
                rr.requerimiento_id AS requerimiento_id,
                rr.usuario_receptor_id AS usuario_receptor_id,
                ur.usuario AS usuario_receptor,
                rr.recurso_grupo_id AS recurso_grupo_id,
                rg.nombre AS recurso_grupo_nombre,
                rr.recurso_tipo_id AS recurso_tipo_id,
                rt.nombre AS recurso_tipo_nombre,
                rr.cantidad_solicitada AS cantidad_solicitada,
                rr.costo AS costo,
                rr.especificaciones AS especificaciones,
                rr.destino AS destino,
                rr.detalle AS detalle,
                rr.requerimiento_estado_id AS requerimiento_estado_id,
                rr.activo AS activo,
                rr.creador AS creador,
                rr.creacion AS creacion,
                rr.modificador AS modificador,
                rr.modificacion AS modificacion,
                rr.usuario_emisor_id AS usuario_emisor_id,
                ue.usuario AS usuario_emisor
            FROM public.requerimiento_recursos rr
            LEFT JOIN public.usuarios ur
                ON rr.usuario_receptor_id = ur.id
            LEFT JOIN public.usuarios ue
                ON rr.usuario_emisor_id = ue.id
            LEFT JOIN public.recurso_tipos rt
                ON rr.recurso_tipo_id = rt.id
            LEFT JOIN public.recurso_grupos rg
                ON rr.recurso_grupo_id = rg.id
            WHERE rr.usuario_emisor_id = :usuario_emisor_id
                AND COALESCE(rr.activo, true) = true
            ORDER BY rr.id DESC
        """),
        {'usuario_emisor_id': usuario_emisor_id}
    )
    rows = []
    for row in result:
        row_mapping = row._mapping
        rows.append({
            'id': row_mapping.get('id'),
            'requerimiento_numero': row_mapping.get('requerimiento_numero'),
            'requerimiento_id': row_mapping.get('requerimiento_id'),
            'requerimiento_estado_id': row_mapping.get('requerimiento_estado_id'),
            'usuario_receptor_id': row_mapping.get('usuario_receptor_id'),
            'usuario_receptor': row_mapping.get('usuario_receptor'),
            'usuario_emisor_id': row_mapping.get('usuario_emisor_id'),
            'usuario_emisor': row_mapping.get('usuario_emisor'),
            'recurso_grupo_id': row_mapping.get('recurso_grupo_id'),
            'recurso_grupo_nombre': row_mapping.get('recurso_grupo_nombre'),
            'recurso_tipo_id': row_mapping.get('recurso_tipo_id'),
            'recurso_tipo_nombre': row_mapping.get('recurso_tipo_nombre'),
            'cantidad_solicitada': row_mapping.get('cantidad_solicitada'),
            'costo': _to_float_optional(row_mapping.get('costo')),
            'especificaciones': row_mapping.get('especificaciones'),
            'destino': row_mapping.get('destino'),
            'detalle': row_mapping.get('detalle'),
            'activo': row_mapping.get('activo'),
            'creador': row_mapping.get('creador'),
            'creacion': _to_iso_optional(row_mapping.get('creacion')),
            'modificador': row_mapping.get('modificador'),
            'modificacion': _to_iso_optional(row_mapping.get('modificacion'))
        })

    return jsonify(rows)


@requerimiento_recursos_bp.route(
    '/api/requerimiento-recursos/rechazados/usuario_emisor/<int:usuario_emisor_id>/requerimiento_estado/<int:requerimiento_estado_id>',
    methods=['GET']
)
def get_requerimiento_recursos_rechazados(usuario_emisor_id, requerimiento_estado_id):
    """Listar requerimientos rechazados por usuario emisor y estado.
    ---
    tags:
      - Requerimiento Recursos
    summary: Listar requerimientos rechazados
    description: Devuelve los requerimientos emitidos por un usuario que coinciden con el estado de rechazo indicado.
    parameters:
      - name: usuario_emisor_id
        in: path
        type: integer
        required: true
        description: ID del usuario emisor al que le rechazaron requerimientos
      - name: requerimiento_estado_id
        in: path
        type: integer
        required: true
        description: ID del estado de requerimiento que representa rechazo
    responses:
      200:
        description: Lista de requerimientos rechazados del usuario emisor
        schema:
          type: array
          items:
            type: object
            properties:
              id: {type: integer}
              requerimiento_numero: {type: string}
              requerimiento_id: {type: integer}
              requerimiento_estado_id: {type: integer}
              usuario_receptor_id: {type: integer}
              usuario_receptor: {type: string}
              usuario_emisor_id: {type: integer}
              usuario_emisor: {type: string}
              recurso_grupo_id: {type: integer}
              recurso_grupo_nombre: {type: string}
              recurso_tipo_id: {type: integer}
              recurso_tipo_nombre: {type: string}
              cantidad_solicitada: {type: integer}
              costo: {type: number}
              especificaciones: {type: string}
              destino: {type: string}
              detalle: {type: string}
              activo: {type: boolean}
              creador: {type: string}
              creacion: {type: string}
              modificador: {type: string}
              modificacion: {type: string}
      400:
        description: requerimiento_estado_id invalido
    """
    if not _requerimiento_estado_existe(requerimiento_estado_id):
        return jsonify({'error': 'requerimiento_estado_id no existe en requerimiento_estados'}), 400

    result = db.session.execute(
        db.text("""
            SELECT
                rr.id AS id,
                rr.requerimiento_numero AS requerimiento_numero,
                rr.requerimiento_id AS requerimiento_id,
                rr.usuario_receptor_id AS usuario_receptor_id,
                ur.usuario AS usuario_receptor,
                rr.recurso_grupo_id AS recurso_grupo_id,
                rg.nombre AS recurso_grupo_nombre,
                rr.recurso_tipo_id AS recurso_tipo_id,
                rt.nombre AS recurso_tipo_nombre,
                rr.cantidad_solicitada AS cantidad_solicitada,
                rr.costo AS costo,
                rr.especificaciones AS especificaciones,
                rr.destino AS destino,
                rr.detalle AS detalle,
                rr.requerimiento_estado_id AS requerimiento_estado_id,
                rr.activo AS activo,
                rr.creador AS creador,
                rr.creacion AS creacion,
                rr.modificador AS modificador,
                rr.modificacion AS modificacion,
                rr.usuario_emisor_id AS usuario_emisor_id,
                ue.usuario AS usuario_emisor
            FROM public.requerimiento_recursos rr
            LEFT JOIN public.usuarios ur
                ON rr.usuario_receptor_id = ur.id
            LEFT JOIN public.usuarios ue
                ON rr.usuario_emisor_id = ue.id
            LEFT JOIN public.recurso_tipos rt
                ON rr.recurso_tipo_id = rt.id
            LEFT JOIN public.recurso_grupos rg
                ON rr.recurso_grupo_id = rg.id
            WHERE rr.usuario_emisor_id = :usuario_emisor_id
              AND rr.requerimiento_estado_id = :requerimiento_estado_id
              AND COALESCE(rr.activo, true) = true
            ORDER BY rr.id DESC
        """),
        {
            'usuario_emisor_id': usuario_emisor_id,
            'requerimiento_estado_id': requerimiento_estado_id
        }
    )
    rows = []
    for row in result:
        row_mapping = row._mapping
        creacion = row_mapping.get('creacion')
        modificacion = row_mapping.get('modificacion')
        rows.append({
            'id': row_mapping.get('id'),
            'requerimiento_numero': row_mapping.get('requerimiento_numero'),
            'requerimiento_id': row_mapping.get('requerimiento_id'),
            'requerimiento_estado_id': row_mapping.get('requerimiento_estado_id'),
            'usuario_receptor_id': row_mapping.get('usuario_receptor_id'),
            'usuario_receptor': row_mapping.get('usuario_receptor'),
            'usuario_emisor_id': row_mapping.get('usuario_emisor_id'),
            'usuario_emisor': row_mapping.get('usuario_emisor'),
            'recurso_grupo_id': row_mapping.get('recurso_grupo_id'),
            'recurso_grupo_nombre': row_mapping.get('recurso_grupo_nombre'),
            'recurso_tipo_id': row_mapping.get('recurso_tipo_id'),
            'recurso_tipo_nombre': row_mapping.get('recurso_tipo_nombre'),
            'cantidad_solicitada': row_mapping.get('cantidad_solicitada'),
            'costo': _to_float_optional(row_mapping.get('costo')),
            'especificaciones': row_mapping.get('especificaciones'),
            'destino': row_mapping.get('destino'),
            'detalle': row_mapping.get('detalle'),
            'activo': row_mapping.get('activo'),
            'creador': row_mapping.get('creador'),
            'creacion': _to_iso_optional(creacion),
            'modificador': row_mapping.get('modificador'),
            'modificacion': _to_iso_optional(modificacion)
        })

    return jsonify(rows)


@requerimiento_recursos_bp.route('/api/requerimiento-recursos/requerimiento_numero/usuario_emisor_id/<int:usuario_emisor_id>', methods=['GET'])
def get_requerimiento_recursos_by_requerimiento_numero_and_usuario_emisor_id( usuario_emisor_id):
    """Obtener requerimientos agrupados por número de requerimiento y usuario emisor.
    ---
    tags:
      - Requerimiento Recursos
    summary: Agrupar requerimientos por número y usuario emisor
    description: Agrupa los requerimientos activos del usuario emisor indicado por `requerimiento_numero`.
    parameters:
      - name: usuario_emisor_id
        in: path
        type: integer
        required: true
    responses:
      200:
        description: Lista de requerimientos recursos que coinciden con el requerimiento_numero y usuario_emisor_id
        schema:
          type: array
          items:
            type: object
            properties:
              requerimiento_numero: {type: string}
              cantidad_solicitada: {type: integer}
              detalle: {type: string}
              activo: {type: boolean}
              creacion: {type: string}
    """
    result = db.session.execute(
        db.text("""
            SELECT
                MAX(RR.ID) AS ULTIMO_ID,
                RR.REQUERIMIENTO_NUMERO AS REQUERIMIENTO_NUMERO,
                SUM(RR.CANTIDAD_SOLICITADA) AS CANTIDAD_SOLICITADA,
                RR.DETALLE AS DETALLE
            FROM
                PUBLIC.REQUERIMIENTO_RECURSOS RR
            WHERE
                RR.USUARIO_EMISOR_ID = :usuario_emisor_id
                AND COALESCE(RR.ACTIVO, TRUE) = TRUE
                AND RR.REQUERIMIENTO_ESTADO_ID NOT IN (4, 6)  -- Excluir estados Rechazado (4) y Anulado (6)
            GROUP BY
                RR.REQUERIMIENTO_NUMERO,
                RR.DETALLE
            ORDER BY
                MAX(RR.ID) DESC;
        """),
        {'usuario_emisor_id': usuario_emisor_id}
        )

    def _to_iso(value):
        if value is None:
            return None
        return value.isoformat() if hasattr(value, 'isoformat') else str(value)

    rows = []
    for row in result:
        row_mapping = row._mapping
        rows.append({
            'id': row_mapping.get('ultimo_id'),
            'requerimiento_numero': row_mapping.get('requerimiento_numero'),
            'cantidad_solicitada': row_mapping.get('cantidad_solicitada'),
            'detalle': row_mapping.get('detalle'),
            'activo': row_mapping.get('activo'),
            'creacion': _to_iso(row_mapping.get('creacion'))
        })

    return jsonify(rows)


@requerimiento_recursos_bp.route('/api/requerimiento-recursos/requerimiento_numero/<string:requerimiento_numero>/usuario_emisor_id/<int:usuario_emisor_id>', methods=['GET'])
def get_requerimiento_recursos_by_requerimiento_numero_x_usuario_emisor_id(requerimiento_numero, usuario_emisor_id):
    """Obtener requerimientos de recursos por número de requerimiento y usuario emisor.
    ---
    tags:
      - Requerimiento Recursos  
    summary: Obtener requerimientos por número y usuario emisor
    description: Devuelve los requerimientos cuyo `requerimiento_numero` y `usuario_emisor_id` coinciden con los parámetros indicados.
    parameters:
      - name: requerimiento_numero
        in: path
        type: string
        required: true
      - name: usuario_emisor_id
        in: path
        type: integer
        required: true
    responses:
      200:
        description: Lista de requerimientos recursos que coinciden con el requerimiento_numero
        schema:
          type: array
          items:
            type: object
            properties:
              id: {type: integer}
              requerimiento_numero: {type: string}
              cantidad_solicitada: {type: integer}
              activo: {type: boolean}
              creacion: {type: string}
              
    """
    result = db.session.execute(
        db.text("""
            SELECT
                rr.id AS id,
                rr.requerimiento_numero AS requerimiento_numero,
                rr.requerimiento_id AS requerimiento_id,
                rr.usuario_receptor_id AS usuario_receptor_id,
                ur.usuario AS usuario_receptor,
                rr.recurso_grupo_id AS recurso_grupo_id,
                rg.nombre AS recurso_grupo_nombre,
                rr.recurso_tipo_id AS recurso_tipo_id,
                rt.nombre AS recurso_tipo_nombre,
                rr.cantidad_solicitada AS cantidad_solicitada,
                rr.costo AS costo,
                rr.especificaciones AS especificaciones,
                rr.destino AS destino,
                rr.detalle AS detalle,
                rr.requerimiento_estado_id AS requerimiento_estado_id,
                re.nombre AS requerimiento_estado_nombre,
                rr.activo AS activo,
                rr.creador AS creador,
                rr.creacion AS creacion,
                rr.modificador AS modificador,
                rr.modificacion AS modificacion,
                rr.usuario_emisor_id AS usuario_emisor_id,
                ue.usuario AS usuario_emisor,
                rr.porcentaje_avance AS porcentaje_avance
            FROM public.requerimiento_recursos rr
            INNER JOIN public.requerimiento_estados re
                ON rr.requerimiento_estado_id = re.id
            LEFT JOIN public.usuarios ur
                ON rr.usuario_receptor_id = ur.id
            LEFT JOIN public.usuarios ue
                ON rr.usuario_emisor_id = ue.id
            LEFT JOIN public.recurso_tipos rt
                ON rr.recurso_tipo_id = rt.id
            LEFT JOIN public.recurso_grupos rg
                ON rr.recurso_grupo_id = rg.id
            WHERE rr.requerimiento_numero = :requerimiento_numero
                AND COALESCE(rr.activo, true) = true
                AND rr.usuario_emisor_id = :usuario_emisor_id
                and re.id not in (4,6) -- Excluir estados Rechazado (4) y Anulado (6)
            ORDER BY rr.id DESC
        """),
        {'requerimiento_numero': requerimiento_numero, 'usuario_emisor_id': usuario_emisor_id}
    )
    def _to_iso_if_datetime(value):
        if value is None:
            return None
        return value.isoformat() if hasattr(value, 'isoformat') else str(value)

    rows = []
    for row in result:
        row_mapping = row._mapping
        rows.append({
            'id': row_mapping.get('id'),
            'requerimiento_numero': row_mapping.get('requerimiento_numero'),
            'requerimiento_id': row_mapping.get('requerimiento_id'),
            'requerimiento_estado_id': row_mapping.get('requerimiento_estado_id'),
            'requerimiento_estado_nombre': row_mapping.get('requerimiento_estado_nombre'),
            'usuario_receptor_id': row_mapping.get('usuario_receptor_id'),
            'usuario_receptor': row_mapping.get('usuario_receptor'),
            'usuario_emisor_id': row_mapping.get('usuario_emisor_id'),
            'usuario_emisor': row_mapping.get('usuario_emisor'),
            'recurso_grupo_id': row_mapping.get('recurso_grupo_id'),
            'recurso_grupo_nombre': row_mapping.get('recurso_grupo_nombre'),
            'recurso_tipo_id': row_mapping.get('recurso_tipo_id'),
            'recurso_tipo_nombre': row_mapping.get('recurso_tipo_nombre'),
            'cantidad_solicitada': row_mapping.get('cantidad_solicitada'),
            'costo': _to_float_optional(row_mapping.get('costo')),
            'especificaciones': row_mapping.get('especificaciones'),
            'destino': row_mapping.get('destino'),
            'detalle': row_mapping.get('detalle'),
            'activo': row_mapping.get('activo'),
            'porcentaje_avance': row_mapping.get('porcentaje_avance'),
            'creador': row_mapping.get('creador'),
            'creacion': _to_iso_if_datetime(row_mapping.get('creacion')),
            'modificador': row_mapping.get('modificador'),
            'modificacion': _to_iso_if_datetime(row_mapping.get('modificacion'))
        })

    return jsonify(rows)

@requerimiento_recursos_bp.route('/api/requerimiento-recursos/requerimiento_numero/<string:requerimiento_numero>/usuario_receptor_id/<int:usuario_receptor_id>', methods=['GET'])
def get_requerimiento_recursos_by_requerimiento_numero_x_usuario_receptor_id(requerimiento_numero, usuario_receptor_id):
    """Obtener requerimientos de recursos por número de requerimiento y usuario receptor.
    ---
    tags:
      - Requerimiento Recursos  
    summary: Obtener requerimientos por número y usuario receptor
    description: Devuelve los requerimientos cuyo `requerimiento_numero` y `usuario_receptor_id` coinciden con los parámetros indicados.
    parameters:
      - name: requerimiento_numero
        in: path
        type: string
        required: true
      - name: usuario_receptor_id
        in: path
        type: integer
        required: true
    responses:
      200:
        description: Lista de requerimientos recursos que coinciden con el requerimiento_numero
        schema:
          type: array
          items:
            type: object
            properties:
              id: {type: integer}
              requerimiento_numero: {type: string}
              cantidad_solicitada: {type: integer}
              activo: {type: boolean}
              creacion: {type: string}
              
    """
    result = db.session.execute(
        db.text("""
            SELECT
                rr.id AS id,
                rr.requerimiento_numero AS requerimiento_numero,
                rr.requerimiento_id AS requerimiento_id,
                rr.usuario_receptor_id AS usuario_receptor_id,
                ur.usuario AS usuario_receptor,
                rr.recurso_grupo_id AS recurso_grupo_id,
                rg.nombre AS recurso_grupo_nombre,
                rr.recurso_tipo_id AS recurso_tipo_id,
                rt.nombre AS recurso_tipo_nombre,
                rr.cantidad_solicitada AS cantidad_solicitada,
                rr.costo AS costo,
                rr.especificaciones AS especificaciones,
                rr.destino AS destino,
                rr.detalle AS detalle,
                rr.requerimiento_estado_id AS requerimiento_estado_id,
                rr.activo AS activo,
                rr.creador AS creador,
                rr.creacion AS creacion,
                rr.modificador AS modificador,
                rr.modificacion AS modificacion,
                rr.usuario_emisor_id AS usuario_emisor_id,
                ue.usuario AS usuario_emisor,
                rr.porcentaje_avance AS porcentaje_avance
            FROM public.requerimiento_recursos rr
            LEFT JOIN public.usuarios ur
                ON rr.usuario_receptor_id = ur.id
            LEFT JOIN public.usuarios ue
                ON rr.usuario_emisor_id = ue.id
            LEFT JOIN public.recurso_tipos rt
                ON rr.recurso_tipo_id = rt.id
            LEFT JOIN public.recurso_grupos rg
                ON rr.recurso_grupo_id = rg.id
            WHERE rr.requerimiento_numero = :requerimiento_numero
                AND COALESCE(rr.activo, true) = true
                AND rr.usuario_receptor_id = :usuario_receptor_id
            ORDER BY rr.id DESC
        """),
        {'requerimiento_numero': requerimiento_numero, 'usuario_receptor_id': usuario_receptor_id}
    )
    def _to_iso_if_datetime(value):
        if value is None:
            return None
        return value.isoformat() if hasattr(value, 'isoformat') else str(value)

    rows = []
    for row in result:
        row_mapping = row._mapping
        costo_raw = row_mapping.get('costo')
        rows.append({
            'id': row_mapping.get('id'),
            'requerimiento_numero': row_mapping.get('requerimiento_numero'),
            'requerimiento_id': row_mapping.get('requerimiento_id'),
            'requerimiento_estado_id': row_mapping.get('requerimiento_estado_id'),
            'usuario_receptor_id': row_mapping.get('usuario_receptor_id'),
            'usuario_receptor': row_mapping.get('usuario_receptor'),
            'usuario_emisor_id': row_mapping.get('usuario_emisor_id'),
            'usuario_emisor': row_mapping.get('usuario_emisor'),
            'recurso_grupo_id': row_mapping.get('recurso_grupo_id'),
            'recurso_grupo_nombre': row_mapping.get('recurso_grupo_nombre'),
            'recurso_tipo_id': row_mapping.get('recurso_tipo_id'),
            'recurso_tipo_nombre': row_mapping.get('recurso_tipo_nombre'),
            'cantidad_solicitada': row_mapping.get('cantidad_solicitada'),
            'costo': _to_float_optional(costo_raw),
            'porcentaje_avance': row_mapping.get('porcentaje_avance'),
            'especificaciones': row_mapping.get('especificaciones'),
            'destino': row_mapping.get('destino'),
            'detalle': row_mapping.get('detalle'),
            'activo': row_mapping.get('activo'),
            'creador': row_mapping.get('creador'),
            'creacion': _to_iso_if_datetime(row_mapping.get('creacion')),
            'modificador': row_mapping.get('modificador'),
            'modificacion': _to_iso_if_datetime(row_mapping.get('modificacion'))
        })

    return jsonify(rows)
    """Obtener requerimientos recursos por requerimiento_numero 
    ---
    tags:
      - Requerimiento Recursos  
    parameters:
      - name: requerimiento_numero
        in: path
        type: string
        required: true
    responses:
      200:
        description: Lista de requerimientos recursos que coinciden con el requerimiento_numero
        schema:
          type: array
          items:
            type: object
            properties:
              id: {type: integer}
              requerimiento_numero: {type: string}
              cantidad_solicitada: {type: integer}
              activo: {type: boolean}
              creacion: {type: string}
    """
    result = db.session.execute(
        db.text("""
            SELECT
                rr.id AS id,
                rr.requerimiento_numero AS requerimiento_numero,
                rr.requerimiento_id AS requerimiento_id,
                rr.usuario_receptor_id AS usuario_receptor_id,
                ur.usuario AS usuario_receptor,
                rr.recurso_grupo_id AS recurso_grupo_id,
                rg.nombre AS recurso_grupo_nombre,
                rr.recurso_tipo_id AS recurso_tipo_id,
                rt.nombre AS recurso_tipo_nombre,
                rr.cantidad_solicitada AS cantidad_solicitada,
                rr.costo AS costo,
                rr.especificaciones AS especificaciones,
                rr.destino AS destino,
                rr.detalle AS detalle,
                rr.requerimiento_estado_id AS requerimiento_estado_id,
                rr.activo AS activo,
                rr.creador AS creador,
                rr.creacion AS creacion,
                rr.modificador AS modificador,
                rr.modificacion AS modificacion,
                rr.usuario_emisor_id AS usuario_emisor_id,
                ue.usuario AS usuario_emisor
            FROM public.requerimiento_recursos rr
            LEFT JOIN public.usuarios ur
                ON rr.usuario_receptor_id = ur.id
            LEFT JOIN public.usuarios ue
                ON rr.usuario_emisor_id = ue.id
            LEFT JOIN public.recurso_tipos rt
                ON rr.recurso_tipo_id = rt.id
            LEFT JOIN public.recurso_grupos rg
                ON rr.recurso_grupo_id = rg.id
            WHERE rr.requerimiento_numero = :requerimiento_numero
                AND COALESCE(rr.activo, true) = true
            ORDER BY rr.id DESC
        """),
        {'requerimiento_numero': requerimiento_numero}
    )
    def _to_iso_if_datetime(value):
        if value is None:
            return None
        return value.isoformat() if hasattr(value, 'isoformat') else str(value)

    rows = []
    for row in result:
        row_mapping = row._mapping
        rows.append({
            'id': row_mapping.get('id'),
            'requerimiento_numero': row_mapping.get('requerimiento_numero'),
            'requerimiento_id': row_mapping.get('requerimiento_id'),
            'requerimiento_estado_id': row_mapping.get('requerimiento_estado_id'),
            'usuario_receptor_id': row_mapping.get('usuario_receptor_id'),
            'usuario_receptor': row_mapping.get('usuario_receptor'),
            'usuario_emisor_id': row_mapping.get('usuario_emisor_id'),
            'usuario_emisor': row_mapping.get('usuario_emisor'),
            'recurso_grupo_id': row_mapping.get('recurso_grupo_id'),
            'recurso_grupo_nombre': row_mapping.get('recurso_grupo_nombre'),
            'recurso_tipo_id': row_mapping.get('recurso_tipo_id'),
            'recurso_tipo_nombre': row_mapping.get('recurso_tipo_nombre'),
            'cantidad_solicitada': row_mapping.get('cantidad_solicitada'),
            'costo': _to_float_optional(row_mapping.get('costo')),
            'especificaciones': row_mapping.get('especificaciones'),
            'destino': row_mapping.get('destino'),
            'detalle': row_mapping.get('detalle'),
            'activo': row_mapping.get('activo'),
            'creador': row_mapping.get('creador'),
            'creacion': _to_iso_if_datetime(row_mapping.get('creacion')),
            'modificador': row_mapping.get('modificador'),
            'modificacion': _to_iso_if_datetime(row_mapping.get('modificacion'))
        })
        
    return jsonify(rows)
