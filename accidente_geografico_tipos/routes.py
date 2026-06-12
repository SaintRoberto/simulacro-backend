from datetime import datetime, timezone

from flask import jsonify, request

from accidente_geografico_tipos import accidente_geografico_tipos_bp
from models import db


TABLE_NAME = "public.accidente_geografico_tipos"


def _to_iso_optional(value):
    if value is None or value == "":
        return None
    if hasattr(value, "isoformat"):
        return value.isoformat()
    return str(value)


def _serialize_accidente_geografico_tipo(row):
    return {
        "id": getattr(row, "id", None),
        "orden": getattr(row, "orden", None),
        "codigo": getattr(row, "codigo", None),
        "nombre": getattr(row, "nombre", None),
        "descripcion": getattr(row, "descripcion", None),
        "activo": getattr(row, "activo", None),
        "creador": getattr(row, "creador", None),
        "creacion": _to_iso_optional(getattr(row, "creacion", None)),
        "modificador": getattr(row, "modificador", None),
        "modificacion": _to_iso_optional(getattr(row, "modificacion", None)),
    }


def _get_accidente_geografico_tipo_by_id(item_id):
    return db.session.execute(
        db.text(f"SELECT * FROM {TABLE_NAME} WHERE id = :id"),
        {"id": item_id},
    ).fetchone()


@accidente_geografico_tipos_bp.route("/api/accidente_geografico_tipos", methods=["GET"])
def get_accidente_geografico_tipos():
    """Listar tipos de accidente geografico.
    ---
    tags:
      - Accidente Geografico Tipos
    summary: Listar tipos de accidente geografico
    description: Devuelve todos los registros del catalogo `accidente_geografico_tipos`, ordenados por `orden` e `id`.
    responses:
      200:
        description: Lista de tipos de accidente geografico
        schema:
          type: array
          items:
            type: object
            properties:
              id: {type: integer, description: Identificador unico del tipo}
              orden: {type: integer, description: Orden de presentacion}
              codigo: {type: string, description: Codigo unico del tipo}
              nombre: {type: string, description: Nombre unico del tipo}
              descripcion: {type: string, description: Descripcion del tipo, nullable: true}
              activo: {type: boolean, description: Estado activo del catalogo}
              creador: {type: string, description: Usuario creador, nullable: true}
              creacion: {type: string, format: date-time, description: Fecha de creacion}
              modificador: {type: string, description: Usuario modificador, nullable: true}
              modificacion: {type: string, format: date-time, description: Fecha de modificacion, nullable: true}
      500:
        description: Error inesperado al consultar los tipos de accidente geografico
    """
    result = db.session.execute(db.text(f"SELECT * FROM {TABLE_NAME} ORDER BY orden ASC, id ASC"))
    return jsonify([_serialize_accidente_geografico_tipo(row) for row in result])


@accidente_geografico_tipos_bp.route("/api/accidente_geografico_tipos/activos", methods=["GET"])
def get_accidente_geografico_tipos_activos():
    """Listar tipos de accidente geografico activos.
    ---
    tags:
      - Accidente Geografico Tipos
    summary: Listar tipos activos de accidente geografico
    description: Devuelve los registros activos del catalogo `accidente_geografico_tipos`, ordenados por `orden` e `id`.
    responses:
      200:
        description: Lista de tipos activos de accidente geografico
      500:
        description: Error inesperado al consultar los tipos activos
    """
    result = db.session.execute(
        db.text(f"SELECT * FROM {TABLE_NAME} WHERE activo = true ORDER BY orden ASC, id ASC")
    )
    return jsonify([_serialize_accidente_geografico_tipo(row) for row in result])


@accidente_geografico_tipos_bp.route("/api/accidente_geografico_tipos/<int:id>", methods=["GET"])
def get_accidente_geografico_tipo(id):
    """Obtener tipo de accidente geografico por ID.
    ---
    tags:
      - Accidente Geografico Tipos
    summary: Obtener tipo de accidente geografico por ID
    description: Devuelve el registro de `accidente_geografico_tipos` identificado por `id`.
    parameters:
      - name: id
        in: path
        type: integer
        required: true
        description: Identificador unico del tipo
    responses:
      200:
        description: Tipo de accidente geografico encontrado
      404:
        description: Tipo de accidente geografico no encontrado
      500:
        description: Error inesperado al consultar el tipo de accidente geografico
    """
    item = _get_accidente_geografico_tipo_by_id(id)
    if not item:
        return jsonify({"error": "Tipo de accidente geografico no encontrado"}), 404
    return jsonify(_serialize_accidente_geografico_tipo(item))


@accidente_geografico_tipos_bp.route("/api/accidente_geografico_tipos", methods=["POST"])
def create_accidente_geografico_tipo():
    """Crear tipo de accidente geografico.
    ---
    tags:
      - Accidente Geografico Tipos
    summary: Crear tipo de accidente geografico
    description: Inserta un registro en `accidente_geografico_tipos`. Los campos `orden`, `codigo` y `nombre` son unicos.
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
            orden: {type: integer, description: Orden de presentacion}
            codigo: {type: string, description: Codigo unico del tipo}
            nombre: {type: string, description: Nombre unico del tipo}
            descripcion: {type: string, description: Descripcion del tipo, nullable: true}
            activo: {type: boolean, default: true, description: Estado activo del catalogo}
            creador: {type: string, description: Usuario creador}
            modificador: {type: string, description: Usuario modificador}
    responses:
      201:
        description: Tipo de accidente geografico creado correctamente
      400:
        description: Campos requeridos faltantes o cuerpo JSON invalido
      500:
        description: Error inesperado al crear el tipo de accidente geografico
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
            return jsonify({"error": "No se pudo crear el tipo de accidente geografico"}), 500
        item_id = row[0]
        db.session.commit()
    except Exception as exc:
        db.session.rollback()
        return jsonify({"error": "Error al crear el tipo de accidente geografico", "detalle": str(exc)}), 500

    item = _get_accidente_geografico_tipo_by_id(item_id)
    if not item:
        return jsonify({"error": "Tipo de accidente geografico no encontrado"}), 404
    return jsonify(_serialize_accidente_geografico_tipo(item)), 201


@accidente_geografico_tipos_bp.route("/api/accidente_geografico_tipos/<int:id>", methods=["PUT"])
def update_accidente_geografico_tipo(id):
    """Actualizar tipo de accidente geografico.
    ---
    tags:
      - Accidente Geografico Tipos
    summary: Actualizar tipo de accidente geografico
    description: Actualiza de forma parcial los campos editables de un registro de `accidente_geografico_tipos`.
    consumes:
      - application/json
    parameters:
      - name: id
        in: path
        type: integer
        required: true
        description: Identificador unico del tipo
      - in: body
        name: body
        required: true
        schema:
          type: object
          properties:
            orden: {type: integer, description: Orden de presentacion}
            codigo: {type: string, description: Codigo unico del tipo}
            nombre: {type: string, description: Nombre unico del tipo}
            descripcion: {type: string, description: Descripcion del tipo, nullable: true}
            activo: {type: boolean, description: Estado activo del catalogo}
            modificador: {type: string, description: Usuario modificador}
    responses:
      200:
        description: Tipo de accidente geografico actualizado correctamente
      400:
        description: No se enviaron campos validos para actualizar
      404:
        description: Tipo de accidente geografico no encontrado
      500:
        description: Error inesperado al actualizar el tipo de accidente geografico
    """
    data = request.get_json(silent=True) or {}
    now = datetime.now(timezone.utc)
    updatable_fields = ["orden", "codigo", "nombre", "descripcion", "activo"]

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
            return jsonify({"error": "Tipo de accidente geografico no encontrado"}), 404
        db.session.commit()
    except Exception as exc:
        db.session.rollback()
        return jsonify({"error": "Error al actualizar el tipo de accidente geografico", "detalle": str(exc)}), 500

    item = _get_accidente_geografico_tipo_by_id(id)
    if not item:
        return jsonify({"error": "Tipo de accidente geografico no encontrado"}), 404
    return jsonify(_serialize_accidente_geografico_tipo(item))


@accidente_geografico_tipos_bp.route("/api/accidente_geografico_tipos/<int:id>", methods=["DELETE"])
def delete_accidente_geografico_tipo(id):
    """Eliminar tipo de accidente geografico.
    ---
    tags:
      - Accidente Geografico Tipos
    summary: Eliminar tipo de accidente geografico
    description: Elimina fisicamente el registro de `accidente_geografico_tipos` identificado por `id`.
    parameters:
      - name: id
        in: path
        type: integer
        required: true
        description: Identificador unico del tipo
    responses:
      200:
        description: Tipo de accidente geografico eliminado correctamente
      404:
        description: Tipo de accidente geografico no encontrado
      500:
        description: Error inesperado al eliminar el tipo de accidente geografico
    """
    try:
        result = db.session.execute(
            db.text(f"DELETE FROM {TABLE_NAME} WHERE id = :id"),
            {"id": id},
        )
        if getattr(result, "rowcount", 0) == 0:
            db.session.rollback()
            return jsonify({"error": "Tipo de accidente geografico no encontrado"}), 404
        db.session.commit()
    except Exception as exc:
        db.session.rollback()
        return jsonify({"error": "Error al eliminar el tipo de accidente geografico", "detalle": str(exc)}), 500

    return jsonify({"mensaje": "Tipo de accidente geografico eliminado correctamente"})
