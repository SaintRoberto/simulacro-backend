from datetime import datetime, timezone

from flask import jsonify, request

from coes_activados import coes_activados_bp
from models import db


TABLE_NAME = "coes_activados"


def _to_iso_optional(value):
    if value is None or value == "":
        return None
    if hasattr(value, "isoformat"):
        return value.isoformat()
    return str(value)


def _serialize_coe_activado(row):
    return {
        "id": getattr(row, "id", None),
        "emergencia_id": getattr(row, "emergencia_id", None),
        "coe_id": getattr(row, "coe_id", None),
        "provincia_id": getattr(row, "provincia_id", None),
        "canton_id": getattr(row, "canton_id", None),
        "parroquia_id": getattr(row, "parroquia_id", None),
        "fecha_activacion": _to_iso_optional(getattr(row, "fecha_activacion", None)),
        "estado_activacion": getattr(row, "estado_activacion", None),
        "activo": getattr(row, "activo", None),
        "creador": getattr(row, "creador", None),
        "creacion": _to_iso_optional(getattr(row, "creacion", None)),
        "modificador": getattr(row, "modificador", None),
        "modificacion": _to_iso_optional(getattr(row, "modificacion", None)),
    }


def _serialize_coe_activado_detalle(row):
    item = _serialize_coe_activado(row)
    optional_fields = [
        "coe_nombre",
        "coe_siglas",
        "provincia_nombre",
        "canton_nombre",
        "parroquia_nombre",
        "estado_activacion_nombre",
    ]
    for field in optional_fields:
        if hasattr(row, field):
            item[field] = getattr(row, field)
    return item


def _get_coe_activado_by_id(item_id):
    return db.session.execute(
        db.text(f"SELECT * FROM {TABLE_NAME} WHERE id = :id"),
        {"id": item_id},
    ).fetchone()


@coes_activados_bp.route("/api/coes_activados", methods=["GET"])
def get_coes_activados():
    """Listar COE activados.
    ---
    tags:
      - COE Activados
    summary: Listar COE activados
    description: Devuelve todos los registros de `coes_activados` ordenados por `id` ascendente, incluyendo los campos de emergencia, COE, ubicación, activación y auditoría.
    responses:
      200:
        description: Lista de COE activados
        schema:
          type: array
          items:
            type: object
            properties:
              id: {type: integer}
              emergencia_id: {type: integer}
              coe_id: {type: integer}
              provincia_id: {type: integer}
              canton_id: {type: integer}
              parroquia_id: {type: integer}
              fecha_activacion: {type: string, format: date-time}
              estado_activacion: {type: integer}
              activo: {type: boolean}
              creador: {type: string}
              creacion: {type: string, format: date-time}
              modificador: {type: string}
              modificacion: {type: string, format: date-time}
      500:
        description: Error inesperado al consultar los COE activados
    """
    result = db.session.execute(db.text(f"SELECT * FROM {TABLE_NAME} ORDER BY id ASC"))
    return jsonify([_serialize_coe_activado(row) for row in result])


@coes_activados_bp.route(
    "/api/coes_activados/emergencia/<int:emergencia_id>",
    methods=["GET"],
)
def get_coes_activados_by_emergencia_by_usuario(emergencia_id):
    """Listar COE activados por emergencia y usuario.
    ---
    tags:
      - COE Activados
    summary: Filtrar COE activados por emergencia y usuario
    description: Devuelve los registros activos de coes_activados visibles para el usuario indicado dentro de la emergencia solicitada. El filtro usa el nivel de COE y el DPA configurado en `usuario_perfil_coe_dpa_mesa` -- un usuario nacional puede ver COE nacional, provinciales y cantonales; un usuario provincial puede ver el COE provincial de su provincia y sus COE cantonales; un usuario cantonal queda limitado a su cantón. La regla DPA sigue el patrón de comodines `(provincia_id = valor OR valor = 0)` y `(canton_id = valor OR valor = 0)`.
    parameters:
      - name: emergencia_id
        in: path
        type: integer
        required: true
        description: Identificador de la emergencia a consultar.
    responses:
      200:
        description: Lista de COE activados visibles para el usuario
        schema:
          type: array
          items:
            type: object
            properties:
              id: {type: integer}
              emergencia_id: {type: integer}
              coe_id: {type: integer}
              coe_nombre: {type: string}
              coe_siglas: {type: string}
              provincia_id: {type: integer}
              provincia_nombre: {type: string}
              canton_id: {type: integer}
              canton_nombre: {type: string}
              parroquia_id: {type: integer}
              parroquia_nombre: {type: string}
              fecha_activacion: {type: string, format: date-time}
              estado_activacion: {type: integer}
              estado_activacion_nombre: {type: string}
              activo: {type: boolean}
              creador: {type: string}
              creacion: {type: string, format: date-time}
              modificador: {type: string}
              modificacion: {type: string, format: date-time}
      500:
        description: Error inesperado al consultar los COE activados por emergencia y usuario
    """
    query = db.text(
        f"""
        SELECT
            ca.id,
            ca.emergencia_id,
            ca.coe_id,
            c.nombre AS coe_nombre,
            c.siglas AS coe_siglas,
            ca.provincia_id,
            p.nombre AS provincia_nombre,
            ca.canton_id,
            k.nombre AS canton_nombre,
            ca.parroquia_id,
            q.nombre AS parroquia_nombre,
            ca.fecha_activacion,
            ca.estado_activacion,
            e.nombre AS estado_activacion_nombre,
            ca.activo,
            ca.creador,
            ca.creacion,
            ca.modificador,
            ca.modificacion
        FROM public.coes_activados ca
        INNER JOIN public.coes c
            ON c.id = ca.coe_id
        LEFT JOIN public.provincias p
            ON p.id = ca.provincia_id
        LEFT JOIN public.cantones k
            ON k.provincia_id = ca.provincia_id
           AND k.id = ca.canton_id
        LEFT JOIN public.parroquias q
            ON q.provincia_id = ca.provincia_id
           AND q.canton_id = ca.canton_id
           AND q.id = ca.parroquia_id
        LEFT JOIN public.coe_activado_estados e
            ON e.id = ca.estado_activacion
        WHERE ca.emergencia_id = :emergencia_id
          AND COALESCE(ca.activo, true) = true
          AND EXISTS (
              SELECT 1
              FROM public.usuario_perfil_coe_dpa_mesa x
              WHERE COALESCE(x.activo, true) = true
                AND ca.coe_id >= x.coe_id
                AND (ca.provincia_id = x.provincia_id OR x.provincia_id IN (0, -1))
                AND (ca.canton_id = x.canton_id OR x.canton_id IN (0, -1))
                AND (ca.parroquia_id = x.parroquia_id OR x.parroquia_id IN (0, -1))
          )
        ORDER BY ca.coe_id ASC, ca.provincia_id ASC, ca.canton_id ASC, ca.parroquia_id ASC, ca.id ASC
        """
    )
    result = db.session.execute(
        query,
        {"emergencia_id": emergencia_id},
    )
    return jsonify([_serialize_coe_activado_detalle(row) for row in result])


@coes_activados_bp.route("/api/coes_activados/<int:id>", methods=["GET"])
def get_coe_activado(id):
    """Obtener un COE activado por ID.
    ---
    tags:
      - COE Activados
    summary: Obtener COE activado por ID
    description: Devuelve el registro de `coes_activados` identificado por `id`.
    parameters:
      - name: id
        in: path
        type: integer
        required: true
        description: Identificador único del COE activado.
    responses:
      200:
        description: COE activado encontrado
        schema:
          type: object
          properties:
            id: {type: integer}
            emergencia_id: {type: integer}
            coe_id: {type: integer}
            provincia_id: {type: integer}
            canton_id: {type: integer}
            parroquia_id: {type: integer}
            fecha_activacion: {type: string, format: date-time}
            estado_activacion: {type: integer}
            activo: {type: boolean}
            creador: {type: string}
            creacion: {type: string, format: date-time}
            modificador: {type: string}
            modificacion: {type: string, format: date-time}
      404:
        description: COE activado no encontrado
      500:
        description: Error inesperado al consultar el COE activado
    """
    item = _get_coe_activado_by_id(id)
    if not item:
        return jsonify({"error": "COE activado no encontrado"}), 404
    return jsonify(_serialize_coe_activado(item))


@coes_activados_bp.route("/api/coes_activados", methods=["POST"])
def create_coe_activado():
    """Crear un COE activado.
    ---
    tags:
      - COE Activados
    summary: Crear COE activado
    description: Inserta un registro en `coes_activados` con la emergencia, COE, ubicación de referencia, fecha de activación, estado y campos de auditoría.
    consumes:
      - application/json
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          required:
            - emergencia_id
            - coe_id
            - provincia_id
            - canton_id
            - parroquia_id
          properties:
            emergencia_id: {type: integer}
            coe_id: {type: integer}
            provincia_id: {type: integer}
            canton_id: {type: integer}
            parroquia_id: {type: integer}
            fecha_activacion: {type: string, format: date-time}
            estado_activacion: {type: integer, default: 1}
            activo: {type: boolean, default: true}
            creador: {type: string}
            modificador: {type: string}
    responses:
      201:
        description: COE activado creado correctamente
        schema:
          type: object
          properties:
            id: {type: integer}
            emergencia_id: {type: integer}
            coe_id: {type: integer}
            provincia_id: {type: integer}
            canton_id: {type: integer}
            parroquia_id: {type: integer}
            fecha_activacion: {type: string, format: date-time}
            estado_activacion: {type: integer}
            activo: {type: boolean}
            creador: {type: string}
            creacion: {type: string, format: date-time}
            modificador: {type: string}
            modificacion: {type: string, format: date-time}
      400:
        description: Campos requeridos faltantes o cuerpo JSON inválido
      500:
        description: Error inesperado al crear el COE activado
    """
    data = request.get_json(silent=True) or {}
    required_fields = ["emergencia_id", "coe_id", "provincia_id", "canton_id", "parroquia_id"]
    missing_fields = [field for field in required_fields if data.get(field) is None]
    if missing_fields:
        return jsonify({"error": f"Campos requeridos faltantes: {', '.join(missing_fields)}"}), 400

    now = datetime.now(timezone.utc)
    creador = data.get("creador", "Sistema")
    modificador = data.get("modificador", creador)

    query = db.text(
        f"""
        INSERT INTO {TABLE_NAME} (
            emergencia_id,
            coe_id,
            provincia_id,
            canton_id,
            parroquia_id,
            fecha_activacion,
            estado_activacion,
            activo,
            creador,
            creacion,
            modificador,
            modificacion
        )
        VALUES (
            :emergencia_id,
            :coe_id,
            :provincia_id,
            :canton_id,
            :parroquia_id,
            :fecha_activacion,
            :estado_activacion,
            :activo,
            :creador,
            :creacion,
            :modificador,
            :modificacion
        )
        RETURNING id
        """
    )

    result = db.session.execute(
        query,
        {
            "emergencia_id": data["emergencia_id"],
            "coe_id": data["coe_id"],
            "provincia_id": data["provincia_id"],
            "canton_id": data["canton_id"],
            "parroquia_id": data["parroquia_id"],
            "fecha_activacion": data.get("fecha_activacion"),
            "estado_activacion": data.get("estado_activacion", 1),
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
        return jsonify({"error": "No se pudo crear el COE activado"}), 500

    item_id = row[0]
    db.session.commit()

    item = _get_coe_activado_by_id(item_id)
    if not item:
        return jsonify({"error": "COE activado no encontrado"}), 404

    return jsonify(_serialize_coe_activado(item)), 201


@coes_activados_bp.route("/api/coes_activados/<int:id>", methods=["PUT"])
def update_coe_activado(id):
    """Actualizar un COE activado.
    ---
    tags:
      - COE Activados
    summary: Actualizar COE activado
    description: Actualiza de forma parcial los campos editables del registro `coes_activados` identificado por `id`.
    consumes:
      - application/json
    parameters:
      - name: id
        in: path
        type: integer
        required: true
        description: Identificador único del COE activado.
      - in: body
        name: body
        required: true
        schema:
          type: object
          properties:
            emergencia_id: {type: integer}
            coe_id: {type: integer}
            provincia_id: {type: integer}
            canton_id: {type: integer}
            parroquia_id: {type: integer}
            fecha_activacion: {type: string, format: date-time}
            estado_activacion: {type: integer}
            activo: {type: boolean}
            modificador: {type: string}
    responses:
      200:
        description: COE activado actualizado correctamente
        schema:
          type: object
          properties:
            id: {type: integer}
            emergencia_id: {type: integer}
            coe_id: {type: integer}
            provincia_id: {type: integer}
            canton_id: {type: integer}
            parroquia_id: {type: integer}
            fecha_activacion: {type: string, format: date-time}
            estado_activacion: {type: integer}
            activo: {type: boolean}
            creador: {type: string}
            creacion: {type: string, format: date-time}
            modificador: {type: string}
            modificacion: {type: string, format: date-time}
      400:
        description: No se enviaron campos válidos para actualizar
      404:
        description: COE activado no encontrado
      500:
        description: Error inesperado al actualizar el COE activado
    """
    data = request.get_json(silent=True) or {}
    now = datetime.now(timezone.utc)

    updatable_fields = [
        "emergencia_id",
        "coe_id",
        "provincia_id",
        "canton_id",
        "parroquia_id",
        "fecha_activacion",
        "estado_activacion",
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
        return jsonify({"error": "No fields to update"}), 400

    update_fields.append("modificador = :modificador")
    update_fields.append("modificacion = :modificacion")

    query = db.text(
        f"""
        UPDATE {TABLE_NAME}
        SET {", ".join(update_fields)}
        WHERE id = :id
        """
    )

    result = db.session.execute(query, params)
    if getattr(result, "rowcount", 0) == 0:
        db.session.rollback()
        return jsonify({"error": "COE activado no encontrado"}), 404

    db.session.commit()

    item = _get_coe_activado_by_id(id)
    if not item:
        return jsonify({"error": "COE activado no encontrado"}), 404

    return jsonify(_serialize_coe_activado(item))


@coes_activados_bp.route("/api/coes_activados/<int:id>", methods=["DELETE"])
def delete_coe_activado(id):
    """Eliminar un COE activado.
    ---
    tags:
      - COE Activados
    summary: Eliminar COE activado
    description: Elimina físicamente el registro de `coes_activados` identificado por `id`.
    parameters:
      - name: id
        in: path
        type: integer
        required: true
        description: Identificador único del COE activado.
    responses:
      200:
        description: COE activado eliminado correctamente
      404:
        description: COE activado no encontrado
      500:
        description: Error inesperado al eliminar el COE activado
    """
    result = db.session.execute(
        db.text(f"DELETE FROM {TABLE_NAME} WHERE id = :id"),
        {"id": id},
    )
    if getattr(result, "rowcount", 0) == 0:
        db.session.rollback()
        return jsonify({"error": "COE activado no encontrado"}), 404

    db.session.commit()
    return jsonify({"mensaje": "COE activado eliminado correctamente"})


@coes_activados_bp.route("/api/coes_activados_estados", methods=["GET"])
def get_coe_activados_estados():
    """Listar estados de activación de COE.
    ---
    tags:
      - COE Activados
    summary: Listar estados de activación de COE
    description: Devuelve todos los registros de `coe_activado_estados` ordenados
    responses:
      200:
        description: Lista de estados de activación de COE
        schema:
          type: array
          items:
            type: object
            properties:
              id: {type: integer}
              nombre: {type: string}
      500:
        description: Error inesperado al consultar los estados de activación de COE
    """
    query = db.text("SELECT * FROM coe_activado_estados WHERE activo = true ORDER BY id ASC")
    result = db.session.execute(query)
    return jsonify([{"id": row.id, "nombre": row.nombre} for row in result])
  