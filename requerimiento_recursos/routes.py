from flask import request, jsonify
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
        'recurso_tipo_id': row.recurso_tipo_id,
        'cantidad_solicitada': row.cantidad_solicitada,
        'costo': float(row.costo) if row.costo is not None else None,
        'especificaciones': row.especificaciones,
        'destino': row.destino,
        'detalle': row.detalle,
        'activo': row.activo,
        'creador': row.creador,
        'creacion': row.creacion.isoformat() if row.creacion else None,
        'modificador': row.modificador,
        'modificacion': row.modificacion.isoformat() if row.modificacion else None,
        "usuario_emisor_id": row.usuario_emisor_id,
        "usuario_emisor": _get_optional('usuario_emisor'),
    }


@requerimiento_recursos_bp.route('/api/requerimiento-recursos', methods=['GET'])
def get_requerimiento_recursos():
    """Listar requerimiento recursos
    ---
    tags:
      - Requerimiento Recursos
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
    """Crear requerimiento recurso
    ---
    tags:
      - Requerimiento Recursos
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
        description: Requerimiento recurso creado
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
    """Obtener requerimiento recurso por requerimiento_id
    ---
    tags:
      - Requerimiento Recursos
    parameters:
      - name: requerimiento_id
        in: path
        type: integer
        required: true
    responses:
      200:
        description: Requerimiento recurso
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
    """Obtener requerimientos recursos por usuario receptor
    ---
    tags:
      - Requerimiento Recursos
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
    """
    result = db.session.execute(
        db.text("""
            SELECT * FROM requerimiento_recursos
            WHERE usuario_receptor_id = :usuario_receptor_id
              AND COALESCE(activo, true) = true
            ORDER BY id DESC
        """),
        {'usuario_receptor_id': usuario_receptor_id}
    )
    return jsonify([_serialize_requerimiento_recurso(row) for row in result])


@requerimiento_recursos_bp.route('/api/requerimiento-recursos/id/<int:id>', methods=['GET'])
def get_requerimiento_recurso(id):
    """Obtener requerimiento recurso por ID
    ---
    tags:
      - Requerimiento Recursos
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
    """Obtener la cantidad pendiente por despachar de un recurso de inventario
    ---
    tags:
      - Requerimiento Recursos
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
    """Actualizar requerimiento recurso
    ---
    tags:
      - Requerimiento Recursos
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
        description: Requerimiento recurso actualizado
      404:
        description: No encontrado
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


@requerimiento_recursos_bp.route('/api/requerimiento-recursos/<int:id>', methods=['DELETE'])
def delete_requerimiento_recurso(id):
    """Eliminar requerimiento recurso
    ---
    tags:
      - Requerimiento Recursos
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
        db.text("DELETE FROM requerimiento_recursos WHERE id = :id"),
        {'id': id}
    )

    if getattr(result, 'rowcount', 0) == 0:
        return jsonify({'error': 'Relacion no encontrada'}), 404

    db.session.commit()
    return jsonify({'mensaje': 'Relacion eliminada correctamente'})



@requerimiento_recursos_bp.route('/api/requerimiento-recursos/usuario_emisor/<int:usuario_emisor_id>', methods=['GET'])
def get_requerimiento_recursos_by_usuario_emisor(usuario_emisor_id):
    """Obtener requerimientos recursos por usuario emisor
    ---
    tags:
      - Requerimiento Recursos
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
            'costo': float(row_mapping.get('costo')) if row_mapping.get('costo') is not None else None,
            'especificaciones': row_mapping.get('especificaciones'),
            'destino': row_mapping.get('destino'),
            'detalle': row_mapping.get('detalle'),
            'activo': row_mapping.get('activo'),
            'creador': row_mapping.get('creador'),
            'creacion': row_mapping.get('creacion').isoformat() if row_mapping.get('creacion') else None,
            'modificador': row_mapping.get('modificador'),
            'modificacion': row_mapping.get('modificacion').isoformat() if row_mapping.get('modificacion') else None
        })

    return jsonify(rows)



@requerimiento_recursos_bp.route('/api/requerimiento-recursos/requerimiento_numero/usuario_emisor_id/<int:usuario_emisor_id>', methods=['GET'])
def get_requerimiento_recursos_by_requerimiento_numero_and_usuario_emisor_id( usuario_emisor_id):
    """Obtener requerimientos agrupados por requerimiento_numero por usuario_emisor_id
    ---
    tags:
      - Requerimiento Recursos
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
              activo: {type: boolean}
              creacion: {type: string}
    """
    result = db.session.execute(
        db.text("""
            SELECT
                rr.requerimiento_numero AS requerimiento_numero,
                SUM(rr.cantidad_solicitada) AS cantidad_solicitada,
                rr.detalle,
                rr.requerimiento_estado_id AS requerimiento_estado_id,
                MAX(rr.creacion) AS creacion
            FROM
                public.requerimiento_recursos rr
            WHERE
                rr.usuario_emisor_id = :usuario_emisor_id
                AND COALESCE(rr.activo, true) = true
            GROUP BY
                rr.requerimiento_numero,
                rr.requerimiento_estado_id,
                rr.detalle
            ORDER BY
                MAX(rr.creacion) DESC;
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
            'requerimiento_numero': row_mapping.get('requerimiento_numero'),
            'cantidad_solicitada': row_mapping.get('cantidad_solicitada'),
            'activo': row_mapping.get('activo'),
            'creacion': _to_iso(row_mapping.get('creacion')),
            'detalle': row_mapping.get('detalle')
        })

    return jsonify(rows)


@requerimiento_recursos_bp.route('/api/requerimiento-recursos/requeramiento_numero/<string:requerimiento_numero>', methods=['GET'])
def get_requerimiento_recursos_by_requerimiento_numero(requerimiento_numero):
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
            'costo': float(row_mapping.get('costo')) if row_mapping.get('costo') is not None else None,
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
            'costo': float(row_mapping.get('costo')) if row_mapping.get('costo') is not None else None,
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