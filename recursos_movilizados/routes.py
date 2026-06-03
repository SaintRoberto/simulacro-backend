from datetime import datetime, timezone

from flask import jsonify, request

from models import db
from recursos_movilizados import recursos_movilizados_bp


def _to_iso_optional(value):
    if value is None or value == "":
        return None
    if hasattr(value, "isoformat"):
        return value.isoformat()
    return str(value)


def _to_float_optional(value):
    if value is None or value == "":
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        if isinstance(value, str):
            normalized_value = value.strip().replace(",", ".")
            if not normalized_value:
                return None
            try:
                return float(normalized_value)
            except (TypeError, ValueError):
                return None
        return None


def _serialize_recurso(row):
    return {
        "id": getattr(row, "id", None),
        "emergencia_id": getattr(row, "emergencia_id", None),
        "recurso_tipo_id": getattr(row, "recurso_tipo_id", None),
        "recurso_tipo": getattr(row, "recurso_tipo", None),
        "institucion_id": getattr(row, "institucion_id", None),
        "institucion": getattr(row, "institucion", None),
        "provincia_destino_id": getattr(row, "provincia_destino_id", None),
        "provincia_nombre": getattr(row, "provincia_nombre", None),
        "canton_destino_id": getattr(row, "canton_destino_id", None),
        "canton_nombre": getattr(row, "canton_nombre", None),
        "parroquia_destino_id": getattr(row, "parroquia_destino_id", None),
        "parroquia_nombre": getattr(row, "parroquia_nombre", None),
        "longitud_destino": _to_float_optional(getattr(row, "longitud_destino", None)),
        "latitud_destino": _to_float_optional(getattr(row, "latitud_destino", None)),
        "fecha_inicio": _to_iso_optional(getattr(row, "fecha_inicio", None)),
        "fecha_fin": _to_iso_optional(getattr(row, "fecha_fin", None)),
        "cantidad_asignada": getattr(row, "cantidad_asignada", None),
        "activo": getattr(row, "activo", None),
        "creador": getattr(row, "creador", None),
        "creacion": _to_iso_optional(getattr(row, "creacion", None)),
        "modificador": getattr(row, "modificador", None),
        "modificacion": _to_iso_optional(getattr(row, "modificacion", None)),
    }


@recursos_movilizados_bp.route("/api/recursos_movilizados", methods=["GET"])
def get_recursos_movilizados():
    """Listar todos los recursos movilizados.
    ---
    tags:
      - Recursos Movilizados
    summary: Listar recursos movilizados
    description: Devuelve todos los registros de `recursos_movilizados` ordenados por `id` ascendente.
    responses:
      200:
        description: Lista de recursos movilizados
      500:
        description: Error inesperado al consultar los recursos movilizados
    """
    result = db.session.execute(db.text("SELECT * FROM recursos_movilizados ORDER BY id ASC"))
    return jsonify([_serialize_recurso(row) for row in result])


@recursos_movilizados_bp.route(
    "/api/recursos_movilizados/emergencia/<int:emergencia_id>/usuario/<int:usuario_id>",
    methods=["GET"],
)
def get_recursos_movilizados_by_emergencia_by_usuario(emergencia_id, usuario_id):
    """Obtener recursos movilizados por emergencia y usuario.
    ---
    tags:
      - Recursos Movilizados
    summary: Filtrar recursos movilizados por emergencia y usuario
    description: Devuelve los recursos movilizados visibles para el usuario indicado dentro de la emergencia solicitada, incluyendo información de ubicación, institución y tipo de recurso.
    parameters:
      - name: emergencia_id
        in: path
        type: integer
        required: true
      - name: usuario_id
        in: path
        type: integer
        required: true
    responses:
      200:
        description: Lista filtrada de recursos movilizados
      500:
        description: Error inesperado al consultar los recursos movilizados
    """
    query = db.text(
        """
        SELECT DISTINCT
            r.id,
            r.emergencia_id,
            r.recurso_tipo_id,
            rt.nombre AS recurso_tipo,
            r.institucion_id,
            i.nombre AS institucion,
            r.provincia_destino_id,
            p.nombre AS provincia_nombre,
            r.canton_destino_id,
            c.nombre AS canton_nombre,
            r.parroquia_destino_id,
            q.nombre AS parroquia_nombre,
            r.longitud_destino,
            r.latitud_destino,
            r.fecha_inicio,
            r.fecha_fin,
            r.cantidad_asignada,
            r.activo,
            r.creador,
            r.creacion,
            r.modificador,
            r.modificacion
        FROM recursos_movilizados r
        INNER JOIN public.usuario_perfil_coe_dpa_mesa x
            ON (r.provincia_destino_id = x.provincia_id OR x.provincia_id = 0)
           AND (r.canton_destino_id = x.canton_id OR x.canton_id = 0)
        LEFT JOIN public.provincias p
            ON r.provincia_destino_id = p.id
        LEFT JOIN public.cantones c
            ON r.canton_destino_id = c.id
        LEFT JOIN public.parroquias q
            ON r.provincia_destino_id = q.provincia_id
           AND r.canton_destino_id = q.canton_id
           AND r.parroquia_destino_id = q.id
        LEFT JOIN public.recurso_tipos rt
            ON r.recurso_tipo_id = rt.id
        LEFT JOIN public.instituciones i
            ON r.institucion_id = i.id
        WHERE r.emergencia_id = :emergencia_id
          AND x.usuario_id = :usuario_id
          AND COALESCE(r.activo, true) = true
        ORDER BY r.id ASC
        """
    )
    result = db.session.execute(query, {"emergencia_id": emergencia_id, "usuario_id": usuario_id})
    return jsonify([_serialize_recurso(row) for row in result])


@recursos_movilizados_bp.route("/api/recursos_movilizados", methods=["POST"])
def create_recurso_movilizado():
    """Crear un nuevo recurso movilizado.
    ---
    tags:
      - Recursos Movilizados
    summary: Crear recurso movilizado
    description: Inserta un registro en `recursos_movilizados` con los campos de emergencia, tipo de recurso, institución, destino y auditoría.
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
            - recurso_tipo_id
            - institucion_id
            - provincia_destino_id
            - canton_destino_id
            - parroquia_destino_id
          properties:
            emergencia_id: {type: integer}
            recurso_tipo_id: {type: integer}
            institucion_id: {type: integer}
            provincia_destino_id: {type: integer}
            canton_destino_id: {type: integer}
            parroquia_destino_id: {type: integer}
            longitud_destino: {type: number}
            latitud_destino: {type: number}
            fecha_inicio: {type: string}
            fecha_fin: {type: string}
            cantidad_asignada: {type: integer}
            activo: {type: boolean}
            creador: {type: string}
            modificador: {type: string}
            modificacion: {type: string}
    responses:
      201:
        description: Recurso movilizado creado correctamente
      400:
        description: Campos requeridos faltantes o datos inválidos
      500:
        description: Error inesperado al crear el recurso movilizado
    """
    data = request.get_json(silent=True) or {}
    required_fields = [
        "emergencia_id",
        "recurso_tipo_id",
        "institucion_id",
        "provincia_destino_id",
        "canton_destino_id",
        "parroquia_destino_id",
    ]
    missing_fields = [field for field in required_fields if data.get(field) is None]
    if missing_fields:
        return jsonify({"error": f"Campos requeridos faltantes: {', '.join(missing_fields)}"}), 400

    now = datetime.now(timezone.utc)
    creador = data.get("creador", "Sistema")
    modificador = data.get("modificador", creador)

    query = db.text(
        """
        INSERT INTO recursos_movilizados (
            emergencia_id,
            recurso_tipo_id,
            institucion_id,
            provincia_destino_id,
            canton_destino_id,
            parroquia_destino_id,
            longitud_destino,
            latitud_destino,
            fecha_inicio,
            fecha_fin,
            cantidad_asignada,
            activo,
            creador,
            creacion,
            modificador,
            modificacion
        )
        VALUES (
            :emergencia_id,
            :recurso_tipo_id,
            :institucion_id,
            :provincia_destino_id,
            :canton_destino_id,
            :parroquia_destino_id,
            :longitud_destino,
            :latitud_destino,
            :fecha_inicio,
            :fecha_fin,
            :cantidad_asignada,
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
            "recurso_tipo_id": data["recurso_tipo_id"],
            "institucion_id": data["institucion_id"],
            "provincia_destino_id": data["provincia_destino_id"],
            "canton_destino_id": data["canton_destino_id"],
            "parroquia_destino_id": data["parroquia_destino_id"],
            "longitud_destino": data.get("longitud_destino", 0),
            "latitud_destino": data.get("latitud_destino", 0),
            "fecha_inicio": data.get("fecha_inicio"),
            "fecha_fin": data.get("fecha_fin"),
            "cantidad_asignada": data.get("cantidad_asignada", 0),
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
        return jsonify({"error": "No se pudo crear el recurso movilizado"}), 500

    recurso_id = row[0]
    db.session.commit()

    recurso = db.session.execute(
        db.text("SELECT * FROM recursos_movilizados WHERE id = :id"),
        {"id": recurso_id},
    ).fetchone()
    if not recurso:
        return jsonify({"error": "Recurso movilizado no encontrado"}), 404

    return jsonify(_serialize_recurso(recurso)), 201


@recursos_movilizados_bp.route("/api/recursos_movilizados/<int:id>", methods=["GET"])
def get_recurso_movilizado(id):
    """Obtener un recurso movilizado por ID.
    ---
    tags:
      - Recursos Movilizados
    summary: Obtener recurso movilizado por ID
    description: Devuelve el registro identificado por `id`.
    parameters:
      - name: id
        in: path
        type: integer
        required: true
    responses:
      200:
        description: Recurso movilizado encontrado
      404:
        description: Recurso movilizado no encontrado
    """
    recurso = db.session.execute(
        db.text("SELECT * FROM recursos_movilizados WHERE id = :id"),
        {"id": id},
    ).fetchone()
    if not recurso:
        return jsonify({"error": "Recurso movilizado no encontrado"}), 404
    return jsonify(_serialize_recurso(recurso))


@recursos_movilizados_bp.route("/api/recursos_movilizados/<int:id>", methods=["PUT"])
def update_recurso_movilizado(id):
    """Actualizar un recurso movilizado.
    ---
    tags:
      - Recursos Movilizados
    summary: Actualizar recurso movilizado
    description: Actualiza de forma parcial los campos editables del recurso movilizado identificado por `id`.
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
            emergencia_id: {type: integer}
            recurso_tipo_id: {type: integer}
            institucion_id: {type: integer}
            provincia_destino_id: {type: integer}
            canton_destino_id: {type: integer}
            parroquia_destino_id: {type: integer}
            longitud_destino: {type: number}
            latitud_destino: {type: number}
            fecha_inicio: {type: string}
            fecha_fin: {type: string}
            cantidad_asignada: {type: integer}
            activo: {type: boolean}
            modificador: {type: string}
    responses:
      200:
        description: Recurso movilizado actualizado correctamente
      400:
        description: No se enviaron campos para actualizar
      404:
        description: Recurso movilizado no encontrado
    """
    data = request.get_json(silent=True) or {}
    now = datetime.now(timezone.utc)

    updatable_fields = [
        "emergencia_id",
        "recurso_tipo_id",
        "institucion_id",
        "provincia_destino_id",
        "canton_destino_id",
        "parroquia_destino_id",
        "longitud_destino",
        "latitud_destino",
        "fecha_inicio",
        "fecha_fin",
        "cantidad_asignada",
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
        UPDATE recursos_movilizados
        SET {", ".join(update_fields)}
        WHERE id = :id
        """
    )

    result = db.session.execute(query, params)
    if getattr(result, "rowcount", 0) == 0:
        return jsonify({"error": "Recurso movilizado no encontrado"}), 404

    db.session.commit()

    recurso = db.session.execute(
        db.text("SELECT * FROM recursos_movilizados WHERE id = :id"),
        {"id": id},
    ).fetchone()
    if not recurso:
        return jsonify({"error": "Recurso movilizado no encontrado"}), 404

    return jsonify(_serialize_recurso(recurso))


@recursos_movilizados_bp.route("/api/recursos_movilizados/<int:id>", methods=["DELETE"])
def delete_recurso_movilizado(id):
    """Eliminar un recurso movilizado.
    ---
    tags:
      - Recursos Movilizados
    summary: Eliminar recurso movilizado
    description: Elimina físicamente el registro identificado por `id`.
    parameters:
      - name: id
        in: path
        type: integer
        required: true
    responses:
      200:
        description: Recurso movilizado eliminado correctamente
      404:
        description: Recurso movilizado no encontrado
    """
    result = db.session.execute(
        db.text("DELETE FROM recursos_movilizados WHERE id = :id"),
        {"id": id},
    )
    if getattr(result, "rowcount", 0) == 0:
        return jsonify({"error": "Recurso movilizado no encontrado"}), 404

    db.session.commit()
    return jsonify({"mensaje": "Recurso movilizado eliminado correctamente"})
