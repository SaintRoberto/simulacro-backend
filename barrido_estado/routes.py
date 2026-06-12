from datetime import datetime, timezone

from flask import jsonify, request

from barrido_estado import barrido_estado_bp
from models import db


TABLE_NAME = "public.barrido_estado"


def _to_iso_optional(value):
    if value is None or value == "":
        return None
    if hasattr(value, "isoformat"):
        return value.isoformat()
    return str(value)


def _serialize_barrido_estado(row):
    return {
        "id": getattr(row, "id", None),
        "orden": getattr(row, "orden", None),
        "codigo": getattr(row, "codigo", None),
        "nombre": getattr(row, "nombre", None),
        "descripcion": getattr(row, "descripcion", None),
        "permite_edicion": getattr(row, "permite_edicion", None),
        "permite_registro_monitoreo": getattr(row, "permite_registro_monitoreo", None),
        "es_estado_final": getattr(row, "es_estado_final", None),
        "activo": getattr(row, "activo", None),
        "creador": getattr(row, "creador", None),
        "creacion": _to_iso_optional(getattr(row, "creacion", None)),
        "modificador": getattr(row, "modificador", None),
        "modificacion": _to_iso_optional(getattr(row, "modificacion", None)),
    }


def _get_barrido_estado_by_id(item_id):
    return db.session.execute(
        db.text(f"SELECT * FROM {TABLE_NAME} WHERE id = :id"),
        {"id": item_id},
    ).fetchone()


@barrido_estado_bp.route("/api/barrido_estado", methods=["GET"])
def get_barrido_estados():
    """Listar estados de barrido.
    ---
    tags:
      - Barrido Estado
    summary: Listar estados de barrido
    description: Devuelve todos los estados del catalogo `barrido_estado`, ordenados por `orden` e `id`.
    responses:
      200:
        description: Lista de estados de barrido
        schema:
          type: array
          items:
            type: object
            properties:
              id: {type: integer, description: Identificador unico del estado}
              orden: {type: integer, description: Orden de presentacion del estado}
              codigo: {type: string, description: Codigo unico del estado}
              nombre: {type: string, description: Nombre unico del estado}
              descripcion: {type: string, description: Descripcion del estado, nullable: true}
              permite_edicion: {type: boolean, description: Indica si el estado permite editar el barrido}
              permite_registro_monitoreo: {type: boolean, description: Indica si el estado permite registrar monitoreo}
              es_estado_final: {type: boolean, description: Indica si el estado finaliza el flujo del barrido}
              activo: {type: boolean, description: Estado activo del catalogo}
              creador: {type: string, description: Usuario creador, nullable: true}
              creacion: {type: string, format: date-time, description: Fecha de creacion}
              modificador: {type: string, description: Usuario modificador, nullable: true}
              modificacion: {type: string, format: date-time, description: Fecha de modificacion, nullable: true}
      500:
        description: Error inesperado al consultar los estados de barrido
    """
    result = db.session.execute(db.text(f"SELECT * FROM {TABLE_NAME} ORDER BY orden ASC, id ASC"))
    return jsonify([_serialize_barrido_estado(row) for row in result])


@barrido_estado_bp.route("/api/barrido_estado/activos", methods=["GET"])
def get_barrido_estados_activos():
    """Listar estados de barrido activos.
    ---
    tags:
      - Barrido Estado
    summary: Listar estados activos de barrido
    description: Devuelve los estados activos del catalogo `barrido_estado`, ordenados por `orden` e `id`.
    responses:
      200:
        description: Lista de estados activos de barrido
        schema:
          type: array
          items:
            type: object
            properties:
              id: {type: integer, description: Identificador unico del estado}
              orden: {type: integer, description: Orden de presentacion del estado}
              codigo: {type: string, description: Codigo unico del estado}
              nombre: {type: string, description: Nombre unico del estado}
              descripcion: {type: string, description: Descripcion del estado, nullable: true}
              permite_edicion: {type: boolean, description: Indica si el estado permite editar el barrido}
              permite_registro_monitoreo: {type: boolean, description: Indica si el estado permite registrar monitoreo}
              es_estado_final: {type: boolean, description: Indica si el estado finaliza el flujo del barrido}
              activo: {type: boolean, description: Estado activo del catalogo}
      500:
        description: Error inesperado al consultar los estados activos de barrido
    """
    result = db.session.execute(
        db.text(f"SELECT * FROM {TABLE_NAME} WHERE COALESCE(activo, true) = true ORDER BY orden ASC, id ASC")
    )
    return jsonify([_serialize_barrido_estado(row) for row in result])


@barrido_estado_bp.route("/api/barrido_estado/<int:id>", methods=["GET"])
def get_barrido_estado(id):
    """Obtener estado de barrido por ID.
    ---
    tags:
      - Barrido Estado
    summary: Obtener estado de barrido por ID
    description: Devuelve un registro de `barrido_estado` identificado por `id`.
    parameters:
      - name: id
        in: path
        type: integer
        required: true
        description: Identificador unico del estado
    responses:
      200:
        description: Estado de barrido encontrado
        schema:
          type: object
          properties:
            id: {type: integer, description: Identificador unico del estado}
            orden: {type: integer, description: Orden de presentacion del estado}
            codigo: {type: string, description: Codigo unico del estado}
            nombre: {type: string, description: Nombre unico del estado}
            descripcion: {type: string, description: Descripcion del estado, nullable: true}
            permite_edicion: {type: boolean, description: Indica si el estado permite editar el barrido}
            permite_registro_monitoreo: {type: boolean, description: Indica si el estado permite registrar monitoreo}
            es_estado_final: {type: boolean, description: Indica si el estado finaliza el flujo del barrido}
            activo: {type: boolean, description: Estado activo del catalogo}
            creador: {type: string, description: Usuario creador, nullable: true}
            creacion: {type: string, format: date-time, description: Fecha de creacion}
            modificador: {type: string, description: Usuario modificador, nullable: true}
            modificacion: {type: string, format: date-time, description: Fecha de modificacion, nullable: true}
      404:
        description: Estado de barrido no encontrado
      500:
        description: Error inesperado al consultar el estado de barrido
    """
    item = _get_barrido_estado_by_id(id)
    if not item:
        return jsonify({"error": "Estado de barrido no encontrado"}), 404
    return jsonify(_serialize_barrido_estado(item))


@barrido_estado_bp.route("/api/barrido_estado", methods=["POST"])
def create_barrido_estado():
    """Crear estado de barrido.
    ---
    tags:
      - Barrido Estado
    summary: Crear estado de barrido
    description: Inserta un registro en `barrido_estado`. Los campos `orden`, `codigo` y `nombre` son unicos segun las restricciones del catalogo.
    consumes:
      - application/json
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          required:
            - orden
            - codigo
            - nombre
          properties:
            orden: {type: integer, description: Orden de presentacion del estado}
            codigo: {type: string, description: Codigo unico del estado}
            nombre: {type: string, description: Nombre unico del estado}
            descripcion: {type: string, description: Descripcion del estado, nullable: true}
            permite_edicion: {type: boolean, default: true, description: Indica si el estado permite editar el barrido}
            permite_registro_monitoreo: {type: boolean, default: true, description: Indica si el estado permite registrar monitoreo}
            es_estado_final: {type: boolean, default: false, description: Indica si el estado finaliza el flujo del barrido}
            activo: {type: boolean, default: true, description: Estado activo del catalogo}
            creador: {type: string, description: Usuario creador}
            modificador: {type: string, description: Usuario modificador}
    responses:
      201:
        description: Estado de barrido creado correctamente
      400:
        description: Campos requeridos faltantes o cuerpo JSON invalido
      500:
        description: Error inesperado al crear el estado de barrido
    """
    data = request.get_json(silent=True) or {}
    required_fields = ["orden", "codigo", "nombre"]
    missing_fields = [field for field in required_fields if data.get(field) is None]
    if missing_fields:
        return jsonify({"error": f"Campos requeridos faltantes: {', '.join(missing_fields)}"}), 400

    now = datetime.now(timezone.utc)
    creador = data.get("creador", "Sistema")
    modificador = data.get("modificador", creador)

    query = db.text(
        f"""
        INSERT INTO {TABLE_NAME} (
            orden,
            codigo,
            nombre,
            descripcion,
            permite_edicion,
            permite_registro_monitoreo,
            es_estado_final,
            activo,
            creador,
            creacion,
            modificador,
            modificacion
        )
        VALUES (
            :orden,
            :codigo,
            :nombre,
            :descripcion,
            :permite_edicion,
            :permite_registro_monitoreo,
            :es_estado_final,
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
                "orden": data["orden"],
                "codigo": data["codigo"],
                "nombre": data["nombre"],
                "descripcion": data.get("descripcion"),
                "permite_edicion": data.get("permite_edicion", True),
                "permite_registro_monitoreo": data.get("permite_registro_monitoreo", True),
                "es_estado_final": data.get("es_estado_final", False),
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
            return jsonify({"error": "No se pudo crear el estado de barrido"}), 500
        item_id = row[0]
        db.session.commit()
    except Exception as exc:
        db.session.rollback()
        return jsonify({"error": "Error al crear el estado de barrido", "detalle": str(exc)}), 500

    item = _get_barrido_estado_by_id(item_id)
    if not item:
        return jsonify({"error": "Estado de barrido no encontrado"}), 404
    return jsonify(_serialize_barrido_estado(item)), 201


@barrido_estado_bp.route("/api/barrido_estado/<int:id>", methods=["PUT"])
def update_barrido_estado(id):
    """Actualizar estado de barrido.
    ---
    tags:
      - Barrido Estado
    summary: Actualizar estado de barrido
    description: Actualiza de forma parcial los campos editables de un registro de `barrido_estado`.
    consumes:
      - application/json
    parameters:
      - name: id
        in: path
        type: integer
        required: true
        description: Identificador unico del estado
      - in: body
        name: body
        required: true
        schema:
          type: object
          properties:
            orden: {type: integer, description: Orden de presentacion del estado}
            codigo: {type: string, description: Codigo unico del estado}
            nombre: {type: string, description: Nombre unico del estado}
            descripcion: {type: string, description: Descripcion del estado, nullable: true}
            permite_edicion: {type: boolean, description: Indica si el estado permite editar el barrido}
            permite_registro_monitoreo: {type: boolean, description: Indica si el estado permite registrar monitoreo}
            es_estado_final: {type: boolean, description: Indica si el estado finaliza el flujo del barrido}
            activo: {type: boolean, description: Estado activo del catalogo}
            modificador: {type: string, description: Usuario modificador}
    responses:
      200:
        description: Estado de barrido actualizado correctamente
      400:
        description: No se enviaron campos validos para actualizar
      404:
        description: Estado de barrido no encontrado
      500:
        description: Error inesperado al actualizar el estado de barrido
    """
    data = request.get_json(silent=True) or {}
    now = datetime.now(timezone.utc)
    updatable_fields = [
        "orden",
        "codigo",
        "nombre",
        "descripcion",
        "permite_edicion",
        "permite_registro_monitoreo",
        "es_estado_final",
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
            return jsonify({"error": "Estado de barrido no encontrado"}), 404
        db.session.commit()
    except Exception as exc:
        db.session.rollback()
        return jsonify({"error": "Error al actualizar el estado de barrido", "detalle": str(exc)}), 500

    item = _get_barrido_estado_by_id(id)
    if not item:
        return jsonify({"error": "Estado de barrido no encontrado"}), 404
    return jsonify(_serialize_barrido_estado(item))


@barrido_estado_bp.route("/api/barrido_estado/<int:id>", methods=["DELETE"])
def delete_barrido_estado(id):
    """Eliminar estado de barrido.
    ---
    tags:
      - Barrido Estado
    summary: Eliminar estado de barrido
    description: Elimina fisicamente el registro de `barrido_estado` identificado por `id`.
    parameters:
      - name: id
        in: path
        type: integer
        required: true
        description: Identificador unico del estado
    responses:
      200:
        description: Estado de barrido eliminado correctamente
      404:
        description: Estado de barrido no encontrado
      500:
        description: Error inesperado al eliminar el estado de barrido
    """
    try:
        result = db.session.execute(
            db.text(f"DELETE FROM {TABLE_NAME} WHERE id = :id"),
            {"id": id},
        )
        if getattr(result, "rowcount", 0) == 0:
            db.session.rollback()
            return jsonify({"error": "Estado de barrido no encontrado"}), 404
        db.session.commit()
    except Exception as exc:
        db.session.rollback()
        return jsonify({"error": "Error al eliminar el estado de barrido", "detalle": str(exc)}), 500

    return jsonify({"mensaje": "Estado de barrido eliminado correctamente"})
