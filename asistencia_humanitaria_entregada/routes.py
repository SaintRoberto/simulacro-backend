from datetime import datetime, timezone

from flask import jsonify, request

from asistencia_humanitaria_entregada import asistencia_humanitaria_entregada_bp
from models import db


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


def _serialize_asistencia(row):
    return {
        "id": getattr(row, "id", None),
        "emergencia_id": getattr(row, "emergencia_id", None),
        "recurso_tipo_id": getattr(row, "recurso_tipo_id", None),
        "recurso_tipo": getattr(row, "recurso_tipo", None),
        "recurso_grupo_id": getattr(row, "recurso_grupo_id", None),
        "recurso_grupo": getattr(row, "recurso_grupo", None),
        "recurso_categoria_id": getattr(row, "recurso_categoria_id", None),
        "recurso_categoria": getattr(row, "recurso_categoria", None),
        "institucion_donante_id": getattr(row, "institucion_donante_id", None),
        "institucion_donante": getattr(row, "institucion_donante", None),
        "provincia_destino_id": getattr(row, "provincia_destino_id", None),
        "provincia_destino": getattr(row, "provincia_destino", None),
        "canton_destino_id": getattr(row, "canton_destino_id", None),
        "canton_destino": getattr(row, "canton_destino", None),
        "parroquia_destino_id": getattr(row, "parroquia_destino_id", None),
        "parroquia_destino": getattr(row, "parroquia_destino", None),
        "sector_destino": getattr(row, "sector_destino", None),
        "longitud_destino": _to_float_optional(getattr(row, "longitud_destino", None)),
        "latitud_destino": _to_float_optional(getattr(row, "latitud_destino", None)),
        "fecha_entrega": _to_iso_optional(getattr(row, "fecha_entrega", None)),
        "cantidad_entregada": getattr(row, "cantidad_entregada", None),
        "familias_beneficiadas": getattr(row, "familias_beneficiadas", None),
        "personas_beneficiadas": getattr(row, "personas_beneficiadas", None),
        "activo": getattr(row, "activo", None),
        "creador": getattr(row, "creador", None),
        "creacion": _to_iso_optional(getattr(row, "creacion", None)),
        "modificador": getattr(row, "modificador", None),
        "modificacion": _to_iso_optional(getattr(row, "modificacion", None)),
    }


def _select_asistencias(where_clause=""):
    return db.text(
        f"""
        SELECT
            a.*,
            rt.nombre AS recurso_tipo,
            rg.id AS recurso_grupo_id,
            rg.nombre AS recurso_grupo,
            rc.id AS recurso_categoria_id,
            rc.nombre AS recurso_categoria,
            i.nombre AS institucion_donante,
            p.nombre AS provincia_destino,
            c.nombre AS canton_destino,
            q.nombre AS parroquia_destino
        FROM public.asistencia_humanitaria_entregada a
        INNER JOIN public.recurso_tipos rt
            ON a.recurso_tipo_id = rt.id
        INNER JOIN public.recurso_grupos rg
            ON rt.recurso_grupo_id = rg.id
           AND rg.recurso_categoria_id = 1
        INNER JOIN public.recurso_categorias rc
            ON rg.recurso_categoria_id = rc.id
        LEFT JOIN public.instituciones i
            ON a.institucion_donante_id = i.id
        LEFT JOIN public.provincias p
            ON a.provincia_destino_id = p.id
        LEFT JOIN public.cantones c
            ON a.canton_destino_id = c.id
        LEFT JOIN public.parroquias q
            ON a.provincia_destino_id = q.provincia_id
           AND a.canton_destino_id = q.canton_id
           AND a.parroquia_destino_id = q.id
        {where_clause}
        ORDER BY a.id ASC
        """
    )


def _get_asistencia_by_id(asistencia_id):
    return db.session.execute(
        _select_asistencias("WHERE a.id = :id"),
        {"id": asistencia_id},
    ).fetchone()


def _recurso_tipo_es_asistencia_humanitaria(recurso_tipo_id):
    result = db.session.execute(
        db.text(
            """
            SELECT rt.id
            FROM public.recurso_tipos rt
            INNER JOIN public.recurso_grupos rg
                ON rt.recurso_grupo_id = rg.id
            WHERE rt.id = :recurso_tipo_id
              AND rg.recurso_categoria_id = 1
              AND COALESCE(rt.activo, true) = true
              AND COALESCE(rg.activo, true) = true
            """
        ),
        {"recurso_tipo_id": recurso_tipo_id},
    ).fetchone()
    return result is not None


@asistencia_humanitaria_entregada_bp.route("/api/asistencia_humanitaria_entregada", methods=["GET"])
def get_asistencia_humanitaria_entregada():
    """Listar asistencias humanitarias entregadas.
    ---
    tags:
      - Asistencia Humanitaria Entregada
    summary: Listar asistencias humanitarias entregadas
    description: Devuelve los registros de `asistencia_humanitaria_entregada` vinculados a tipos de recurso de asistencia humanitaria.
    responses:
      200:
        description: Lista de asistencias humanitarias entregadas
    """
    result = db.session.execute(_select_asistencias())
    return jsonify([_serialize_asistencia(row) for row in result])


@asistencia_humanitaria_entregada_bp.route(
    "/api/asistencia_humanitaria_entregada/emergencia/<int:emergencia_id>/usuario/<int:usuario_id>",
    methods=["GET"],
)
def get_asistencia_humanitaria_entregada_by_emergencia_by_usuario(emergencia_id, usuario_id):
    """Obtener asistencia humanitaria entregada por emergencia y usuario.
    ---
    tags:
      - Asistencia Humanitaria Entregada
    summary: Filtrar asistencia humanitaria entregada por emergencia y usuario
    description: Devuelve las asistencias visibles para el usuario indicado dentro de la emergencia solicitada, segun su alcance DPA y los recursos de categoria 1.
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
        description: Lista filtrada de asistencias humanitarias entregadas
    """
    query = db.text(
        """
        SELECT DISTINCT
            a.*,
            rt.nombre AS recurso_tipo,
            rg.id AS recurso_grupo_id,
            rg.nombre AS recurso_grupo,
            rc.id AS recurso_categoria_id,
            rc.nombre AS recurso_categoria,
            i.nombre AS institucion_donante,
            p.nombre AS provincia_destino,
            c.nombre AS canton_destino,
            q.nombre AS parroquia_destino
        FROM public.asistencia_humanitaria_entregada a
        INNER JOIN public.usuario_perfil_coe_dpa_mesa x
            ON (a.provincia_destino_id = x.provincia_id OR x.provincia_id = 0)
           AND (a.canton_destino_id = x.canton_id OR x.canton_id = 0)
        INNER JOIN public.recurso_tipos rt
            ON a.recurso_tipo_id = rt.id
        INNER JOIN public.recurso_grupos rg
            ON rt.recurso_grupo_id = rg.id
           AND rg.recurso_categoria_id = 1
        INNER JOIN public.recurso_categorias rc
            ON rg.recurso_categoria_id = rc.id
        LEFT JOIN public.instituciones i
            ON a.institucion_donante_id = i.id
        LEFT JOIN public.provincias p
            ON a.provincia_destino_id = p.id
        LEFT JOIN public.cantones c
            ON a.canton_destino_id = c.id
        LEFT JOIN public.parroquias q
            ON a.provincia_destino_id = q.provincia_id
           AND a.canton_destino_id = q.canton_id
           AND a.parroquia_destino_id = q.id
        WHERE a.emergencia_id = :emergencia_id
          AND x.usuario_id = :usuario_id
          AND COALESCE(a.activo, true) = true
        ORDER BY a.id ASC
        """
    )
    result = db.session.execute(query, {"emergencia_id": emergencia_id, "usuario_id": usuario_id})
    return jsonify([_serialize_asistencia(row) for row in result])


@asistencia_humanitaria_entregada_bp.route("/api/asistencia_humanitaria_entregada", methods=["POST"])
def create_asistencia_humanitaria_entregada():
    """Crear asistencia humanitaria entregada.
    ---
    tags:
      - Asistencia Humanitaria Entregada
    summary: Crear asistencia humanitaria entregada
    description: Inserta un registro en `asistencia_humanitaria_entregada` validando que `recurso_tipo_id` pertenezca a la categoria 1.
    consumes:
      - application/json
    responses:
      201:
        description: Asistencia humanitaria entregada creada correctamente
      400:
        description: Campos requeridos faltantes o recurso_tipo_id invalido
    """
    data = request.get_json(silent=True) or {}
    required_fields = [
        "emergencia_id",
        "recurso_tipo_id",
        "institucion_donante_id",
        "provincia_destino_id",
        "canton_destino_id",
        "parroquia_destino_id",
        "sector_destino",
        "familias_beneficiadas",
        "personas_beneficiadas",
    ]
    missing_fields = [field for field in required_fields if data.get(field) is None]
    if missing_fields:
        return jsonify({"error": f"Campos requeridos faltantes: {', '.join(missing_fields)}"}), 400

    if not _recurso_tipo_es_asistencia_humanitaria(data["recurso_tipo_id"]):
        return jsonify({"error": "recurso_tipo_id debe pertenecer a la categoria de asistencia humanitaria"}), 400

    now = datetime.now(timezone.utc)
    creador = data.get("creador", "Sistema")
    modificador = data.get("modificador", creador)

    result = db.session.execute(
        db.text(
            """
            INSERT INTO public.asistencia_humanitaria_entregada (
                emergencia_id,
                recurso_tipo_id,
                institucion_donante_id,
                provincia_destino_id,
                canton_destino_id,
                parroquia_destino_id,
                sector_destino,
                longitud_destino,
                latitud_destino,
                fecha_entrega,
                cantidad_entregada,
                familias_beneficiadas,
                personas_beneficiadas,
                activo,
                creador,
                creacion,
                modificador,
                modificacion
            )
            VALUES (
                :emergencia_id,
                :recurso_tipo_id,
                :institucion_donante_id,
                :provincia_destino_id,
                :canton_destino_id,
                :parroquia_destino_id,
                :sector_destino,
                :longitud_destino,
                :latitud_destino,
                :fecha_entrega,
                :cantidad_entregada,
                :familias_beneficiadas,
                :personas_beneficiadas,
                :activo,
                :creador,
                :creacion,
                :modificador,
                :modificacion
            )
            RETURNING id
            """
        ),
        {
            "emergencia_id": data["emergencia_id"],
            "recurso_tipo_id": data["recurso_tipo_id"],
            "institucion_donante_id": data["institucion_donante_id"],
            "provincia_destino_id": data["provincia_destino_id"],
            "canton_destino_id": data["canton_destino_id"],
            "parroquia_destino_id": data["parroquia_destino_id"],
            "sector_destino": data["sector_destino"],
            "longitud_destino": data.get("longitud_destino", 0),
            "latitud_destino": data.get("latitud_destino", 0),
            "fecha_entrega": data.get("fecha_entrega"),
            "cantidad_entregada": data.get("cantidad_entregada", 0),
            "familias_beneficiadas": data["familias_beneficiadas"],
            "personas_beneficiadas": data["personas_beneficiadas"],
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
        return jsonify({"error": "No se pudo crear el registro"}), 500

    asistencia_id = row[0]
    db.session.commit()

    asistencia = _get_asistencia_by_id(asistencia_id)
    if not asistencia:
        return jsonify({"error": "Asistencia humanitaria entregada no encontrada"}), 404

    return jsonify(_serialize_asistencia(asistencia)), 201


@asistencia_humanitaria_entregada_bp.route("/api/asistencia_humanitaria_entregada/<int:id>", methods=["GET"])
def get_asistencia_humanitaria_entregada_item(id):
    """Obtener asistencia humanitaria entregada por ID.
    ---
    tags:
      - Asistencia Humanitaria Entregada
    summary: Obtener asistencia humanitaria entregada por ID
    parameters:
      - name: id
        in: path
        type: integer
        required: true
    responses:
      200:
        description: Asistencia humanitaria entregada encontrada
      404:
        description: Asistencia humanitaria entregada no encontrada
    """
    asistencia = _get_asistencia_by_id(id)
    if not asistencia:
        return jsonify({"error": "Asistencia humanitaria entregada no encontrada"}), 404
    return jsonify(_serialize_asistencia(asistencia))


@asistencia_humanitaria_entregada_bp.route("/api/asistencia_humanitaria_entregada/<int:id>", methods=["PUT"])
def update_asistencia_humanitaria_entregada(id):
    """Actualizar asistencia humanitaria entregada.
    ---
    tags:
      - Asistencia Humanitaria Entregada
    summary: Actualizar asistencia humanitaria entregada
    description: Actualiza parcialmente un registro de `asistencia_humanitaria_entregada`.
    consumes:
      - application/json
    responses:
      200:
        description: Asistencia humanitaria entregada actualizada correctamente
      400:
        description: No se enviaron campos para actualizar o recurso_tipo_id invalido
      404:
        description: Asistencia humanitaria entregada no encontrada
    """
    data = request.get_json(silent=True) or {}
    if "recurso_tipo_id" in data and not _recurso_tipo_es_asistencia_humanitaria(data["recurso_tipo_id"]):
        return jsonify({"error": "recurso_tipo_id debe pertenecer a la categoria de asistencia humanitaria"}), 400

    updatable_fields = [
        "emergencia_id",
        "recurso_tipo_id",
        "institucion_donante_id",
        "provincia_destino_id",
        "canton_destino_id",
        "parroquia_destino_id",
        "sector_destino",
        "longitud_destino",
        "latitud_destino",
        "fecha_entrega",
        "cantidad_entregada",
        "familias_beneficiadas",
        "personas_beneficiadas",
        "activo",
    ]

    params = {
        "id": id,
        "modificador": data.get("modificador", "Sistema"),
        "modificacion": datetime.now(timezone.utc),
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

    result = db.session.execute(
        db.text(
            f"""
            UPDATE public.asistencia_humanitaria_entregada
            SET {", ".join(update_fields)}
            WHERE id = :id
            """
        ),
        params,
    )
    if getattr(result, "rowcount", 0) == 0:
        return jsonify({"error": "Asistencia humanitaria entregada no encontrada"}), 404

    db.session.commit()

    asistencia = _get_asistencia_by_id(id)
    if not asistencia:
        return jsonify({"error": "Asistencia humanitaria entregada no encontrada"}), 404

    return jsonify(_serialize_asistencia(asistencia))


@asistencia_humanitaria_entregada_bp.route("/api/asistencia_humanitaria_entregada/<int:id>", methods=["DELETE"])
def delete_asistencia_humanitaria_entregada(id):
    """Eliminar asistencia humanitaria entregada.
    ---
    tags:
      - Asistencia Humanitaria Entregada
    summary: Eliminar asistencia humanitaria entregada
    parameters:
      - name: id
        in: path
        type: integer
        required: true
    responses:
      200:
        description: Asistencia humanitaria entregada eliminada correctamente
      404:
        description: Asistencia humanitaria entregada no encontrada
    """
    result = db.session.execute(
        db.text("DELETE FROM public.asistencia_humanitaria_entregada WHERE id = :id"),
        {"id": id},
    )
    if getattr(result, "rowcount", 0) == 0:
        return jsonify({"error": "Asistencia humanitaria entregada no encontrada"}), 404

    db.session.commit()
    return jsonify({"mensaje": "Asistencia humanitaria entregada eliminada correctamente"})
