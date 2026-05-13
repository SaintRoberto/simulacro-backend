from flask import request, jsonify
from requerimiento_recursos import requerimiento_recursos_bp
from models import db
from datetime import datetime, timezone


def _serialize_requerimiento_recurso(row):
    return {
        'id': row.id,
        'requerimiento_id': row.requerimiento_id,
        'usuario_receptor_id': row.usuario_receptor_id,
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
        'modificacion': row.modificacion.isoformat() if row.modificacion else None
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
              requerimiento_id: {type: integer}
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
          required: [requerimiento_id, usuario_receptor_id, recurso_grupo_id, recurso_tipo_id]
          properties:
            requerimiento_id: {type: integer}
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
    responses:
      201:
        description: Requerimiento recurso creado
    """
    data = request.get_json() or {}
    required_fields = ['requerimiento_id', 'usuario_receptor_id', 'recurso_grupo_id', 'recurso_tipo_id']
    missing_fields = [field for field in required_fields if field not in data]
    if missing_fields:
        return jsonify({'error': f"Campos requeridos faltantes: {', '.join(missing_fields)}"}), 400

    now = datetime.now(timezone.utc)

    query = db.text("""
        INSERT INTO requerimiento_recursos (
            requerimiento_id, usuario_receptor_id, recurso_grupo_id, recurso_tipo_id, cantidad_solicitada, costo,
            especificaciones, destino, detalle, activo, creador, creacion, modificador, modificacion
        )
        VALUES (
            :requerimiento_id, :usuario_receptor_id, :recurso_grupo_id, :recurso_tipo_id, :cantidad_solicitada, :costo,
            :especificaciones, :destino, :detalle, :activo, :creador, :creacion, :modificador, :modificacion
        )
        RETURNING id
    """)

    result = db.session.execute(query, {
        'requerimiento_id': data['requerimiento_id'],
        'usuario_receptor_id': data['usuario_receptor_id'],
        'recurso_grupo_id': data['recurso_grupo_id'],
        'recurso_tipo_id': data['recurso_tipo_id'],
        'cantidad_solicitada': data.get('cantidad_solicitada', data.get('cantidad', 1)),
        'costo': data.get('costo', 0),
        'especificaciones': data.get('especificaciones'),
        'destino': data.get('destino'),
        'detalle': data.get('detalle'),
        'activo': data.get('activo', True),
        'creador': data.get('creador', 'Sistema'),
        'creacion': now,
        'modificador': data.get('modificador', data.get('creador', 'Sistema')),
        'modificacion': data.get('modificacion')
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
              requerimiento_id: {type: integer}
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
            requerimiento_id: {type: integer}
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

    params = {
        'id': id,
        'requerimiento_id': data.get('requerimiento_id', actual.requerimiento_id),
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
        'modificacion': data.get('modificacion', now)
    }

    query = db.text("""
        UPDATE requerimiento_recursos
        SET requerimiento_id = :requerimiento_id,
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
            modificacion = :modificacion
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
