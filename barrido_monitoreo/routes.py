from datetime import datetime, timezone

from flask import jsonify, request

from barrido_monitoreo import barrido_monitoreo_bp
from models import db


TABLE_NAME = "public.barrido_monitoreo"


def _to_float_optional(value):
    if value is None or value == "":
        return None
    return float(value)


def _to_iso_optional(value):
    if value is None or value == "":
        return None
    if hasattr(value, "isoformat"):
        return value.isoformat()
    return str(value)


def _serialize_barrido_monitoreo(row):
    return {
        "id": getattr(row, "id", None),
        "barrido_id": getattr(row, "barrido_id", None),
        "barrido_evento_tipo_id": getattr(row, "barrido_evento_tipo_id", None),
        "barrido_evento_tipo_nombre": getattr(row, "barrido_evento_tipo_nombre", None),
        "barrido_evento_fecha": _to_iso_optional(getattr(row, "barrido_evento_fecha", None)),
        "emergencia_id": getattr(row, "emergencia_id", None),
        "emergencia_nombre": getattr(row, "emergencia_nombre", None),
        "monitoreo_fecha": _to_iso_optional(getattr(row, "monitoreo_fecha", None)),
        "provincia_id": getattr(row, "provincia_id", None),
        "provincia_nombre": getattr(row, "provincia_nombre", None),
        "canton_id": getattr(row, "canton_id", None),
        "canton_nombre": getattr(row, "canton_nombre", None),
        "parroquia_id": getattr(row, "parroquia_id", None),
        "parroquia_nombre": getattr(row, "parroquia_nombre", None),
        "sector": getattr(row, "sector", None),
        "longitud": _to_float_optional(getattr(row, "longitud", None)),
        "latitud": _to_float_optional(getattr(row, "latitud", None)),
        "intensidad_id": getattr(row, "intensidad_id", None),
        "intensidad_orden": getattr(row, "intensidad_orden", None),
        "intensidad_nombre": getattr(row, "intensidad_nombre", None),
        "intensidad_descripcion": getattr(row, "intensidad_descripcion", None),
        "fuente": getattr(row, "fuente", None),
        "observaciones": getattr(row, "observaciones", None),
        "activo": getattr(row, "activo", None),
        "creador": getattr(row, "creador", None),
        "creacion": _to_iso_optional(getattr(row, "creacion", None)),
        "modificador": getattr(row, "modificador", None),
        "modificacion": _to_iso_optional(getattr(row, "modificacion", None)),
    }


def _select_barrido_monitoreo(where_clause="", order_by="bm.id ASC"):
    return db.text(
        f"""
        SELECT
            bm.id,
            bm.barrido_id,
            b.evento_tipo_id AS barrido_evento_tipo_id,
            et.nombre AS barrido_evento_tipo_nombre,
            b.evento_fecha AS barrido_evento_fecha,
            b.emergencia_id,
            e.nombre AS emergencia_nombre,
            bm.monitoreo_fecha,
            bm.provincia_id,
            p.nombre AS provincia_nombre,
            bm.canton_id,
            c.nombre AS canton_nombre,
            bm.parroquia_id,
            q.nombre AS parroquia_nombre,
            bm.sector,
            bm.longitud,
            bm.latitud,
            bm.intensidad_id,
            bi.orden AS intensidad_orden,
            bi.nombre AS intensidad_nombre,
            bi.descripcion AS intensidad_descripcion,
            bm.fuente,
            bm.observaciones,
            bm.activo,
            bm.creador,
            bm.creacion,
            bm.modificador,
            bm.modificacion
        FROM {TABLE_NAME} bm
        LEFT JOIN public.barridos b
            ON b.id = bm.barrido_id
        LEFT JOIN public.emergencias e
            ON e.id = b.emergencia_id
        LEFT JOIN public.evento_tipos et
            ON et.id = b.evento_tipo_id
        LEFT JOIN public.barrido_intensidad bi
            ON bi.id = bm.intensidad_id
        LEFT JOIN public.provincias p
            ON p.id = bm.provincia_id
        LEFT JOIN public.cantones c
            ON c.provincia_id = bm.provincia_id
           AND c.id = bm.canton_id
        LEFT JOIN public.parroquias q
            ON q.provincia_id = bm.provincia_id
           AND q.canton_id = bm.canton_id
           AND q.id = bm.parroquia_id
        {where_clause}
        ORDER BY {order_by}
        """
    )


def _get_barrido_monitoreo_by_id(item_id):
    query = _select_barrido_monitoreo("WHERE bm.id = :id", "bm.id ASC")
    return db.session.execute(query, {"id": item_id}).fetchone()


def _get_latest_barrido_id():
    query = db.text(
        """
        SELECT id
        FROM public.barridos
        WHERE COALESCE(activo, true) = true
        ORDER BY evento_fecha DESC, id DESC
        LIMIT 1
        """
    )
    row = db.session.execute(query).fetchone()
    return row.id if row else None


def _get_monitoreo_base_values(item_id):
    query = db.text(
        f"""
        SELECT barrido_id, intensidad_id
        FROM {TABLE_NAME}
        WHERE id = :id
        """
    )
    return db.session.execute(query, {"id": item_id}).fetchone()


def _validate_intensidad_for_barrido(barrido_id, intensidad_id):
    query = db.text(
        """
        SELECT
            b.evento_tipo_id AS barrido_evento_tipo_id,
            bi.evento_tipo_id AS intensidad_evento_tipo_id
        FROM public.barridos b
        LEFT JOIN public.barrido_intensidad bi
            ON bi.id = :intensidad_id
        WHERE b.id = :barrido_id
        """
    )
    row = db.session.execute(
        query,
        {"barrido_id": barrido_id, "intensidad_id": intensidad_id},
    ).fetchone()
    if not row:
        return "Barrido no encontrado"
    if row.intensidad_evento_tipo_id is None:
        return "Intensidad de barrido no encontrada"
    if row.barrido_evento_tipo_id != row.intensidad_evento_tipo_id:
        return "La intensidad_id no corresponde al tipo de evento del barrido"
    return None


@barrido_monitoreo_bp.route("/api/barrido_monitoreo", methods=["GET"])
def get_barrido_monitoreos():
    """Listar monitoreos de barrido.
    ---
    tags:
      - Barrido Monitoreo
    summary: Listar monitoreos de barrido
    description: Devuelve todos los registros de `barrido_monitoreo` ordenados por `id` ascendente. Incluye datos del barrido cabecera, ubicacion, intensidad, fuente, observaciones y auditoria.
    responses:
      200:
        description: Lista de monitoreos de barrido
        schema:
          type: array
          items:
            type: object
            properties:
              id: {type: integer, description: Identificador unico del monitoreo}
              barrido_id: {type: integer, description: ID del barrido cabecera}
              barrido_evento_tipo_id: {type: integer, description: Tipo de evento del barrido}
              barrido_evento_tipo_nombre: {type: string, description: Nombre del tipo de evento del barrido, nullable: true}
              barrido_evento_fecha: {type: string, format: date-time, description: Fecha del evento del barrido}
              emergencia_id: {type: integer, description: ID de la emergencia relacionada, nullable: true}
              emergencia_nombre: {type: string, description: Nombre de la emergencia, nullable: true}
              monitoreo_fecha: {type: string, format: date-time, description: Fecha del monitoreo}
              provincia_id: {type: integer, description: ID de provincia monitoreada}
              provincia_nombre: {type: string, description: Nombre de provincia, nullable: true}
              canton_id: {type: integer, description: ID de canton monitoreado}
              canton_nombre: {type: string, description: Nombre de canton, nullable: true}
              parroquia_id: {type: integer, description: ID de parroquia monitoreada, nullable: true}
              parroquia_nombre: {type: string, description: Nombre de parroquia, nullable: true}
              sector: {type: string, description: Sector monitoreado}
              longitud: {type: number, format: float, description: Longitud del punto monitoreado}
              latitud: {type: number, format: float, description: Latitud del punto monitoreado}
              intensidad_id: {type: integer, description: ID de intensidad reportada}
              intensidad_orden: {type: integer, description: Orden de la intensidad, nullable: true}
              intensidad_nombre: {type: string, description: Nombre de la intensidad, nullable: true}
              intensidad_descripcion: {type: string, description: Descripcion de la intensidad, nullable: true}
              fuente: {type: string, description: Fuente de informacion, nullable: true}
              observaciones: {type: string, description: Observaciones del monitoreo, nullable: true}
              activo: {type: boolean, description: Estado activo del registro}
              creador: {type: string, description: Usuario creador, nullable: true}
              creacion: {type: string, format: date-time, description: Fecha de creacion}
              modificador: {type: string, description: Usuario modificador, nullable: true}
              modificacion: {type: string, format: date-time, description: Fecha de modificacion, nullable: true}
      500:
        description: Error inesperado al consultar monitoreos de barrido
    """
    result = db.session.execute(_select_barrido_monitoreo())
    return jsonify([_serialize_barrido_monitoreo(row) for row in result])


@barrido_monitoreo_bp.route("/api/barrido_monitoreo/barrido/reciente", methods=["GET"])
def get_barrido_monitoreos_by_barrido_reciente():
    """Listar monitoreos del barrido mas reciente.
    ---
    tags:
      - Barrido Monitoreo
    summary: Listar monitoreos del barrido mas reciente
    description: Busca el barrido activo mas reciente y devuelve sus registros activos de `barrido_monitoreo`, ordenados por fecha de monitoreo descendente.
    responses:
      200:
        description: Lista de monitoreos activos del barrido mas reciente
      404:
        description: No existe un barrido activo para consultar monitoreos
      500:
        description: Error inesperado al consultar monitoreos del barrido mas reciente
    """
    barrido_id = _get_latest_barrido_id()
    if barrido_id is None:
        return jsonify({"error": "No existe un barrido activo"}), 404

    query = _select_barrido_monitoreo(
        "WHERE bm.barrido_id = :barrido_id AND COALESCE(bm.activo, true) = true",
        "bm.monitoreo_fecha DESC, bm.id DESC",
    )
    result = db.session.execute(query, {"barrido_id": barrido_id})
    return jsonify([_serialize_barrido_monitoreo(row) for row in result])


@barrido_monitoreo_bp.route("/api/barrido_monitoreo/barrido/<int:barrido_id>", methods=["GET"])
def get_barrido_monitoreos_by_barrido(barrido_id):
    """Listar monitoreos por barrido.
    ---
    tags:
      - Barrido Monitoreo
    summary: Listar monitoreos por barrido
    description: Devuelve los registros activos de `barrido_monitoreo` asociados al `barrido_id` indicado.
    parameters:
      - name: barrido_id
        in: path
        type: integer
        required: true
        description: Identificador del barrido cabecera
    responses:
      200:
        description: Lista de monitoreos activos del barrido
      500:
        description: Error inesperado al consultar monitoreos por barrido
    """
    query = _select_barrido_monitoreo(
        "WHERE bm.barrido_id = :barrido_id AND COALESCE(bm.activo, true) = true",
        "bm.monitoreo_fecha DESC, bm.id DESC",
    )
    result = db.session.execute(query, {"barrido_id": barrido_id})
    return jsonify([_serialize_barrido_monitoreo(row) for row in result])


@barrido_monitoreo_bp.route("/api/barrido_monitoreo/<int:id>", methods=["GET"])
def get_barrido_monitoreo(id):
    """Obtener monitoreo de barrido por ID.
    ---
    tags:
      - Barrido Monitoreo
    summary: Obtener monitoreo de barrido por ID
    description: Devuelve el registro de `barrido_monitoreo` identificado por `id`, incluyendo datos descriptivos del barrido, ubicacion e intensidad.
    parameters:
      - name: id
        in: path
        type: integer
        required: true
        description: Identificador unico del monitoreo
    responses:
      200:
        description: Monitoreo de barrido encontrado
      404:
        description: Monitoreo de barrido no encontrado
      500:
        description: Error inesperado al consultar el monitoreo de barrido
    """
    item = _get_barrido_monitoreo_by_id(id)
    if not item:
        return jsonify({"error": "Monitoreo de barrido no encontrado"}), 404
    return jsonify(_serialize_barrido_monitoreo(item))


@barrido_monitoreo_bp.route("/api/barrido_monitoreo", methods=["POST"])
def create_barrido_monitoreo():
    """Crear monitoreo de barrido.
    ---
    tags:
      - Barrido Monitoreo
    summary: Crear monitoreo de barrido
    description: Inserta un registro de monitoreo. Si no se envia `barrido_id`, el endpoint toma automaticamente el barrido activo mas reciente por `evento_fecha` e `id`. La `intensidad_id` debe pertenecer al mismo `evento_tipo_id` del barrido.
    consumes:
      - application/json
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          required:
            - provincia_id
            - canton_id
            - sector
            - intensidad_id
          properties:
            barrido_id: {type: integer, description: ID del barrido cabecera. Si se omite, usa el barrido activo mas reciente}
            monitoreo_fecha: {type: string, format: date-time, description: Fecha del monitoreo. Si se omite, usa la fecha actual}
            provincia_id: {type: integer, description: ID de provincia monitoreada}
            canton_id: {type: integer, description: ID de canton monitoreado}
            parroquia_id: {type: integer, description: ID de parroquia monitoreada, nullable: true}
            sector: {type: string, description: Sector monitoreado}
            longitud: {type: number, format: float, default: 0, description: Longitud del punto monitoreado}
            latitud: {type: number, format: float, default: 0, description: Latitud del punto monitoreado}
            intensidad_id: {type: integer, description: ID de intensidad reportada}
            fuente: {type: string, description: Fuente de informacion, nullable: true}
            observaciones: {type: string, description: Observaciones del monitoreo, nullable: true}
            activo: {type: boolean, default: true, description: Estado activo del registro}
            creador: {type: string, description: Usuario creador}
            modificador: {type: string, description: Usuario modificador}
    responses:
      201:
        description: Monitoreo de barrido creado correctamente
      400:
        description: Campos requeridos faltantes, barrido inexistente o intensidad incompatible
      500:
        description: Error inesperado al crear el monitoreo de barrido
    """
    data = request.get_json(silent=True) or {}
    required_fields = ["provincia_id", "canton_id", "sector", "intensidad_id"]
    missing_fields = [field for field in required_fields if data.get(field) is None]
    if missing_fields:
        return jsonify({"error": f"Campos requeridos faltantes: {', '.join(missing_fields)}"}), 400

    barrido_id = data.get("barrido_id")
    if barrido_id is None:
        barrido_id = _get_latest_barrido_id()
    if barrido_id is None:
        return jsonify({"error": "No existe un barrido activo para iniciar el monitoreo"}), 400

    validation_error = _validate_intensidad_for_barrido(barrido_id, data["intensidad_id"])
    if validation_error:
        return jsonify({"error": validation_error}), 400

    now = datetime.now(timezone.utc)
    creador = data.get("creador", "Sistema")
    modificador = data.get("modificador", creador)

    query = db.text(
        f"""
        INSERT INTO {TABLE_NAME} (
            barrido_id,
            monitoreo_fecha,
            provincia_id,
            canton_id,
            parroquia_id,
            sector,
            longitud,
            latitud,
            intensidad_id,
            fuente,
            observaciones,
            activo,
            creador,
            creacion,
            modificador,
            modificacion
        )
        VALUES (
            :barrido_id,
            :monitoreo_fecha,
            :provincia_id,
            :canton_id,
            :parroquia_id,
            :sector,
            :longitud,
            :latitud,
            :intensidad_id,
            :fuente,
            :observaciones,
            :activo,
            :creador,
            :creacion,
            :modificador,
            :modificacion
        )
        RETURNING id
        """
    )

    try:
        result = db.session.execute(
            query,
            {
                "barrido_id": barrido_id,
                "monitoreo_fecha": data.get("monitoreo_fecha", now),
                "provincia_id": data["provincia_id"],
                "canton_id": data["canton_id"],
                "parroquia_id": data.get("parroquia_id"),
                "sector": data["sector"],
                "longitud": data.get("longitud", 0),
                "latitud": data.get("latitud", 0),
                "intensidad_id": data["intensidad_id"],
                "fuente": data.get("fuente"),
                "observaciones": data.get("observaciones"),
                "activo": data.get("activo", True),
                "creador": creador,
                "creacion": now,
                "modificador": modificador,
                "modificacion": now,
            },
        )
        row = result.fetchone()
        if row is None:
            db.session.rollback()
            return jsonify({"error": "No se pudo crear el monitoreo de barrido"}), 500
        item_id = row[0]
        db.session.commit()
    except Exception as exc:
        db.session.rollback()
        return jsonify({"error": "Error al crear el monitoreo de barrido", "detalle": str(exc)}), 500

    item = _get_barrido_monitoreo_by_id(item_id)
    if not item:
        return jsonify({"error": "Monitoreo de barrido no encontrado"}), 404
    return jsonify(_serialize_barrido_monitoreo(item)), 201


@barrido_monitoreo_bp.route("/api/barrido_monitoreo/<int:id>", methods=["PUT"])
def update_barrido_monitoreo(id):
    """Actualizar monitoreo de barrido.
    ---
    tags:
      - Barrido Monitoreo
    summary: Actualizar monitoreo de barrido
    description: Actualiza de forma parcial un registro de `barrido_monitoreo`. Si se cambia `barrido_id` o `intensidad_id`, valida que la intensidad pertenezca al tipo de evento del barrido resultante.
    consumes:
      - application/json
    parameters:
      - name: id
        in: path
        type: integer
        required: true
        description: Identificador unico del monitoreo
      - in: body
        name: body
        required: true
        schema:
          type: object
          properties:
            barrido_id: {type: integer, description: ID del barrido cabecera}
            monitoreo_fecha: {type: string, format: date-time, description: Fecha del monitoreo}
            provincia_id: {type: integer, description: ID de provincia monitoreada}
            canton_id: {type: integer, description: ID de canton monitoreado}
            parroquia_id: {type: integer, description: ID de parroquia monitoreada, nullable: true}
            sector: {type: string, description: Sector monitoreado}
            longitud: {type: number, format: float, description: Longitud del punto monitoreado}
            latitud: {type: number, format: float, description: Latitud del punto monitoreado}
            intensidad_id: {type: integer, description: ID de intensidad reportada}
            fuente: {type: string, description: Fuente de informacion, nullable: true}
            observaciones: {type: string, description: Observaciones del monitoreo, nullable: true}
            activo: {type: boolean, description: Estado activo del registro}
            modificador: {type: string, description: Usuario modificador}
    responses:
      200:
        description: Monitoreo de barrido actualizado correctamente
      400:
        description: No se enviaron campos validos o la intensidad no corresponde al barrido
      404:
        description: Monitoreo de barrido no encontrado
      500:
        description: Error inesperado al actualizar el monitoreo de barrido
    """
    data = request.get_json(silent=True) or {}
    existing = _get_monitoreo_base_values(id)
    if not existing:
        return jsonify({"error": "Monitoreo de barrido no encontrado"}), 404

    target_barrido_id = data.get("barrido_id", existing.barrido_id)
    target_intensidad_id = data.get("intensidad_id", existing.intensidad_id)
    if "barrido_id" in data or "intensidad_id" in data:
        validation_error = _validate_intensidad_for_barrido(target_barrido_id, target_intensidad_id)
        if validation_error:
            return jsonify({"error": validation_error}), 400

    now = datetime.now(timezone.utc)
    updatable_fields = [
        "barrido_id",
        "monitoreo_fecha",
        "provincia_id",
        "canton_id",
        "parroquia_id",
        "sector",
        "longitud",
        "latitud",
        "intensidad_id",
        "fuente",
        "observaciones",
        "activo",
    ]

    params = {
        "id": id,
        "modificador": data.get("modificador", "Sistema"),
        "modificacion": now,
    }
    update_fields = []
    for field in updatable_fields:
        if field in data:
            update_fields.append(f"{field} = :{field}")
            params[field] = data[field]

    if not update_fields:
        return jsonify({"error": "No se enviaron campos validos para actualizar"}), 400

    update_fields.append("modificador = :modificador")
    update_fields.append("modificacion = :modificacion")

    query = db.text(
        f"""
        UPDATE {TABLE_NAME}
        SET {", ".join(update_fields)}
        WHERE id = :id
        """
    )

    try:
        result = db.session.execute(query, params)
        if getattr(result, "rowcount", 0) == 0:
            db.session.rollback()
            return jsonify({"error": "Monitoreo de barrido no encontrado"}), 404
        db.session.commit()
    except Exception as exc:
        db.session.rollback()
        return jsonify({"error": "Error al actualizar el monitoreo de barrido", "detalle": str(exc)}), 500

    item = _get_barrido_monitoreo_by_id(id)
    if not item:
        return jsonify({"error": "Monitoreo de barrido no encontrado"}), 404
    return jsonify(_serialize_barrido_monitoreo(item))


@barrido_monitoreo_bp.route("/api/barrido_monitoreo/<int:id>", methods=["DELETE"])
def delete_barrido_monitoreo(id):
    """Eliminar monitoreo de barrido.
    ---
    tags:
      - Barrido Monitoreo
    summary: Eliminar monitoreo de barrido
    description: Elimina fisicamente el registro de `barrido_monitoreo` identificado por `id`.
    parameters:
      - name: id
        in: path
        type: integer
        required: true
        description: Identificador unico del monitoreo
    responses:
      200:
        description: Monitoreo de barrido eliminado correctamente
      404:
        description: Monitoreo de barrido no encontrado
      500:
        description: Error inesperado al eliminar el monitoreo de barrido
    """
    try:
        result = db.session.execute(
            db.text(f"DELETE FROM {TABLE_NAME} WHERE id = :id"),
            {"id": id},
        )
        if getattr(result, "rowcount", 0) == 0:
            db.session.rollback()
            return jsonify({"error": "Monitoreo de barrido no encontrado"}), 404
        db.session.commit()
    except Exception as exc:
        db.session.rollback()
        return jsonify({"error": "Error al eliminar el monitoreo de barrido", "detalle": str(exc)}), 500

    return jsonify({"mensaje": "Monitoreo de barrido eliminado correctamente"})
