from datetime import datetime, timezone

from flask import jsonify, request

from accidentes_geograficos import accidentes_geograficos_bp
from models import db


TABLE_NAME = "public.accidentes_geograficos"


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


def _accidente_geografico_tipo_existe(accidente_geografico_tipo_id):
    row = db.session.execute(
        db.text("SELECT 1 FROM public.accidente_geografico_tipos WHERE id = :id"),
        {"id": accidente_geografico_tipo_id},
    ).fetchone()
    return row is not None


def _evento_tipo_existe(evento_tipo_id):
    row = db.session.execute(
        db.text("SELECT 1 FROM public.evento_tipos WHERE id = :id"),
        {"id": evento_tipo_id},
    ).fetchone()
    return row is not None


def _serialize_accidente_geografico(row):
    return {
        "id": getattr(row, "id", None),
        "evento_tipo_id": getattr(row, "evento_tipo_id", None),
        "evento_tipo_nombre": getattr(row, "evento_tipo_nombre", None),
        "accidente_geografico_tipo_id": getattr(row, "accidente_geografico_tipo_id", None),
        "accidente_geografico_tipo_codigo": getattr(row, "accidente_geografico_tipo_codigo", None),
        "accidente_geografico_tipo_nombre": getattr(row, "accidente_geografico_tipo_nombre", None),
        "accidente_geografico_tipo_descripcion": getattr(row, "accidente_geografico_tipo_descripcion", None),
        "nombre": getattr(row, "nombre", None),
        "descripcion": getattr(row, "descripcion", None),
        "provincia_id": getattr(row, "provincia_id", None),
        "provincia_nombre": getattr(row, "provincia_nombre", None),
        "canton_id": getattr(row, "canton_id", None),
        "canton_nombre": getattr(row, "canton_nombre", None),
        "parroquia_id": getattr(row, "parroquia_id", None),
        "parroquia_nombre": getattr(row, "parroquia_nombre", None),
        "longitud": _to_float_optional(getattr(row, "longitud", None)),
        "latitud": _to_float_optional(getattr(row, "latitud", None)),
        "activo": getattr(row, "activo", None),
        "creador": getattr(row, "creador", None),
        "creacion": _to_iso_optional(getattr(row, "creacion", None)),
        "modificador": getattr(row, "modificador", None),
        "modificacion": _to_iso_optional(getattr(row, "modificacion", None)),
    }


def _select_accidentes_geograficos(where_clause="", order_by="ag.id ASC"):
    return db.text(
        f"""
        SELECT
            ag.id,
            ag.evento_tipo_id,
            et.nombre AS evento_tipo_nombre,
            ag.accidente_geografico_tipo_id,
            agt.codigo AS accidente_geografico_tipo_codigo,
            agt.nombre AS accidente_geografico_tipo_nombre,
            agt.descripcion AS accidente_geografico_tipo_descripcion,
            ag.nombre,
            ag.descripcion,
            ag.provincia_id,
            p.nombre AS provincia_nombre,
            ag.canton_id,
            c.nombre AS canton_nombre,
            ag.parroquia_id,
            q.nombre AS parroquia_nombre,
            ag.longitud,
            ag.latitud,
            ag.activo,
            ag.creador,
            ag.creacion,
            ag.modificador,
            ag.modificacion
        FROM {TABLE_NAME} ag
        LEFT JOIN public.evento_tipos et
            ON et.id = ag.evento_tipo_id
        LEFT JOIN public.accidente_geografico_tipos agt
            ON agt.id = ag.accidente_geografico_tipo_id
        LEFT JOIN public.provincias p
            ON p.id = ag.provincia_id
        LEFT JOIN public.cantones c
            ON c.provincia_id = ag.provincia_id
           AND c.id = ag.canton_id
        LEFT JOIN public.parroquias q
            ON q.provincia_id = ag.provincia_id
           AND q.canton_id = ag.canton_id
           AND q.id = ag.parroquia_id
        {where_clause}
        ORDER BY {order_by}
        """
    )


def _get_accidente_geografico_by_id(item_id):
    query = _select_accidentes_geograficos("WHERE ag.id = :id", "ag.id ASC")
    return db.session.execute(query, {"id": item_id}).fetchone()


@accidentes_geograficos_bp.route("/api/accidentes_geograficos", methods=["GET"])
def get_accidentes_geograficos():
    """Listar accidentes geograficos.
    ---
    tags:
      - Accidentes Geograficos
    summary: Listar accidentes geograficos
    description: Devuelve todos los registros de `accidentes_geograficos`, incluyendo tipo de evento, tipo de accidente geografico, ubicacion, coordenadas y auditoria.
    responses:
      200:
        description: Lista de accidentes geograficos
        schema:
          type: array
          items:
            type: object
            properties:
              id: {type: integer, description: Identificador unico del accidente geografico}
              evento_tipo_id: {type: integer, description: ID del tipo de evento relacionado}
              evento_tipo_nombre: {type: string, description: Nombre del tipo de evento, nullable: true}
              accidente_geografico_tipo_id: {type: integer, description: ID del tipo de accidente geografico}
              accidente_geografico_tipo_codigo: {type: string, description: Codigo del tipo, nullable: true}
              accidente_geografico_tipo_nombre: {type: string, description: Nombre del tipo, nullable: true}
              accidente_geografico_tipo_descripcion: {type: string, description: Descripcion del tipo, nullable: true}
              nombre: {type: string, description: Nombre del accidente geografico}
              descripcion: {type: string, description: Descripcion del accidente geografico, nullable: true}
              provincia_id: {type: integer, description: ID de provincia, nullable: true}
              provincia_nombre: {type: string, description: Nombre de provincia, nullable: true}
              canton_id: {type: integer, description: ID de canton, nullable: true}
              canton_nombre: {type: string, description: Nombre de canton, nullable: true}
              parroquia_id: {type: integer, description: ID de parroquia, nullable: true}
              parroquia_nombre: {type: string, description: Nombre de parroquia, nullable: true}
              longitud: {type: number, format: float, description: Longitud, nullable: true}
              latitud: {type: number, format: float, description: Latitud, nullable: true}
              activo: {type: boolean, description: Estado activo del registro}
              creador: {type: string, description: Usuario creador, nullable: true}
              creacion: {type: string, format: date-time, description: Fecha de creacion}
              modificador: {type: string, description: Usuario modificador, nullable: true}
              modificacion: {type: string, format: date-time, description: Fecha de modificacion, nullable: true}
      500:
        description: Error inesperado al consultar accidentes geograficos
    """
    result = db.session.execute(_select_accidentes_geograficos())
    return jsonify([_serialize_accidente_geografico(row) for row in result])


@accidentes_geograficos_bp.route("/api/accidentes_geograficos/tipo/<int:accidente_geografico_tipo_id>", methods=["GET"])
def get_accidentes_geograficos_by_tipo(accidente_geografico_tipo_id):
    """Listar accidentes geograficos por tipo.
    ---
    tags:
      - Accidentes Geograficos
    summary: Listar accidentes geograficos por tipo
    description: Devuelve los accidentes geograficos activos del tipo indicado.
    parameters:
      - name: accidente_geografico_tipo_id
        in: path
        type: integer
        required: true
        description: Identificador del tipo de accidente geografico
    responses:
      200:
        description: Lista de accidentes geograficos activos del tipo indicado
      500:
        description: Error inesperado al consultar accidentes geograficos por tipo
    """
    query = _select_accidentes_geograficos(
        "WHERE ag.accidente_geografico_tipo_id = :accidente_geografico_tipo_id AND COALESCE(ag.activo, true) = true",
        "ag.nombre ASC, ag.id ASC",
    )
    result = db.session.execute(query, {"accidente_geografico_tipo_id": accidente_geografico_tipo_id})
    return jsonify([_serialize_accidente_geografico(row) for row in result])


@accidentes_geograficos_bp.route("/api/accidentes_geograficos/evento_tipo/<int:evento_tipo_id>", methods=["GET"])
def get_accidentes_geograficos_by_evento_tipo(evento_tipo_id):
    """Listar accidentes geograficos por tipo de evento.
    ---
    tags:
      - Accidentes Geograficos
    summary: Listar accidentes geograficos por tipo de evento
    description: Devuelve los accidentes geograficos activos asociados al `evento_tipo_id` indicado.
    parameters:
      - name: evento_tipo_id
        in: path
        type: integer
        required: true
        description: Identificador del tipo de evento
    responses:
      200:
        description: Lista de accidentes geograficos activos del tipo de evento indicado
      500:
        description: Error inesperado al consultar accidentes geograficos por tipo de evento
    """
    query = _select_accidentes_geograficos(
        "WHERE ag.evento_tipo_id = :evento_tipo_id AND COALESCE(ag.activo, true) = true",
        "ag.nombre ASC, ag.id ASC",
    )
    result = db.session.execute(query, {"evento_tipo_id": evento_tipo_id})
    return jsonify([_serialize_accidente_geografico(row) for row in result])


@accidentes_geograficos_bp.route("/api/accidentes_geograficos/tipo_codigo/<string:codigo>", methods=["GET"])
def get_accidentes_geograficos_by_tipo_codigo(codigo):
    """Listar accidentes geograficos por codigo de tipo.
    ---
    tags:
      - Accidentes Geograficos
    summary: Listar accidentes geograficos por codigo de tipo
    description: Devuelve los accidentes geograficos activos cuyo tipo coincide con el `codigo` indicado en `accidente_geografico_tipos`. Por ejemplo, `VOLCAN` devuelve el catalogo de volcanes usado por `barridos.accidente_geografico_id`.
    parameters:
      - name: codigo
        in: path
        type: string
        required: true
        description: Codigo del tipo de accidente geografico
    responses:
      200:
        description: Lista de accidentes geograficos activos del codigo de tipo indicado
      500:
        description: Error inesperado al consultar accidentes geograficos por codigo de tipo
    """
    query = _select_accidentes_geograficos(
        """
        WHERE UPPER(agt.codigo) = UPPER(:codigo)
          AND COALESCE(ag.activo, true) = true
          AND COALESCE(agt.activo, true) = true
        """,
        "ag.nombre ASC, ag.id ASC",
    )
    result = db.session.execute(query, {"codigo": codigo})
    return jsonify([_serialize_accidente_geografico(row) for row in result])


@accidentes_geograficos_bp.route(
    "/api/accidentes_geograficos/evento_tipo/<int:evento_tipo_id>/tipo_codigo/<string:codigo>",
    methods=["GET"],
)
def get_accidentes_geograficos_by_evento_tipo_by_tipo_codigo(evento_tipo_id, codigo):
    """Listar accidentes geograficos por tipo de evento y codigo de tipo.
    ---
    tags:
      - Accidentes Geograficos
    summary: Listar accidentes geograficos por evento y codigo de tipo
    description: Devuelve los accidentes geograficos activos asociados al `evento_tipo_id` y al `codigo` de `accidente_geografico_tipos`.
    parameters:
      - name: evento_tipo_id
        in: path
        type: integer
        required: true
        description: Identificador del tipo de evento
      - name: codigo
        in: path
        type: string
        required: true
        description: Codigo del tipo de accidente geografico
    responses:
      200:
        description: Lista de accidentes geograficos activos del evento y codigo de tipo indicados
      500:
        description: Error inesperado al consultar accidentes geograficos por evento y codigo de tipo
    """
    query = _select_accidentes_geograficos(
        """
        WHERE ag.evento_tipo_id = :evento_tipo_id
          AND UPPER(agt.codigo) = UPPER(:codigo)
          AND COALESCE(ag.activo, true) = true
          AND COALESCE(agt.activo, true) = true
        """,
        "ag.nombre ASC, ag.id ASC",
    )
    result = db.session.execute(query, {"evento_tipo_id": evento_tipo_id, "codigo": codigo})
    return jsonify([_serialize_accidente_geografico(row) for row in result])


@accidentes_geograficos_bp.route("/api/accidentes_geograficos/volcanes", methods=["GET"])
def get_accidentes_geograficos_volcanes():
    """Listar volcanes.
    ---
    tags:
      - Accidentes Geograficos
    summary: Listar volcanes
    description: Devuelve los accidentes geograficos activos cuyo tipo tiene codigo `VOLCAN`. Estos registros son los valores validos para `barridos.accidente_geografico_id` en eventos de erupcion volcanica.
    responses:
      200:
        description: Lista de volcanes activos
      500:
        description: Error inesperado al consultar volcanes
    """
    query = _select_accidentes_geograficos(
        """
        WHERE agt.codigo = 'VOLCAN'
          AND COALESCE(ag.activo, true) = true
          AND COALESCE(agt.activo, true) = true
        """,
        "ag.nombre ASC, ag.id ASC",
    )
    result = db.session.execute(query)
    return jsonify([_serialize_accidente_geografico(row) for row in result])


@accidentes_geograficos_bp.route("/api/accidentes_geograficos/volcanes/evento_tipo/<int:evento_tipo_id>", methods=["GET"])
def get_accidentes_geograficos_volcanes_by_evento_tipo(evento_tipo_id):
    """Listar volcanes por tipo de evento.
    ---
    tags:
      - Accidentes Geograficos
    summary: Listar volcanes por tipo de evento
    description: Devuelve los accidentes geograficos activos de tipo `VOLCAN` asociados al `evento_tipo_id` indicado. Estos registros son los valores validos para `barridos.accidente_geografico_id` en eventos de erupcion volcanica.
    parameters:
      - name: evento_tipo_id
        in: path
        type: integer
        required: true
        description: Identificador del tipo de evento
    responses:
      200:
        description: Lista de volcanes activos del tipo de evento indicado
      500:
        description: Error inesperado al consultar volcanes por tipo de evento
    """
    query = _select_accidentes_geograficos(
        """
        WHERE ag.evento_tipo_id = :evento_tipo_id
          AND agt.codigo = 'VOLCAN'
          AND COALESCE(ag.activo, true) = true
          AND COALESCE(agt.activo, true) = true
        """,
        "ag.nombre ASC, ag.id ASC",
    )
    result = db.session.execute(query, {"evento_tipo_id": evento_tipo_id})
    return jsonify([_serialize_accidente_geografico(row) for row in result])


@accidentes_geograficos_bp.route(
    "/api/accidentes_geograficos/provincia/<int:provincia_id>/canton/<int:canton_id>",
    methods=["GET"],
)
def get_accidentes_geograficos_by_ubicacion(provincia_id, canton_id):
    """Listar accidentes geograficos por ubicacion.
    ---
    tags:
      - Accidentes Geograficos
    summary: Listar accidentes geograficos por provincia y canton
    description: Devuelve los accidentes geograficos activos asociados a la provincia y canton indicados.
    parameters:
      - name: provincia_id
        in: path
        type: integer
        required: true
        description: Identificador de provincia
      - name: canton_id
        in: path
        type: integer
        required: true
        description: Identificador de canton
    responses:
      200:
        description: Lista de accidentes geograficos activos por ubicacion
      500:
        description: Error inesperado al consultar accidentes geograficos por ubicacion
    """
    query = _select_accidentes_geograficos(
        """
        WHERE ag.provincia_id = :provincia_id
          AND ag.canton_id = :canton_id
          AND COALESCE(ag.activo, true) = true
        """,
        "ag.nombre ASC, ag.id ASC",
    )
    result = db.session.execute(query, {"provincia_id": provincia_id, "canton_id": canton_id})
    return jsonify([_serialize_accidente_geografico(row) for row in result])


@accidentes_geograficos_bp.route("/api/accidentes_geograficos/<int:id>", methods=["GET"])
def get_accidente_geografico(id):
    """Obtener accidente geografico por ID.
    ---
    tags:
      - Accidentes Geograficos
    summary: Obtener accidente geografico por ID
    description: Devuelve el registro de `accidentes_geograficos` identificado por `id`.
    parameters:
      - name: id
        in: path
        type: integer
        required: true
        description: Identificador unico del accidente geografico
    responses:
      200:
        description: Accidente geografico encontrado
      404:
        description: Accidente geografico no encontrado
      500:
        description: Error inesperado al consultar el accidente geografico
    """
    item = _get_accidente_geografico_by_id(id)
    if not item:
        return jsonify({"error": "Accidente geografico no encontrado"}), 404
    return jsonify(_serialize_accidente_geografico(item))


@accidentes_geograficos_bp.route("/api/accidentes_geograficos", methods=["POST"])
def create_accidente_geografico():
    """Crear accidente geografico.
    ---
    tags:
      - Accidentes Geograficos
    summary: Crear accidente geografico
    description: Inserta un registro en `accidentes_geograficos` con tipo de evento, tipo de accidente geografico, nombre, descripcion, ubicacion opcional, coordenadas y auditoria.
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
            - accidente_geografico_tipo_id
            - nombre
          properties:
            evento_tipo_id: {type: integer, description: ID del tipo de evento relacionado}
            accidente_geografico_tipo_id: {type: integer, description: ID del tipo de accidente geografico}
            nombre: {type: string, description: Nombre del accidente geografico}
            descripcion: {type: string, description: Descripcion del accidente geografico, nullable: true}
            provincia_id: {type: integer, description: ID de provincia, nullable: true}
            canton_id: {type: integer, description: ID de canton, nullable: true}
            parroquia_id: {type: integer, description: ID de parroquia, nullable: true}
            longitud: {type: number, format: float, description: Longitud, nullable: true}
            latitud: {type: number, format: float, description: Latitud, nullable: true}
            activo: {type: boolean, default: true, description: Estado activo del registro}
            creador: {type: string, description: Usuario creador}
            modificador: {type: string, description: Usuario modificador}
    responses:
      201:
        description: Accidente geografico creado correctamente
      400:
        description: Campos requeridos faltantes, cuerpo JSON invalido, evento_tipo_id inexistente o tipo inexistente
      500:
        description: Error inesperado al crear el accidente geografico
    """
    data = request.get_json(silent=True) or {}
    required_fields = ["evento_tipo_id", "accidente_geografico_tipo_id", "nombre"]
    missing_fields = [field for field in required_fields if data.get(field) is None]
    if missing_fields:
        return jsonify({"error": f"Campos requeridos faltantes: {', '.join(missing_fields)}"}), 400

    if not _evento_tipo_existe(data["evento_tipo_id"]):
        return jsonify({"error": "evento_tipo_id no existe en evento_tipos"}), 400

    if not _accidente_geografico_tipo_existe(data["accidente_geografico_tipo_id"]):
        return jsonify({"error": "accidente_geografico_tipo_id no existe en accidente_geografico_tipos"}), 400

    now = datetime.now(timezone.utc)
    creador = data.get("creador", "Sistema")
    modificador = data.get("modificador", creador)

    query = db.text(
        f"""
        INSERT INTO {TABLE_NAME} (
            evento_tipo_id,
            accidente_geografico_tipo_id,
            nombre,
            descripcion,
            provincia_id,
            canton_id,
            parroquia_id,
            longitud,
            latitud,
            activo,
            creador,
            creacion,
            modificador,
            modificacion
        )
        VALUES (
            :evento_tipo_id,
            :accidente_geografico_tipo_id,
            :nombre,
            :descripcion,
            :provincia_id,
            :canton_id,
            :parroquia_id,
            :longitud,
            :latitud,
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
                "accidente_geografico_tipo_id": data["accidente_geografico_tipo_id"],
                "nombre": data["nombre"],
                "descripcion": data.get("descripcion"),
                "provincia_id": data.get("provincia_id"),
                "canton_id": data.get("canton_id"),
                "parroquia_id": data.get("parroquia_id"),
                "longitud": data.get("longitud"),
                "latitud": data.get("latitud"),
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
            return jsonify({"error": "No se pudo crear el accidente geografico"}), 500
        item_id = row[0]
        db.session.commit()
    except Exception as exc:
        db.session.rollback()
        return jsonify({"error": "Error al crear el accidente geografico", "detalle": str(exc)}), 500

    item = _get_accidente_geografico_by_id(item_id)
    if not item:
        return jsonify({"error": "Accidente geografico no encontrado"}), 404
    return jsonify(_serialize_accidente_geografico(item)), 201


@accidentes_geograficos_bp.route("/api/accidentes_geograficos/<int:id>", methods=["PUT"])
def update_accidente_geografico(id):
    """Actualizar accidente geografico.
    ---
    tags:
      - Accidentes Geograficos
    summary: Actualizar accidente geografico
    description: Actualiza de forma parcial los campos editables de un registro de `accidentes_geograficos`.
    consumes:
      - application/json
    parameters:
      - name: id
        in: path
        type: integer
        required: true
        description: Identificador unico del accidente geografico
      - in: body
        name: body
        required: true
        schema:
          type: object
          properties:
            evento_tipo_id: {type: integer, description: ID del tipo de evento relacionado}
            accidente_geografico_tipo_id: {type: integer, description: ID del tipo de accidente geografico}
            nombre: {type: string, description: Nombre del accidente geografico}
            descripcion: {type: string, description: Descripcion del accidente geografico, nullable: true}
            provincia_id: {type: integer, description: ID de provincia, nullable: true}
            canton_id: {type: integer, description: ID de canton, nullable: true}
            parroquia_id: {type: integer, description: ID de parroquia, nullable: true}
            longitud: {type: number, format: float, description: Longitud, nullable: true}
            latitud: {type: number, format: float, description: Latitud, nullable: true}
            activo: {type: boolean, description: Estado activo del registro}
            modificador: {type: string, description: Usuario modificador}
    responses:
      200:
        description: Accidente geografico actualizado correctamente
      400:
        description: No se enviaron campos validos, evento_tipo_id inexistente o tipo inexistente
      404:
        description: Accidente geografico no encontrado
      500:
        description: Error inesperado al actualizar el accidente geografico
    """
    data = request.get_json(silent=True) or {}
    if "evento_tipo_id" in data:
        if data["evento_tipo_id"] is None:
            return jsonify({"error": "evento_tipo_id no puede ser null"}), 400
        if not _evento_tipo_existe(data["evento_tipo_id"]):
            return jsonify({"error": "evento_tipo_id no existe en evento_tipos"}), 400

    if "accidente_geografico_tipo_id" in data:
        if data["accidente_geografico_tipo_id"] is None:
            return jsonify({"error": "accidente_geografico_tipo_id no puede ser null"}), 400
        if not _accidente_geografico_tipo_existe(data["accidente_geografico_tipo_id"]):
            return jsonify({"error": "accidente_geografico_tipo_id no existe en accidente_geografico_tipos"}), 400

    now = datetime.now(timezone.utc)
    updatable_fields = [
        "evento_tipo_id",
        "accidente_geografico_tipo_id",
        "nombre",
        "descripcion",
        "provincia_id",
        "canton_id",
        "parroquia_id",
        "longitud",
        "latitud",
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
            return jsonify({"error": "Accidente geografico no encontrado"}), 404
        db.session.commit()
    except Exception as exc:
        db.session.rollback()
        return jsonify({"error": "Error al actualizar el accidente geografico", "detalle": str(exc)}), 500

    item = _get_accidente_geografico_by_id(id)
    if not item:
        return jsonify({"error": "Accidente geografico no encontrado"}), 404
    return jsonify(_serialize_accidente_geografico(item))


@accidentes_geograficos_bp.route("/api/accidentes_geograficos/<int:id>", methods=["DELETE"])
def delete_accidente_geografico(id):
    """Eliminar accidente geografico.
    ---
    tags:
      - Accidentes Geograficos
    summary: Eliminar accidente geografico
    description: Elimina fisicamente el registro de `accidentes_geograficos` identificado por `id`.
    parameters:
      - name: id
        in: path
        type: integer
        required: true
        description: Identificador unico del accidente geografico
    responses:
      200:
        description: Accidente geografico eliminado correctamente
      404:
        description: Accidente geografico no encontrado
      500:
        description: Error inesperado al eliminar el accidente geografico
    """
    try:
        result = db.session.execute(
            db.text(f"DELETE FROM {TABLE_NAME} WHERE id = :id"),
            {"id": id},
        )
        if getattr(result, "rowcount", 0) == 0:
            db.session.rollback()
            return jsonify({"error": "Accidente geografico no encontrado"}), 404
        db.session.commit()
    except Exception as exc:
        db.session.rollback()
        return jsonify({"error": "Error al eliminar el accidente geografico", "detalle": str(exc)}), 500

    return jsonify({"mensaje": "Accidente geografico eliminado correctamente"})
