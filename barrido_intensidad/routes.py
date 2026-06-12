from datetime import datetime, timezone

from flask import jsonify, request

from barrido_intensidad import barrido_intensidad_bp
from models import db


TABLE_NAME = "public.barrido_intensidad"


def _to_iso_optional(value):
    if value is None or value == "":
        return None
    if hasattr(value, "isoformat"):
        return value.isoformat()
    return str(value)


def _serialize_barrido_intensidad(row):
    item = {
        "id": getattr(row, "id", None),
        "evento_tipo_id": getattr(row, "evento_tipo_id", None),
        "orden": getattr(row, "orden", None),
        "nombre": getattr(row, "nombre", None),
        "descripcion": getattr(row, "descripcion", None),
        "activo": getattr(row, "activo", None),
        "creador": getattr(row, "creador", None),
        "creacion": _to_iso_optional(getattr(row, "creacion", None)),
        "modificador": getattr(row, "modificador", None),
        "modificacion": _to_iso_optional(getattr(row, "modificacion", None)),
    }

    optional_fields = ["evento_tipo_nombre", "barrido_id", "barrido_evento_fecha"]
    for field in optional_fields:
        if hasattr(row, field):
            value = getattr(row, field)
            item[field] = _to_iso_optional(value) if field == "barrido_evento_fecha" else value

    return item


def _select_barrido_intensidad(where_clause="", order_by="bi.evento_tipo_id ASC, bi.orden ASC, bi.id ASC"):
    return db.text(
        f"""
        SELECT
            bi.id,
            bi.evento_tipo_id,
            et.nombre AS evento_tipo_nombre,
            bi.orden,
            bi.nombre,
            bi.descripcion,
            bi.activo,
            bi.creador,
            bi.creacion,
            bi.modificador,
            bi.modificacion
        FROM {TABLE_NAME} bi
        LEFT JOIN public.evento_tipos et
            ON et.id = bi.evento_tipo_id
        {where_clause}
        ORDER BY {order_by}
        """
    )


def _get_barrido_intensidad_by_id(item_id):
    query = _select_barrido_intensidad("WHERE bi.id = :id", "bi.id ASC")
    return db.session.execute(query, {"id": item_id}).fetchone()


def _get_latest_barrido():
    query = db.text(
        """
        SELECT
            b.id AS barrido_id,
            b.evento_tipo_id,
            b.evento_fecha AS barrido_evento_fecha
        FROM public.barridos b
        WHERE COALESCE(b.activo, true) = true
        ORDER BY b.evento_fecha DESC, b.id DESC
        LIMIT 1
        """
    )
    return db.session.execute(query).fetchone()


def _get_barrido_evento_tipo(barrido_id):
    query = db.text(
        """
        SELECT
            b.id AS barrido_id,
            b.evento_tipo_id,
            b.evento_fecha AS barrido_evento_fecha
        FROM public.barridos b
        WHERE b.id = :barrido_id
        """
    )
    return db.session.execute(query, {"barrido_id": barrido_id}).fetchone()


def _list_by_evento_tipo(evento_tipo_id, barrido=None):
    query = _select_barrido_intensidad(
        "WHERE bi.evento_tipo_id = :evento_tipo_id AND COALESCE(bi.activo, true) = true",
        "bi.orden ASC, bi.id ASC",
    )
    rows = db.session.execute(query, {"evento_tipo_id": evento_tipo_id})
    items = [_serialize_barrido_intensidad(row) for row in rows]
    if barrido is not None:
        for item in items:
            item["barrido_id"] = barrido.barrido_id
            item["barrido_evento_fecha"] = _to_iso_optional(barrido.barrido_evento_fecha)
    return items


@barrido_intensidad_bp.route("/api/barrido_intensidad", methods=["GET"])
def get_barrido_intensidades():
    """Listar intensidades de barrido.
    ---
    tags:
      - Barrido Intensidad
    summary: Listar intensidades de barrido
    description: Devuelve todos los registros del catalogo `barrido_intensidad`, ordenados por tipo de evento, orden e id.
    responses:
      200:
        description: Lista de intensidades de barrido
        schema:
          type: array
          items:
            type: object
            properties:
              id: {type: integer, description: Identificador unico de la intensidad}
              evento_tipo_id: {type: integer, description: ID del tipo de evento al que aplica la intensidad}
              evento_tipo_nombre: {type: string, description: Nombre del tipo de evento, nullable: true}
              orden: {type: integer, description: Orden de presentacion de la intensidad}
              nombre: {type: string, description: Nombre de la intensidad}
              descripcion: {type: string, description: Descripcion de la intensidad, nullable: true}
              activo: {type: boolean, description: Estado activo del catalogo}
              creador: {type: string, description: Usuario creador, nullable: true}
              creacion: {type: string, format: date-time, description: Fecha de creacion}
              modificador: {type: string, description: Usuario modificador, nullable: true}
              modificacion: {type: string, format: date-time, description: Fecha de modificacion, nullable: true}
      500:
        description: Error inesperado al consultar las intensidades de barrido
    """
    result = db.session.execute(_select_barrido_intensidad())
    return jsonify([_serialize_barrido_intensidad(row) for row in result])


@barrido_intensidad_bp.route("/api/barrido_intensidad/evento_tipo/<int:evento_tipo_id>", methods=["GET"])
def get_barrido_intensidades_by_evento_tipo(evento_tipo_id):
    """Listar intensidades por tipo de evento.
    ---
    tags:
      - Barrido Intensidad
    summary: Listar intensidades por tipo de evento
    description: Devuelve las intensidades activas disponibles para el `evento_tipo_id` indicado, ordenadas por el campo `orden`.
    parameters:
      - name: evento_tipo_id
        in: path
        type: integer
        required: true
        description: Identificador del tipo de evento
    responses:
      200:
        description: Lista de intensidades activas para el tipo de evento
        schema:
          type: array
          items:
            type: object
            properties:
              id: {type: integer, description: Identificador unico de la intensidad}
              evento_tipo_id: {type: integer, description: ID del tipo de evento al que aplica la intensidad}
              evento_tipo_nombre: {type: string, description: Nombre del tipo de evento, nullable: true}
              orden: {type: integer, description: Orden de presentacion de la intensidad}
              nombre: {type: string, description: Nombre de la intensidad}
              descripcion: {type: string, description: Descripcion de la intensidad, nullable: true}
              activo: {type: boolean, description: Estado activo del catalogo}
      500:
        description: Error inesperado al consultar intensidades por tipo de evento
    """
    return jsonify(_list_by_evento_tipo(evento_tipo_id))


@barrido_intensidad_bp.route("/api/barrido_intensidad/barrido/reciente", methods=["GET"])
def get_barrido_intensidades_by_barrido_reciente():
    """Listar intensidades del barrido mas reciente.
    ---
    tags:
      - Barrido Intensidad
    summary: Listar intensidades del barrido mas reciente
    description: Busca el barrido activo mas reciente y devuelve el catalogo de intensidades activas correspondiente a su `evento_tipo_id`. Sirve para iniciar el monitoreo sin que el cliente tenga que resolver primero el tipo de evento.
    responses:
      200:
        description: Lista de intensidades activas del barrido mas reciente
        schema:
          type: array
          items:
            type: object
            properties:
              id: {type: integer, description: Identificador unico de la intensidad}
              barrido_id: {type: integer, description: ID del barrido activo mas reciente}
              barrido_evento_fecha: {type: string, format: date-time, description: Fecha del evento del barrido}
              evento_tipo_id: {type: integer, description: ID del tipo de evento al que aplica la intensidad}
              evento_tipo_nombre: {type: string, description: Nombre del tipo de evento, nullable: true}
              orden: {type: integer, description: Orden de presentacion de la intensidad}
              nombre: {type: string, description: Nombre de la intensidad}
              descripcion: {type: string, description: Descripcion de la intensidad, nullable: true}
              activo: {type: boolean, description: Estado activo del catalogo}
      404:
        description: No existe un barrido activo para resolver el catalogo
      500:
        description: Error inesperado al consultar intensidades del barrido mas reciente
    """
    barrido = _get_latest_barrido()
    if not barrido:
        return jsonify({"error": "No existe un barrido activo"}), 404
    return jsonify(_list_by_evento_tipo(barrido.evento_tipo_id, barrido))


@barrido_intensidad_bp.route("/api/barrido_intensidad/barrido/<int:barrido_id>", methods=["GET"])
def get_barrido_intensidades_by_barrido(barrido_id):
    """Listar intensidades por barrido.
    ---
    tags:
      - Barrido Intensidad
    summary: Listar intensidades por barrido
    description: Devuelve las intensidades activas que corresponden al `evento_tipo_id` de la cabecera de barrido indicada.
    parameters:
      - name: barrido_id
        in: path
        type: integer
        required: true
        description: Identificador del barrido
    responses:
      200:
        description: Lista de intensidades activas para el barrido
        schema:
          type: array
          items:
            type: object
            properties:
              id: {type: integer, description: Identificador unico de la intensidad}
              barrido_id: {type: integer, description: ID del barrido consultado}
              barrido_evento_fecha: {type: string, format: date-time, description: Fecha del evento del barrido}
              evento_tipo_id: {type: integer, description: ID del tipo de evento al que aplica la intensidad}
              evento_tipo_nombre: {type: string, description: Nombre del tipo de evento, nullable: true}
              orden: {type: integer, description: Orden de presentacion de la intensidad}
              nombre: {type: string, description: Nombre de la intensidad}
              descripcion: {type: string, description: Descripcion de la intensidad, nullable: true}
              activo: {type: boolean, description: Estado activo del catalogo}
      404:
        description: Barrido no encontrado
      500:
        description: Error inesperado al consultar intensidades por barrido
    """
    barrido = _get_barrido_evento_tipo(barrido_id)
    if not barrido:
        return jsonify({"error": "Barrido no encontrado"}), 404
    return jsonify(_list_by_evento_tipo(barrido.evento_tipo_id, barrido))


@barrido_intensidad_bp.route("/api/barrido_intensidad/<int:id>", methods=["GET"])
def get_barrido_intensidad(id):
    """Obtener intensidad de barrido por ID.
    ---
    tags:
      - Barrido Intensidad
    summary: Obtener intensidad de barrido por ID
    description: Devuelve un registro del catalogo `barrido_intensidad` identificado por `id`.
    parameters:
      - name: id
        in: path
        type: integer
        required: true
        description: Identificador unico de la intensidad
    responses:
      200:
        description: Intensidad de barrido encontrada
      404:
        description: Intensidad de barrido no encontrada
      500:
        description: Error inesperado al consultar la intensidad de barrido
    """
    item = _get_barrido_intensidad_by_id(id)
    if not item:
        return jsonify({"error": "Intensidad de barrido no encontrada"}), 404
    return jsonify(_serialize_barrido_intensidad(item))


@barrido_intensidad_bp.route("/api/barrido_intensidad", methods=["POST"])
def create_barrido_intensidad():
    """Crear intensidad de barrido.
    ---
    tags:
      - Barrido Intensidad
    summary: Crear intensidad de barrido
    description: Inserta un registro en `barrido_intensidad`. El par `evento_tipo_id` y `nombre` debe ser unico segun la restriccion del catalogo.
    consumes:
      - application/json
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          required:
            - evento_tipo_id
            - orden
            - nombre
          properties:
            evento_tipo_id: {type: integer, description: ID del tipo de evento al que aplica la intensidad}
            orden: {type: integer, description: Orden de presentacion}
            nombre: {type: string, description: Nombre de la intensidad}
            descripcion: {type: string, description: Descripcion de la intensidad, nullable: true}
            activo: {type: boolean, default: true, description: Estado activo del catalogo}
            creador: {type: string, description: Usuario creador}
            modificador: {type: string, description: Usuario modificador}
    responses:
      201:
        description: Intensidad de barrido creada correctamente
      400:
        description: Campos requeridos faltantes o cuerpo JSON invalido
      500:
        description: Error inesperado al crear la intensidad de barrido
    """
    data = request.get_json(silent=True) or {}
    required_fields = ["evento_tipo_id", "orden", "nombre"]
    missing_fields = [field for field in required_fields if data.get(field) is None]
    if missing_fields:
        return jsonify({"error": f"Campos requeridos faltantes: {', '.join(missing_fields)}"}), 400

    now = datetime.now(timezone.utc)
    creador = data.get("creador", "Sistema")
    modificador = data.get("modificador", creador)

    query = db.text(
        f"""
        INSERT INTO {TABLE_NAME} (
            evento_tipo_id,
            orden,
            nombre,
            descripcion,
            activo,
            creador,
            creacion,
            modificador,
            modificacion
        )
        VALUES (
            :evento_tipo_id,
            :orden,
            :nombre,
            :descripcion,
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
                "evento_tipo_id": data["evento_tipo_id"],
                "orden": data["orden"],
                "nombre": data["nombre"],
                "descripcion": data.get("descripcion"),
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
            return jsonify({"error": "No se pudo crear la intensidad de barrido"}), 500
        item_id = row[0]
        db.session.commit()
    except Exception as exc:
        db.session.rollback()
        return jsonify({"error": "Error al crear la intensidad de barrido", "detalle": str(exc)}), 500

    item = _get_barrido_intensidad_by_id(item_id)
    if not item:
        return jsonify({"error": "Intensidad de barrido no encontrada"}), 404
    return jsonify(_serialize_barrido_intensidad(item)), 201


@barrido_intensidad_bp.route("/api/barrido_intensidad/<int:id>", methods=["PUT"])
def update_barrido_intensidad(id):
    """Actualizar intensidad de barrido.
    ---
    tags:
      - Barrido Intensidad
    summary: Actualizar intensidad de barrido
    description: Actualiza de forma parcial los campos editables de un registro de `barrido_intensidad`.
    consumes:
      - application/json
    parameters:
      - name: id
        in: path
        type: integer
        required: true
        description: Identificador unico de la intensidad
      - in: body
        name: body
        required: true
        schema:
          type: object
          properties:
            evento_tipo_id: {type: integer, description: ID del tipo de evento al que aplica la intensidad}
            orden: {type: integer, description: Orden de presentacion}
            nombre: {type: string, description: Nombre de la intensidad}
            descripcion: {type: string, description: Descripcion de la intensidad, nullable: true}
            activo: {type: boolean, description: Estado activo del catalogo}
            modificador: {type: string, description: Usuario modificador}
    responses:
      200:
        description: Intensidad de barrido actualizada correctamente
      400:
        description: No se enviaron campos validos para actualizar
      404:
        description: Intensidad de barrido no encontrada
      500:
        description: Error inesperado al actualizar la intensidad de barrido
    """
    data = request.get_json(silent=True) or {}
    now = datetime.now(timezone.utc)
    updatable_fields = ["evento_tipo_id", "orden", "nombre", "descripcion", "activo"]

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
            return jsonify({"error": "Intensidad de barrido no encontrada"}), 404
        db.session.commit()
    except Exception as exc:
        db.session.rollback()
        return jsonify({"error": "Error al actualizar la intensidad de barrido", "detalle": str(exc)}), 500

    item = _get_barrido_intensidad_by_id(id)
    if not item:
        return jsonify({"error": "Intensidad de barrido no encontrada"}), 404
    return jsonify(_serialize_barrido_intensidad(item))


@barrido_intensidad_bp.route("/api/barrido_intensidad/<int:id>", methods=["DELETE"])
def delete_barrido_intensidad(id):
    """Eliminar intensidad de barrido.
    ---
    tags:
      - Barrido Intensidad
    summary: Eliminar intensidad de barrido
    description: Elimina fisicamente el registro de `barrido_intensidad` identificado por `id`.
    parameters:
      - name: id
        in: path
        type: integer
        required: true
        description: Identificador unico de la intensidad
    responses:
      200:
        description: Intensidad de barrido eliminada correctamente
      404:
        description: Intensidad de barrido no encontrada
      500:
        description: Error inesperado al eliminar la intensidad de barrido
    """
    try:
        result = db.session.execute(
            db.text(f"DELETE FROM {TABLE_NAME} WHERE id = :id"),
            {"id": id},
        )
        if getattr(result, "rowcount", 0) == 0:
            db.session.rollback()
            return jsonify({"error": "Intensidad de barrido no encontrada"}), 404
        db.session.commit()
    except Exception as exc:
        db.session.rollback()
        return jsonify({"error": "Error al eliminar la intensidad de barrido", "detalle": str(exc)}), 500

    return jsonify({"mensaje": "Intensidad de barrido eliminada correctamente"})
