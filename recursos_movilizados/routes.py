from datetime import datetime, timezone

from flask import jsonify, request

from models import db
from recursos_movilizados import recursos_movilizados_bp


def _to_iso(value):
    return value.isoformat() if value else None


def _to_float(value):
    return float(value) if value is not None else None


def _payload_get(data, *keys, default=None):
    for key in keys:
        if key in data:
            return data[key]
    return default


def _serialize_recurso(row):
    return {
        "id": row.id,
        "recurso_inventario_id": row.recurso_inventario_id,
        "emergencia_id": row.emergencia_id,
        "provincia_destino_id": row.provincia_destino_id,
        "canton_destino_id": row.canton_destino_id,
        "parroquia_destino_id": row.parroquia_destino_id,
        "longitud_destino": _to_float(getattr(row, "longitud_destino", None)),
        "latitud_destino": _to_float(getattr(row, "latitud_destino", None)),
        "fecha_inicio": _to_iso(getattr(row, "fecha_inicio", None)),
        "fecha_fin": _to_iso(getattr(row, "fecha_fin", None)),
        "cantidad_asignada": getattr(row, "cantidad_asignada", None),
        "factor": getattr(row, "factor", None),
        "activo": getattr(row, "activo", None),
        "creador": getattr(row, "creador", None),
        "creacion": _to_iso(getattr(row, "creacion", None)),
        "modificador": getattr(row, "modificador", None),
        "modificacion": _to_iso(getattr(row, "modificacion", None)),
    }


@recursos_movilizados_bp.route("/api/recursos_movilizados", methods=["GET"])
def get_recursos_movilizados():
    """Listar recursos movilizados
    ---
    tags:
      - Recursos Movilizados
    responses:
      200:
        description: Lista de recursos movilizados
        schema:
          type: array
          items:
            type: object
            properties:
              id: {type: integer}
              recurso_inventario_id: {type: integer}
              emergencia_id: {type: integer}
              provincia_destino_id: {type: integer}
              canton_destino_id: {type: integer}
              parroquia_destino_id: {type: integer}
              longitud_destino: {type: number}
              latitud_destino: {type: number}
              fecha_inicio: {type: string}
              fecha_fin: {type: string}
              cantidad_asignada: {type: integer}
              factor: {type: integer}
              activo: {type: boolean}
              creador: {type: string}
              creacion: {type: string}
              modificador: {type: string}
              modificacion: {type: string}
    """
    result = db.session.execute(db.text("SELECT * FROM recursos_movilizados ORDER BY id ASC"))
    return jsonify([_serialize_recurso(row) for row in result])


@recursos_movilizados_bp.route(
    "/api/recursos_movilizados/emergencia/<int:emergencia_id>/usuario/<int:usuario_id>",
    methods=["GET"],
)
def get_recursos_movilizados_by_emergencia_by_usuario(emergencia_id, usuario_id):
    """Obtener recursos movilizados por emergencia y usuario
    ---
    tags:
      - Recursos Movilizados
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
        description: Lista de recursos movilizados filtrados por emergencia y usuario
        schema:
          type: array
          items:
            type: object
            properties:
              id: {type: integer}
              parroquia_nombre: {type: string}
              recurso_grupo: {type: string}
              recurso_tipo: {type: string}
              institucion: {type: string}
              fecha_inicio: {type: string}
              fecha_fin: {type: string}
              cantidad_asignada: {type: integer}
              factor: {type: integer}
              disponible: {type: integer}
              latitud_destino: {type: number}
              longitud_destino: {type: number}
    """
    query = db.text(
        """
        SELECT DISTINCT
            r.id,
            q.nombre AS parroquia_nombre,
            g.nombre AS recurso_grupo,
            t.nombre AS recurso_tipo,
            i.nombre AS institucion,
            r.fecha_inicio,
            r.fecha_fin,
            r.cantidad_asignada,
            r.factor,
            r.latitud_destino,
            r.longitud_destino,
            (
                COALESCE(inv.existencias, 0) - COALESCE(au.comprometido_en_uso, 0)
            ) AS disponible
        FROM recursos_movilizados r
        INNER JOIN public.usuario_perfil_coe_dpa_mesa x
            ON (r.provincia_destino_id = x.provincia_id OR x.provincia_id = 0)
           AND (r.canton_destino_id = x.canton_id OR x.canton_id = 0)
        INNER JOIN parroquias q
            ON (r.provincia_destino_id = q.provincia_id)
           AND (r.canton_destino_id = q.canton_id)
           AND (r.parroquia_destino_id = q.id)
        INNER JOIN recursos_inventario inv
            ON r.recurso_inventario_id = inv.id
        INNER JOIN recurso_tipos t
            ON inv.recurso_tipo_id = t.id
        INNER JOIN recurso_grupos g
            ON t.recurso_grupo_id = g.id
           AND g.recurso_categoria_id = 2
        INNER JOIN instituciones i
            ON inv.institucion_duena_id = i.id
        LEFT JOIN (
            SELECT
                rr.recurso_inventario_id,
                COALESCE(
                    SUM(
                        COALESCE(rr.cantidad_asignada, 0)
                        * CASE
                            WHEN LOWER(COALESCE(rr.factor::text, '1')) IN ('1', 'true', 't')
                                THEN 1
                            WHEN LOWER(COALESCE(rr.factor::text, '1')) IN ('-1', 'false', 'f')
                                THEN -1
                            ELSE 0
                          END
                    ),
                    0
                ) AS comprometido_en_uso
            FROM public.requerimiento_respuestas rr
            WHERE COALESCE(rr.activo, true) = true
            GROUP BY rr.recurso_inventario_id
        ) au
            ON au.recurso_inventario_id = inv.id
        WHERE r.emergencia_id = :emergencia_id
          AND x.usuario_id = :usuario_id
          AND COALESCE(r.activo, true) = true
        ORDER BY r.id ASC;
        """
    )
    result = db.session.execute(query, {"emergencia_id": emergencia_id, "usuario_id": usuario_id})
    recursos = []
    for row in result:
        recursos.append(
            {
                "id": row.id,
                "parroquia_nombre": row.parroquia_nombre,
                "recurso_grupo": row.recurso_grupo,
                "recurso_tipo": row.recurso_tipo,
                "institucion": row.institucion,
                "fecha_inicio": _to_iso(getattr(row, "fecha_inicio", None)),
                "fecha_fin": _to_iso(getattr(row, "fecha_fin", None)),
                "cantidad_asignada": row.cantidad_asignada,
                "factor": row.factor,
                "disponible": row.disponible,
                "latitud_destino": _to_float(getattr(row, "latitud_destino", None)),
                "longitud_destino": _to_float(getattr(row, "longitud_destino", None)),
            }
        )
    return jsonify(recursos)


@recursos_movilizados_bp.route("/api/recursos_movilizados", methods=["POST"])
def create_recurso_movilizado():
    """Crear nuevo recurso movilizado
    ---
    tags:
      - Recursos Movilizados
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
            - recurso_inventario_id
            - provincia_destino_id
            - canton_destino_id
            - parroquia_destino_id
          properties:
            recurso_inventario_id: {type: integer}
            emergencia_id: {type: integer}
            provincia_destino_id: {type: integer}
            canton_destino_id: {type: integer}
            parroquia_destino_id: {type: integer}
            longitud_destino: {type: number}
            latitud_destino: {type: number}
            fecha_inicio: {type: string}
            fecha_fin: {type: string}
            cantidad_asignada: {type: integer}
            factor: {type: integer}
            activo: {type: boolean}
            creador: {type: string}
            modificador: {type: string}
    responses:
      201:
        description: Recurso movilizado creado
        schema:
          type: object
          properties:
            id: {type: integer}
            recurso_inventario_id: {type: integer}
            emergencia_id: {type: integer}
            provincia_destino_id: {type: integer}
            canton_destino_id: {type: integer}
            parroquia_destino_id: {type: integer}
            longitud_destino: {type: number}
            latitud_destino: {type: number}
            fecha_inicio: {type: string}
            fecha_fin: {type: string}
            cantidad_asignada: {type: integer}
            factor: {type: integer}
            activo: {type: boolean}
            creador: {type: string}
            creacion: {type: string}
            modificador: {type: string}
            modificacion: {type: string}
    """
    data = request.get_json() or {}

    required_fields = [
        "emergencia_id",
        "recurso_inventario_id",
        "provincia_destino_id",
        "canton_destino_id",
        "parroquia_destino_id",
    ]
    payload = {
        "emergencia_id": data.get("emergencia_id"),
        "recurso_inventario_id": data.get("recurso_inventario_id"),
        "provincia_destino_id": data.get("provincia_destino_id"),
        "canton_destino_id": data.get("canton_destino_id"),
        "parroquia_destino_id": data.get("parroquia_destino_id"),
    }
    missing_fields = [field for field in required_fields if payload.get(field) is None]
    if missing_fields:
        return jsonify({"error": f"Campos requeridos faltantes: {', '.join(missing_fields)}"}), 400

    now = datetime.now(timezone.utc)
    creador = data.get("creador", "Sistema")

    query = db.text(
        """
        INSERT INTO recursos_movilizados (
            recurso_inventario_id,
            emergencia_id,
            provincia_destino_id,
            canton_destino_id,
            parroquia_destino_id,
            longitud_destino,
            latitud_destino,
            fecha_inicio,
            fecha_fin,
            cantidad_asignada,
            factor,
            activo,
            creador,
            creacion,
            modificador,
            modificacion
        )
        VALUES (
            :recurso_inventario_id,
            :emergencia_id,
            :provincia_destino_id,
            :canton_destino_id,
            :parroquia_destino_id,
            :longitud_destino,
            :latitud_destino,
            :fecha_inicio,
            :fecha_fin,
            :cantidad_asignada,
            :factor,
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
            **payload,
            "longitud_destino": data.get("longitud_destino", 0),
            "latitud_destino": data.get("latitud_destino", 0),
            "fecha_inicio": data.get("fecha_inicio"),
            "fecha_fin": data.get("fecha_fin"),
            "cantidad_asignada": data.get("cantidad_asignada", 0),
            "factor": data.get("factor", 0),
            "activo": data.get("activo", True),
            "creador": creador,
            "creacion": now,
            "modificador": data.get("modificador", creador),
            "modificacion": now,
        },
    )

    row = result.fetchone()
    if row is None:
        db.session.rollback()
        return jsonify({"error": "Failed to create recurso_movilizado"}), 500

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
    """Obtener recurso movilizado por ID
    ---
    tags:
      - Recursos Movilizados
    parameters:
      - name: id
        in: path
        type: integer
        required: true
    responses:
      200:
        description: Recurso movilizado
        schema:
          type: object
          properties:
            id: {type: integer}
            recurso_inventario_id: {type: integer}
            emergencia_id: {type: integer}
            provincia_destino_id: {type: integer}
            canton_destino_id: {type: integer}
            parroquia_destino_id: {type: integer}
            longitud_destino: {type: number}
            latitud_destino: {type: number}
            fecha_inicio: {type: string}
            fecha_fin: {type: string}
            cantidad_asignada: {type: integer}
            factor: {type: integer}
            activo: {type: boolean}
            creador: {type: string}
            creacion: {type: string}
            modificador: {type: string}
            modificacion: {type: string}
      404:
        description: No encontrado
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
    """Actualizar recurso movilizado
    ---
    tags:
      - Recursos Movilizados
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
            recurso_inventario_id: {type: integer}
            emergencia_id: {type: integer}
            provincia_destino_id: {type: integer}
            canton_destino_id: {type: integer}
            parroquia_destino_id: {type: integer}
            longitud_destino: {type: number}
            latitud_destino: {type: number}
            fecha_inicio: {type: string}
            fecha_fin: {type: string}
            cantidad_asignada: {type: integer}
            factor: {type: integer}
            activo: {type: boolean}
            modificador: {type: string}
    responses:
      200:
        description: Recurso movilizado actualizado
        schema:
          type: object
          properties:
            id: {type: integer}
            recurso_inventario_id: {type: integer}
            emergencia_id: {type: integer}
            provincia_destino_id: {type: integer}
            canton_destino_id: {type: integer}
            parroquia_destino_id: {type: integer}
            longitud_destino: {type: number}
            latitud_destino: {type: number}
            fecha_inicio: {type: string}
            fecha_fin: {type: string}
            cantidad_asignada: {type: integer}
            factor: {type: integer}
            activo: {type: boolean}
            creador: {type: string}
            creacion: {type: string}
            modificador: {type: string}
            modificacion: {type: string}
      404:
        description: No encontrado
    """
    data = request.get_json() or {}
    now = datetime.now(timezone.utc)

    updatable_fields = [
        "recurso_inventario_id",
        "emergencia_id",
        "provincia_destino_id",
        "canton_destino_id",
        "parroquia_destino_id",
        "longitud_destino",
        "latitud_destino",
        "fecha_inicio",
        "fecha_fin",
        "cantidad_asignada",
        "factor",
        "activo",
    ]

    params = {"id": id, "modificador": data.get("modificador", "Sistema"), "modificacion": now}
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
    """Eliminar recurso movilizado
    ---
    tags:
      - Recursos Movilizados
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
        db.text("DELETE FROM recursos_movilizados WHERE id = :id"),
        {"id": id},
    )
    if getattr(result, "rowcount", 0) == 0:
        return jsonify({"error": "Recurso movilizado no encontrado"}), 404

    db.session.commit()
    return jsonify({"mensaje": "Recurso movilizado eliminado correctamente"})
