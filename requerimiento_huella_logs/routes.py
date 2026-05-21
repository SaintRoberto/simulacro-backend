from datetime import datetime, timezone

from flask import jsonify, request
from sqlalchemy.exc import IntegrityError

from models import db
from requerimiento_huella_logs import requerimiento_huella_logs_bp


def _serialize_requerimiento_huella_log(row):
    row_mapping = getattr(row, "_mapping", {})

    def _get_optional(column_name):
        if column_name in row_mapping:
            return row_mapping[column_name]
        upper_column_name = column_name.upper()
        if upper_column_name in row_mapping:
            return row_mapping[upper_column_name]
        return None

    respuesta_fecha = _get_optional("respuesta_fecha")
    return {
        "id": _get_optional("id"),
        "requerimiento_recurso_id": _get_optional("requerimiento_recurso_id"),
        "requerimiento_numero": _get_optional("requerimiento_numero"),
        "secuencia": _get_optional("secuencia"),
        "requerimiento_accion_log_id": _get_optional("requerimiento_accion_log_id"),
        "requerimiento_accion": _get_optional("requerimiento_accion"),
        "requerimiento_estado_id": _get_optional("requerimiento_estado_id"),
        "requerimiento_estado": _get_optional("requerimiento_estado"),
        "respuesta_estado_id": _get_optional("respuesta_estado_id"),
        "respuesta_estado": _get_optional("respuesta_estado"),
        "movimiento_tipo_id": _get_optional("movimiento_tipo_id"),
        "movimiento_tipo": _get_optional("movimiento_tipo"),
        "usuario_accion_id": _get_optional("usuario_accion_id"),
        "usuario_accion": _get_optional("usuario_accion"),
        "usuario_emisor_id": _get_optional("usuario_emisor_id"),
        "usuario_emisor": _get_optional("usuario_emisor"),
        "usuario_receptor_id": _get_optional("usuario_receptor_id"),
        "usuario_receptor": _get_optional("usuario_receptor"),
        "coe_origen_id": _get_optional("coe_origen_id"),
        "coe_origen": _get_optional("coe_origen"),
        "mesa_origen_id": _get_optional("mesa_origen_id"),
        "mesa_origen": _get_optional("mesa_origen"),
        "coe_destino_id": _get_optional("coe_destino_id"),
        "coe_destino": _get_optional("coe_destino"),
        "mesa_destino_id": _get_optional("mesa_destino_id"),
        "mesa_destino": _get_optional("mesa_destino"),
        "recurso_grupo_id": _get_optional("recurso_grupo_id"),
        "recurso_grupo": _get_optional("recurso_grupo"),
        "recurso_tipo_id": _get_optional("recurso_tipo_id"),
        "recurso_tipo": _get_optional("recurso_tipo"),
        "recurso_inventario_id": _get_optional("recurso_inventario_id"),
        "cantidad_solicitada": _get_optional("cantidad_solicitada"),
        "cantidad_asignada": _get_optional("cantidad_asignada"),
        "motivo_id": _get_optional("motivo_id"),
        "motivo": _get_optional("motivo"),
        "respuesta_fecha": respuesta_fecha.isoformat() if hasattr(respuesta_fecha, "isoformat") else respuesta_fecha
    }


def _build_base_historial_query():
    return """
        SELECT
            rhl.id,
            rhl.requerimiento_recurso_id,
            rhl.requerimiento_numero,
            rhl.secuencia,
            rhl.requerimiento_accion_log_id,
            rac.nombre AS requerimiento_accion,
            rhl.requerimiento_estado_id,
            res.nombre AS requerimiento_estado,
            rhl.respuesta_estado_id,
            rres.nombre AS respuesta_estado,
            rhl.movimiento_tipo_id,
            rmt.nombre AS movimiento_tipo,
            rhl.usuario_accion_id,
            uacc.usuario AS usuario_accion,
            rhl.usuario_emisor_id,
            uem.usuario AS usuario_emisor,
            rhl.usuario_receptor_id,
            urec.usuario AS usuario_receptor,
            rhl.coe_origen_id,
            coo.siglas AS coe_origen,
            rhl.mesa_origen_id,
            moo.nombre AS mesa_origen,
            rhl.coe_destino_id,
            cod.siglas AS coe_destino,
            rhl.mesa_destino_id,
            mods.nombre AS mesa_destino,
            rhl.recurso_grupo_id,
            rg.nombre AS recurso_grupo,
            rhl.recurso_tipo_id,
            rt.nombre AS recurso_tipo,
            rhl.recurso_inventario_id,
            rhl.cantidad_solicitada,
            rhl.cantidad_asignada,
            rhl.motivo_id,
            rm.nombre AS motivo,
            rhl.respuesta_fecha
        FROM public.requerimiento_huella_logs rhl
        LEFT JOIN public.requerimiento_huella_log_acciones rac
            ON rhl.requerimiento_accion_log_id = rac.id
        LEFT JOIN public.requerimiento_huella_log_estados res
            ON rhl.requerimiento_estado_id = res.id
        LEFT JOIN public.requerimiento_huella_log_respuesta_estados rres
            ON rhl.respuesta_estado_id = rres.id
        LEFT JOIN public.requerimiento_huella_log_movimiento_tipos rmt
            ON rhl.movimiento_tipo_id = rmt.id
        LEFT JOIN public.requerimiento_huella_log_motivos rm
            ON rhl.motivo_id = rm.id
        LEFT JOIN public.usuarios uacc
            ON rhl.usuario_accion_id = uacc.id
        LEFT JOIN public.usuarios uem
            ON rhl.usuario_emisor_id = uem.id
        LEFT JOIN public.usuarios urec
            ON rhl.usuario_receptor_id = urec.id
        LEFT JOIN public.coes coo
            ON rhl.coe_origen_id = coo.id
        LEFT JOIN public.coes cod
            ON rhl.coe_destino_id = cod.id
        LEFT JOIN public.mesas moo
            ON rhl.mesa_origen_id = moo.id
        LEFT JOIN public.mesas mods
            ON rhl.mesa_destino_id = mods.id
        LEFT JOIN public.recurso_grupos rg
            ON rhl.recurso_grupo_id = rg.id
        LEFT JOIN public.recurso_tipos rt
            ON rhl.recurso_tipo_id = rt.id
    """


def _exists(table_name, item_id):
    query = db.text(f"SELECT 1 FROM public.{table_name} WHERE id = :id")
    return db.session.execute(query, {"id": item_id}).fetchone() is not None


def _validate_required_field(data, field_name):
    return field_name in data and data[field_name] is not None


def _validate_fk(data, field_name, table_name, required=False):
    field_exists = field_name in data and data[field_name] is not None
    if required and not field_exists:
        return f"{field_name} es requerido"
    if not field_exists:
        return None
    if not _exists(table_name, data[field_name]):
        return f"{field_name} no existe en {table_name}"
    return None


def _validate_cantidades(cantidad_solicitada, cantidad_asignada):
    if cantidad_solicitada is not None and cantidad_solicitada < 0:
        return "cantidad_solicitada debe ser mayor o igual a 0"
    if cantidad_asignada is not None and cantidad_asignada < 0:
        return "cantidad_asignada debe ser mayor o igual a 0"
    return None


def _siguiente_secuencia(requerimiento_recurso_id):
    query = db.text("""
        SELECT COALESCE(MAX(secuencia), 0) + 1 AS secuencia
        FROM public.requerimiento_huella_logs
        WHERE requerimiento_recurso_id = :requerimiento_recurso_id
    """)
    row = db.session.execute(
        query,
        {"requerimiento_recurso_id": requerimiento_recurso_id}
    ).fetchone()
    return row.secuencia if row else 1


@requerimiento_huella_logs_bp.route("/api/requerimiento-huella-logs", methods=["GET"])
def get_requerimiento_huella_logs():
    """Listar historial de huella de requerimientos
    ---
    tags:
      - Requerimiento Huella Logs
    parameters:
      - name: requerimiento_recurso_id
        in: query
        type: integer
        required: false
      - name: requerimiento_numero
        in: query
        type: string
        required: false
      - name: usuario_accion_id
        in: query
        type: integer
        required: false
      - name: usuario_emisor_id
        in: query
        type: integer
        required: false
      - name: usuario_receptor_id
        in: query
        type: integer
        required: false
      - name: requerimiento_estado_id
        in: query
        type: integer
        required: false
      - name: requerimiento_accion_log_id
        in: query
        type: integer
        required: false
      - name: respuesta_estado_id
        in: query
        type: integer
        required: false
      - name: limit
        in: query
        type: integer
        required: false
        description: Limite de registros (1-2000), por defecto 500
    responses:
      200:
        description: Lista de logs historicos
        schema:
          type: array
          items:
            type: object
            properties:
              id: {type: integer}
              requerimiento_recurso_id: {type: integer}
              requerimiento_numero: {type: string}
              secuencia: {type: integer}
              requerimiento_accion_log_id: {type: integer}
              requerimiento_accion: {type: string}
              requerimiento_estado_id: {type: integer}
              requerimiento_estado: {type: string}
              respuesta_estado_id: {type: integer}
              respuesta_estado: {type: string}
              movimiento_tipo_id: {type: integer}
              movimiento_tipo: {type: string}
              usuario_accion_id: {type: integer}
              usuario_accion: {type: string}
              usuario_emisor_id: {type: integer}
              usuario_emisor: {type: string}
              usuario_receptor_id: {type: integer}
              usuario_receptor: {type: string}
              coe_origen_id: {type: integer}
              coe_origen: {type: string}
              mesa_origen_id: {type: integer}
              mesa_origen: {type: string}
              coe_destino_id: {type: integer}
              coe_destino: {type: string}
              mesa_destino_id: {type: integer}
              mesa_destino: {type: string}
              recurso_grupo_id: {type: integer}
              recurso_grupo: {type: string}
              recurso_tipo_id: {type: integer}
              recurso_tipo: {type: string}
              recurso_inventario_id: {type: integer}
              cantidad_solicitada: {type: integer}
              cantidad_asignada: {type: integer}
              motivo_id: {type: integer}
              motivo: {type: string}
              respuesta_fecha: {type: string}
      400:
        description: Parametros invalidos
    """
    filters = []
    params = {}

    query_param_map = {
        "requerimiento_recurso_id": "rhl.requerimiento_recurso_id = :requerimiento_recurso_id",
        "requerimiento_numero": "rhl.requerimiento_numero = :requerimiento_numero",
        "usuario_accion_id": "rhl.usuario_accion_id = :usuario_accion_id",
        "usuario_emisor_id": "rhl.usuario_emisor_id = :usuario_emisor_id",
        "usuario_receptor_id": "rhl.usuario_receptor_id = :usuario_receptor_id",
        "requerimiento_estado_id": "rhl.requerimiento_estado_id = :requerimiento_estado_id",
        "requerimiento_accion_log_id": "rhl.requerimiento_accion_log_id = :requerimiento_accion_log_id",
        "respuesta_estado_id": "rhl.respuesta_estado_id = :respuesta_estado_id",
    }

    for param_name, condition in query_param_map.items():
        value = request.args.get(param_name)
        if value is None:
            continue
        if param_name == "requerimiento_numero":
            params[param_name] = value
        else:
            try:
                params[param_name] = int(value)
            except ValueError:
                return jsonify({"error": f"{param_name} debe ser numerico"}), 400
        filters.append(condition)

    limit_value = request.args.get("limit", "500")
    try:
        limit = int(limit_value)
    except ValueError:
        return jsonify({"error": "limit debe ser numerico"}), 400
    if limit < 1 or limit > 2000:
        return jsonify({"error": "limit debe estar entre 1 y 2000"}), 400
    params["limit"] = limit

    sql = _build_base_historial_query()
    if filters:
        sql += "\nWHERE " + " AND ".join(filters)
    sql += "\nORDER BY rhl.requerimiento_recurso_id DESC, rhl.secuencia DESC, rhl.id DESC"
    sql += "\nLIMIT :limit"

    result = db.session.execute(db.text(sql), params)
    return jsonify([_serialize_requerimiento_huella_log(row) for row in result])


@requerimiento_huella_logs_bp.route("/api/requerimiento-huella-logs/<int:id>", methods=["GET"])
def get_requerimiento_huella_log_by_id(id):
    """Obtener un log historico por ID
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
    sql = _build_base_historial_query() + "\nWHERE rhl.id = :id"
    row = db.session.execute(db.text(sql), {"id": id}).fetchone()
    if row is None:
        return jsonify({"error": "Log no encontrado"}), 404
    return jsonify(_serialize_requerimiento_huella_log(row))


@requerimiento_huella_logs_bp.route(
    "/api/requerimiento-huella-logs/requerimiento-recurso/<int:requerimiento_recurso_id>",
    methods=["GET"]
)
def get_requerimiento_huella_logs_by_requerimiento_recurso_id(requerimiento_recurso_id):
    """Obtener historial completo por requerimiento_recurso_id
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
        description: Historial ordenado por secuencia ascendente
        schema:
          type: array
          items:
            type: object
            properties:
              id: {type: integer}
              requerimiento_recurso_id: {type: integer}
              secuencia: {type: integer}
              requerimiento_accion: {type: string}
              requerimiento_estado: {type: string}
              respuesta_estado: {type: string}
              movimiento_tipo: {type: string}
              motivo: {type: string}
              respuesta_fecha: {type: string}
    """
    sql = _build_base_historial_query() + """
        WHERE rhl.requerimiento_recurso_id = :requerimiento_recurso_id
        ORDER BY rhl.secuencia ASC, rhl.id ASC
    """
    result = db.session.execute(
        db.text(sql),
        {"requerimiento_recurso_id": requerimiento_recurso_id}
    )
    return jsonify([_serialize_requerimiento_huella_log(row) for row in result])


@requerimiento_huella_logs_bp.route(
    "/api/requerimiento-huella-logs/requerimiento-numero/<string:requerimiento_numero>",
    methods=["GET"]
)
def get_requerimiento_huella_logs_by_requerimiento_numero(requerimiento_numero):
    """Obtener historial completo por requerimiento_numero
    ---
    tags:
      - Requerimiento Huella Logs
    parameters:
      - name: requerimiento_numero
        in: path
        type: string
        required: true
    responses:
      200:
        description: Historial del requerimiento agrupado por numero
        schema:
          type: array
          items:
            type: object
            properties:
              id: {type: integer}
              requerimiento_numero: {type: string}
              requerimiento_recurso_id: {type: integer}
              secuencia: {type: integer}
              requerimiento_accion: {type: string}
              requerimiento_estado: {type: string}
              respuesta_fecha: {type: string}
    """
    sql = _build_base_historial_query() + """
        WHERE rhl.requerimiento_numero = :requerimiento_numero
        ORDER BY rhl.requerimiento_recurso_id ASC, rhl.secuencia ASC, rhl.id ASC
    """
    result = db.session.execute(
        db.text(sql),
        {"requerimiento_numero": requerimiento_numero}
    )
    return jsonify([_serialize_requerimiento_huella_log(row) for row in result])


@requerimiento_huella_logs_bp.route("/api/requerimiento-huella-logs", methods=["POST"])
def create_requerimiento_huella_log():
    """Crear un registro de huella historica
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
            - requerimiento_recurso_id
            - requerimiento_accion_log_id
            - requerimiento_estado_id
            - usuario_accion_id
            - recurso_grupo_id
            - recurso_tipo_id
          properties:
            requerimiento_recurso_id: {type: integer}
            requerimiento_numero: {type: string}
            secuencia: {type: integer, description: Opcional. Si no se envia se autogenera secuencia incremental}
            requerimiento_accion_log_id: {type: integer}
            requerimiento_estado_id: {type: integer}
            respuesta_estado_id: {type: integer}
            movimiento_tipo_id: {type: integer}
            usuario_accion_id: {type: integer}
            usuario_emisor_id: {type: integer}
            usuario_receptor_id: {type: integer}
            coe_origen_id: {type: integer}
            mesa_origen_id: {type: integer}
            coe_destino_id: {type: integer}
            mesa_destino_id: {type: integer}
            recurso_grupo_id: {type: integer}
            recurso_tipo_id: {type: integer}
            recurso_inventario_id: {type: integer}
            cantidad_solicitada: {type: integer}
            cantidad_asignada: {type: integer}
            motivo_id: {type: integer}
            respuesta_fecha: {type: string}
    responses:
      201:
        description: Log historico creado
      400:
        description: Error de validacion
      409:
        description: Conflicto de secuencia unica
    """
    data = request.get_json() or {}

    required_fields = [
        "requerimiento_recurso_id",
        "requerimiento_accion_log_id",
        "requerimiento_estado_id",
        "usuario_accion_id",
        "recurso_grupo_id",
        "recurso_tipo_id",
    ]
    missing_fields = [field for field in required_fields if not _validate_required_field(data, field)]
    if missing_fields:
        return jsonify({"error": f"Campos requeridos faltantes: {', '.join(missing_fields)}"}), 400

    fk_errors = []
    fk_checks = [
        ("requerimiento_recurso_id", "requerimiento_recursos", True),
        ("requerimiento_accion_log_id", "requerimiento_huella_log_acciones", True),
        ("requerimiento_estado_id", "requerimiento_huella_log_estados", True),
        ("respuesta_estado_id", "requerimiento_huella_log_respuesta_estados", False),
        ("movimiento_tipo_id", "requerimiento_huella_log_movimiento_tipos", False),
        ("usuario_accion_id", "usuarios", True),
        ("usuario_emisor_id", "usuarios", False),
        ("usuario_receptor_id", "usuarios", False),
        ("coe_origen_id", "coes", False),
        ("mesa_origen_id", "mesas", False),
        ("coe_destino_id", "coes", False),
        ("mesa_destino_id", "mesas", False),
        ("recurso_grupo_id", "recurso_grupos", True),
        ("recurso_tipo_id", "recurso_tipos", True),
        ("recurso_inventario_id", "recursos_inventario", False),
        ("motivo_id", "requerimiento_huella_log_motivos", False),
    ]
    for field_name, table_name, required in fk_checks:
        error = _validate_fk(data, field_name, table_name, required=required)
        if error:
            fk_errors.append(error)

    if fk_errors:
        return jsonify({"error": "Validacion de llaves foraneas fallida", "detalles": fk_errors}), 400

    cantidad_solicitada = data.get("cantidad_solicitada", 1)
    cantidad_asignada = data.get("cantidad_asignada", 0)
    cantidad_error = _validate_cantidades(cantidad_solicitada, cantidad_asignada)
    if cantidad_error:
        return jsonify({"error": cantidad_error}), 400

    secuencia = data.get("secuencia")
    if secuencia is None:
        secuencia = _siguiente_secuencia(data["requerimiento_recurso_id"])
    elif secuencia < 1:
        return jsonify({"error": "secuencia debe ser mayor o igual a 1"}), 400

    respuesta_fecha = data.get("respuesta_fecha", datetime.now(timezone.utc))

    query = db.text("""
        INSERT INTO public.requerimiento_huella_logs (
            requerimiento_recurso_id,
            requerimiento_numero,
            secuencia,
            requerimiento_accion_log_id,
            requerimiento_estado_id,
            respuesta_estado_id,
            movimiento_tipo_id,
            usuario_accion_id,
            usuario_emisor_id,
            usuario_receptor_id,
            coe_origen_id,
            mesa_origen_id,
            coe_destino_id,
            mesa_destino_id,
            recurso_grupo_id,
            recurso_tipo_id,
            recurso_inventario_id,
            cantidad_solicitada,
            cantidad_asignada,
            motivo_id,
            respuesta_fecha
        )
        VALUES (
            :requerimiento_recurso_id,
            :requerimiento_numero,
            :secuencia,
            :requerimiento_accion_log_id,
            :requerimiento_estado_id,
            :respuesta_estado_id,
            :movimiento_tipo_id,
            :usuario_accion_id,
            :usuario_emisor_id,
            :usuario_receptor_id,
            :coe_origen_id,
            :mesa_origen_id,
            :coe_destino_id,
            :mesa_destino_id,
            :recurso_grupo_id,
            :recurso_tipo_id,
            :recurso_inventario_id,
            :cantidad_solicitada,
            :cantidad_asignada,
            :motivo_id,
            :respuesta_fecha
        )
        RETURNING id
    """)

    params = {
        "requerimiento_recurso_id": data["requerimiento_recurso_id"],
        "requerimiento_numero": data.get("requerimiento_numero"),
        "secuencia": secuencia,
        "requerimiento_accion_log_id": data["requerimiento_accion_log_id"],
        "requerimiento_estado_id": data["requerimiento_estado_id"],
        "respuesta_estado_id": data.get("respuesta_estado_id"),
        "movimiento_tipo_id": data.get("movimiento_tipo_id"),
        "usuario_accion_id": data["usuario_accion_id"],
        "usuario_emisor_id": data.get("usuario_emisor_id"),
        "usuario_receptor_id": data.get("usuario_receptor_id"),
        "coe_origen_id": data.get("coe_origen_id"),
        "mesa_origen_id": data.get("mesa_origen_id"),
        "coe_destino_id": data.get("coe_destino_id"),
        "mesa_destino_id": data.get("mesa_destino_id"),
        "recurso_grupo_id": data["recurso_grupo_id"],
        "recurso_tipo_id": data["recurso_tipo_id"],
        "recurso_inventario_id": data.get("recurso_inventario_id"),
        "cantidad_solicitada": cantidad_solicitada,
        "cantidad_asignada": cantidad_asignada,
        "motivo_id": data.get("motivo_id"),
        "respuesta_fecha": respuesta_fecha,
    }

    try:
        result = db.session.execute(query, params)
        row = result.fetchone()
        if row is None:
            db.session.rollback()
            return jsonify({"error": "No se pudo crear el log historico"}), 500
        log_id = row[0]
        db.session.commit()
    except IntegrityError as ex:
        db.session.rollback()
        message = str(getattr(ex, "orig", ex))
        if "uq_req_huella_secuencia" in message:
            return jsonify({
                "error": "Ya existe la secuencia para este requerimiento_recurso_id",
                "detalle": message
            }), 409
        if "chk_req_huella_cantidades" in message:
            return jsonify({
                "error": "Las cantidades deben ser mayores o iguales a 0",
                "detalle": message
            }), 400
        return jsonify({"error": "Error de integridad al crear log", "detalle": message}), 400

    sql = _build_base_historial_query() + "\nWHERE rhl.id = :id"
    created_row = db.session.execute(db.text(sql), {"id": log_id}).fetchone()
    if created_row is None:
        return jsonify({"error": "Log creado pero no encontrado"}), 500
    return jsonify(_serialize_requerimiento_huella_log(created_row)), 201


@requerimiento_huella_logs_bp.route("/api/requerimiento-huella-logs/<int:id>", methods=["PUT"])
def update_requerimiento_huella_log(id):
    """Actualizar un log historico
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
            secuencia: {type: integer}
            requerimiento_accion_log_id: {type: integer}
            requerimiento_estado_id: {type: integer}
            respuesta_estado_id: {type: integer}
            movimiento_tipo_id: {type: integer}
            usuario_accion_id: {type: integer}
            usuario_emisor_id: {type: integer}
            usuario_receptor_id: {type: integer}
            coe_origen_id: {type: integer}
            mesa_origen_id: {type: integer}
            coe_destino_id: {type: integer}
            mesa_destino_id: {type: integer}
            recurso_grupo_id: {type: integer}
            recurso_tipo_id: {type: integer}
            recurso_inventario_id: {type: integer}
            cantidad_solicitada: {type: integer}
            cantidad_asignada: {type: integer}
            motivo_id: {type: integer}
            respuesta_fecha: {type: string}
    responses:
      200:
        description: Log actualizado
      400:
        description: Error de validacion
      404:
        description: Log no encontrado
      409:
        description: Conflicto por secuencia unica
    """
    data = request.get_json() or {}
    actual = db.session.execute(
        db.text("SELECT * FROM public.requerimiento_huella_logs WHERE id = :id"),
        {"id": id}
    ).fetchone()
    if actual is None:
        return jsonify({"error": "Log no encontrado"}), 404

    candidate = {
        "requerimiento_recurso_id": data.get("requerimiento_recurso_id", actual.requerimiento_recurso_id),
        "requerimiento_numero": data.get("requerimiento_numero", actual.requerimiento_numero),
        "secuencia": data.get("secuencia", actual.secuencia),
        "requerimiento_accion_log_id": data.get("requerimiento_accion_log_id", actual.requerimiento_accion_log_id),
        "requerimiento_estado_id": data.get("requerimiento_estado_id", actual.requerimiento_estado_id),
        "respuesta_estado_id": data.get("respuesta_estado_id", actual.respuesta_estado_id),
        "movimiento_tipo_id": data.get("movimiento_tipo_id", actual.movimiento_tipo_id),
        "usuario_accion_id": data.get("usuario_accion_id", actual.usuario_accion_id),
        "usuario_emisor_id": data.get("usuario_emisor_id", actual.usuario_emisor_id),
        "usuario_receptor_id": data.get("usuario_receptor_id", actual.usuario_receptor_id),
        "coe_origen_id": data.get("coe_origen_id", actual.coe_origen_id),
        "mesa_origen_id": data.get("mesa_origen_id", actual.mesa_origen_id),
        "coe_destino_id": data.get("coe_destino_id", actual.coe_destino_id),
        "mesa_destino_id": data.get("mesa_destino_id", actual.mesa_destino_id),
        "recurso_grupo_id": data.get("recurso_grupo_id", actual.recurso_grupo_id),
        "recurso_tipo_id": data.get("recurso_tipo_id", actual.recurso_tipo_id),
        "recurso_inventario_id": data.get("recurso_inventario_id", actual.recurso_inventario_id),
        "cantidad_solicitada": data.get("cantidad_solicitada", actual.cantidad_solicitada),
        "cantidad_asignada": data.get("cantidad_asignada", actual.cantidad_asignada),
        "motivo_id": data.get("motivo_id", actual.motivo_id),
        "respuesta_fecha": data.get("respuesta_fecha", actual.respuesta_fecha),
    }

    if candidate["secuencia"] is None or candidate["secuencia"] < 1:
        return jsonify({"error": "secuencia debe ser mayor o igual a 1"}), 400

    cantidad_error = _validate_cantidades(candidate["cantidad_solicitada"], candidate["cantidad_asignada"])
    if cantidad_error:
        return jsonify({"error": cantidad_error}), 400

    fk_data = candidate
    fk_errors = []
    fk_checks = [
        ("requerimiento_recurso_id", "requerimiento_recursos", True),
        ("requerimiento_accion_log_id", "requerimiento_huella_log_acciones", True),
        ("requerimiento_estado_id", "requerimiento_huella_log_estados", True),
        ("respuesta_estado_id", "requerimiento_huella_log_respuesta_estados", False),
        ("movimiento_tipo_id", "requerimiento_huella_log_movimiento_tipos", False),
        ("usuario_accion_id", "usuarios", True),
        ("usuario_emisor_id", "usuarios", False),
        ("usuario_receptor_id", "usuarios", False),
        ("coe_origen_id", "coes", False),
        ("mesa_origen_id", "mesas", False),
        ("coe_destino_id", "coes", False),
        ("mesa_destino_id", "mesas", False),
        ("recurso_grupo_id", "recurso_grupos", True),
        ("recurso_tipo_id", "recurso_tipos", True),
        ("recurso_inventario_id", "recursos_inventario", False),
        ("motivo_id", "requerimiento_huella_log_motivos", False),
    ]
    for field_name, table_name, required in fk_checks:
        error = _validate_fk(fk_data, field_name, table_name, required=required)
        if error:
            fk_errors.append(error)
    if fk_errors:
        return jsonify({"error": "Validacion de llaves foraneas fallida", "detalles": fk_errors}), 400

    query = db.text("""
        UPDATE public.requerimiento_huella_logs
        SET requerimiento_recurso_id = :requerimiento_recurso_id,
            requerimiento_numero = :requerimiento_numero,
            secuencia = :secuencia,
            requerimiento_accion_log_id = :requerimiento_accion_log_id,
            requerimiento_estado_id = :requerimiento_estado_id,
            respuesta_estado_id = :respuesta_estado_id,
            movimiento_tipo_id = :movimiento_tipo_id,
            usuario_accion_id = :usuario_accion_id,
            usuario_emisor_id = :usuario_emisor_id,
            usuario_receptor_id = :usuario_receptor_id,
            coe_origen_id = :coe_origen_id,
            mesa_origen_id = :mesa_origen_id,
            coe_destino_id = :coe_destino_id,
            mesa_destino_id = :mesa_destino_id,
            recurso_grupo_id = :recurso_grupo_id,
            recurso_tipo_id = :recurso_tipo_id,
            recurso_inventario_id = :recurso_inventario_id,
            cantidad_solicitada = :cantidad_solicitada,
            cantidad_asignada = :cantidad_asignada,
            motivo_id = :motivo_id,
            respuesta_fecha = :respuesta_fecha
        WHERE id = :id
    """)
    params = {"id": id, **candidate}

    try:
        db.session.execute(query, params)
        db.session.commit()
    except IntegrityError as ex:
        db.session.rollback()
        message = str(getattr(ex, "orig", ex))
        if "uq_req_huella_secuencia" in message:
            return jsonify({
                "error": "Ya existe la secuencia para este requerimiento_recurso_id",
                "detalle": message
            }), 409
        if "chk_req_huella_cantidades" in message:
            return jsonify({
                "error": "Las cantidades deben ser mayores o iguales a 0",
                "detalle": message
            }), 400
        return jsonify({"error": "Error de integridad al actualizar log", "detalle": message}), 400

    sql = _build_base_historial_query() + "\nWHERE rhl.id = :id"
    updated = db.session.execute(db.text(sql), {"id": id}).fetchone()
    if updated is None:
        return jsonify({"error": "Log no encontrado despues de actualizar"}), 500
    return jsonify(_serialize_requerimiento_huella_log(updated))


@requerimiento_huella_logs_bp.route("/api/requerimiento-huella-logs/<int:id>", methods=["DELETE"])
def delete_requerimiento_huella_log(id):
    """Eliminar un log historico
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
        db.text("DELETE FROM public.requerimiento_huella_logs WHERE id = :id"),
        {"id": id}
    )
    if getattr(result, "rowcount", 0) == 0:
        return jsonify({"error": "Log no encontrado"}), 404
    db.session.commit()
    return jsonify({"mensaje": "Log eliminado correctamente"})
