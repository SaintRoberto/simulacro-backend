from datetime import datetime, timezone

from flask import jsonify, request

from models import db
from perfil_coe_mesa_menu_opcion import perfil_coe_mesa_menu_opcion_bp


def _to_bool(value):
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        value_norm = value.strip().lower()
        if value_norm in ("true", "1", "t", "si"):
            return True
        if value_norm in ("false", "0", "f", "no"):
            return False
    return None


def _row_to_dict(row):
    return {
        "id": row.id,
        "perfil_id": row.perfil_id,
        "perfil_nombre": row.perfil_nombre,
        "coe_id": row.coe_id,
        "coe_nombre": row.coe_nombre,
        "mesa_id": row.mesa_id,
        "mesa_nombre": row.mesa_nombre,
        "menu_id": row.menu_id,
        "menu_nombre": row.menu_nombre,
        "opcion_id": row.opcion_id,
        "opcion_nombre": row.opcion_nombre,
        "activo": row.activo,
        "creador": row.creador,
        "creacion": row.creacion.isoformat() if row.creacion else None,
        "modificador": row.modificador,
        "modificacion": row.modificacion.isoformat() if row.modificacion else None,
    }


def _get_item_with_details_by_id(item_id):
    query = db.text(
        """
        SELECT
            x.id,
            x.perfil_id,
            p.nombre AS perfil_nombre,
            x.coe_id,
            c.nombre AS coe_nombre,
            x.mesa_id,
            m.nombre AS mesa_nombre,
            x.menu_id,
            mn.nombre AS menu_nombre,
            x.opcion_id,
            o.nombre AS opcion_nombre,
            x.activo,
            x.creador,
            x.creacion,
            x.modificador,
            x.modificacion
        FROM perfil_coe_mesa_menu_opcion x
        INNER JOIN perfiles p ON p.id = x.perfil_id
        INNER JOIN coes c ON c.id = x.coe_id
        INNER JOIN mesas m ON m.id = x.mesa_id
        INNER JOIN menus mn ON mn.id = x.menu_id
        INNER JOIN opciones o ON o.id = x.opcion_id
        WHERE x.id = :id
        """
    )
    return db.session.execute(query, {"id": item_id}).fetchone()


def _validate_scope(perfil_id, coe_id, mesa_id):
    perfil_ok = db.session.execute(
        db.text("SELECT 1 FROM perfiles WHERE id = :id"),
        {"id": perfil_id},
    ).fetchone()
    if perfil_ok is None:
        return "El perfil_id no existe"

    coe_ok = db.session.execute(
        db.text("SELECT 1 FROM coes WHERE id = :id"),
        {"id": coe_id},
    ).fetchone()
    if coe_ok is None:
        return "El coe_id no existe"

    mesa_ok = db.session.execute(
        db.text("SELECT 1 FROM mesas WHERE id = :mesa_id AND coe_id = :coe_id"),
        {"mesa_id": mesa_id, "coe_id": coe_id},
    ).fetchone()
    if mesa_ok is None:
        return "La mesa no existe para el coe_id indicado"

    return None


def _validate_coe_mesa(coe_id, mesa_id):
    coe_ok = db.session.execute(
        db.text("SELECT 1 FROM coes WHERE id = :id"),
        {"id": coe_id},
    ).fetchone()
    if coe_ok is None:
        return "El coe_id no existe"

    mesa_ok = db.session.execute(
        db.text("SELECT 1 FROM mesas WHERE id = :mesa_id AND coe_id = :coe_id"),
        {"mesa_id": mesa_id, "coe_id": coe_id},
    ).fetchone()
    if mesa_ok is None:
        return "La mesa no existe para el coe_id indicado"

    return None


def _validate_perfil(perfil_id):
    perfil_ok = db.session.execute(
        db.text("SELECT 1 FROM perfiles WHERE id = :id"),
        {"id": perfil_id},
    ).fetchone()
    if perfil_ok is None:
        return "El perfil_id no existe"
    return None


def _validate_menu_opcion(menu_id, opcion_id):
    menu_ok = db.session.execute(
        db.text("SELECT 1 FROM menus WHERE id = :id"),
        {"id": menu_id},
    ).fetchone()
    if menu_ok is None:
        return "El menu_id no existe"

    opcion_ok = db.session.execute(
        db.text("SELECT 1 FROM opciones WHERE id = :id"),
        {"id": opcion_id},
    ).fetchone()
    if opcion_ok is None:
        return "El opcion_id no existe"

    return None


def _validate_unique_combination(perfil_id, coe_id, mesa_id, menu_id, opcion_id, current_id=None):
    query = """
        SELECT id
        FROM perfil_coe_mesa_menu_opcion
        WHERE perfil_id = :perfil_id
          AND coe_id = :coe_id
          AND mesa_id = :mesa_id
          AND menu_id = :menu_id
          AND opcion_id = :opcion_id
    """
    params = {
        "perfil_id": perfil_id,
        "coe_id": coe_id,
        "mesa_id": mesa_id,
        "menu_id": menu_id,
        "opcion_id": opcion_id,
    }

    if current_id is not None:
        query += " AND id <> :current_id"
        params["current_id"] = current_id

    existing = db.session.execute(db.text(query), params).fetchone()
    if existing is not None:
        return "Ya existe un permiso para esa combinacion de perfil/coe/mesa/menu/opcion"
    return None


@perfil_coe_mesa_menu_opcion_bp.route("/api/perfil-coe-mesa-menu-opcion", methods=["GET"])
def get_perfil_coe_mesa_menu_opcion():
    """Lista permisos perfil/coe/mesa/menu/opcion.

    Query params:
        activo (bool, opcional): filtra por estado activo.

    Returns:
        200: listado de permisos con nombres descriptivos.
        400: valor invalido para el parametro activo.
    """
    activo_param = request.args.get("activo")
    where_clause = ""
    params = {}

    if activo_param is not None:
        activo_value = _to_bool(activo_param)
        if activo_value is None:
            return jsonify({"error": 'El parametro "activo" debe ser true o false'}), 400
        where_clause = "WHERE x.activo = :activo"
        params["activo"] = activo_value

    query = db.text(
        f"""
        SELECT
            x.id,
            x.perfil_id,
            p.nombre AS perfil_nombre,
            x.coe_id,
            c.nombre AS coe_nombre,
            x.mesa_id,
            m.nombre AS mesa_nombre,
            x.menu_id,
            mn.nombre AS menu_nombre,
            x.opcion_id,
            o.nombre AS opcion_nombre,
            x.activo,
            x.creador,
            x.creacion,
            x.modificador,
            x.modificacion
        FROM perfil_coe_mesa_menu_opcion x
        INNER JOIN perfiles p ON p.id = x.perfil_id
        INNER JOIN coes c ON c.id = x.coe_id
        INNER JOIN mesas m ON m.id = x.mesa_id
        INNER JOIN menus mn ON mn.id = x.menu_id
        INNER JOIN opciones o ON o.id = x.opcion_id
        {where_clause}
        ORDER BY x.perfil_id, x.coe_id, x.mesa_id, x.menu_id, x.opcion_id
        """
    )
    rows = db.session.execute(query, params)
    return jsonify([_row_to_dict(row) for row in rows])


@perfil_coe_mesa_menu_opcion_bp.route("/api/perfil-coe-mesa-menu-opcion/<int:item_id>", methods=["GET"])
def get_perfil_coe_mesa_menu_opcion_by_id(item_id):
    """Obtiene un permiso por su identificador.

    Args:
        item_id (int): id del permiso.

    Returns:
        200: permiso encontrado.
        404: permiso no existe.
    """
    row = _get_item_with_details_by_id(item_id)
    if row is None:
        return jsonify({"error": "Permiso no encontrado"}), 404
    return jsonify(_row_to_dict(row))


@perfil_coe_mesa_menu_opcion_bp.route(
    "/api/perfil-coe-mesa-menu-opcion/perfil/<int:perfil_id>/coe/<int:coe_id>/mesa/<int:mesa_id>",
    methods=["GET"],
)
def get_permisos_by_scope(perfil_id, coe_id, mesa_id):
    """Lista permisos por ambito perfil/coe/mesa.

    Args:
        perfil_id (int): id del perfil.
        coe_id (int): id del COE.
        mesa_id (int): id de la mesa.

    Query params:
        activo (bool, opcional): filtra por estado activo.

    Returns:
        200: permisos del ambito solicitado.
        400: ambito invalido o parametro activo invalido.
    """
    scope_error = _validate_scope(perfil_id, coe_id, mesa_id)
    if scope_error:
        return jsonify({"error": scope_error}), 400

    activo_param = request.args.get("activo")
    where_activo = ""
    params = {"perfil_id": perfil_id, "coe_id": coe_id, "mesa_id": mesa_id}

    if activo_param is not None:
        activo_value = _to_bool(activo_param)
        if activo_value is None:
            return jsonify({"error": 'El parametro "activo" debe ser true o false'}), 400
        where_activo = "AND x.activo = :activo"
        params["activo"] = activo_value

    query = db.text(
        f"""
        SELECT
            x.id,
            x.perfil_id,
            p.nombre AS perfil_nombre,
            x.coe_id,
            c.nombre AS coe_nombre,
            x.mesa_id,
            m.nombre AS mesa_nombre,
            x.menu_id,
            mn.nombre AS menu_nombre,
            x.opcion_id,
            o.nombre AS opcion_nombre,
            x.activo,
            x.creador,
            x.creacion,
            x.modificador,
            x.modificacion
        FROM perfil_coe_mesa_menu_opcion x
        INNER JOIN perfiles p ON p.id = x.perfil_id
        INNER JOIN coes c ON c.id = x.coe_id
        INNER JOIN mesas m ON m.id = x.mesa_id
        INNER JOIN menus mn ON mn.id = x.menu_id
        INNER JOIN opciones o ON o.id = x.opcion_id
        WHERE x.perfil_id = :perfil_id
          AND x.coe_id = :coe_id
          AND x.mesa_id = :mesa_id
          {where_activo}
        ORDER BY x.menu_id, x.opcion_id
        """
    )

    rows = db.session.execute(query, params)
    return jsonify([_row_to_dict(row) for row in rows])


@perfil_coe_mesa_menu_opcion_bp.route("/api/perfil-coe-mesa-menu-opcion", methods=["POST"])
def create_perfil_coe_mesa_menu_opcion():
    """Crea un permiso perfil/coe/mesa/menu/opcion.

    Body:
        perfil_id (int), coe_id (int), mesa_id (int), menu_id (int), opcion_id (int).
        activo (bool, opcional), creador (str, opcional), modificador (str, opcional).

    Returns:
        201: permiso creado.
        400: datos faltantes o referencias invalidas.
        409: combinacion ya existente.
        500: error al persistir.
    """
    data = request.get_json() or {}
    required_fields = ["perfil_id", "coe_id", "mesa_id", "menu_id", "opcion_id"]
    missing = [field for field in required_fields if field not in data]
    if missing:
        return jsonify({"error": f"Campos requeridos faltantes: {', '.join(missing)}"}), 400

    perfil_id = data["perfil_id"]
    coe_id = data["coe_id"]
    mesa_id = data["mesa_id"]
    menu_id = data["menu_id"]
    opcion_id = data["opcion_id"]

    scope_error = _validate_scope(perfil_id, coe_id, mesa_id)
    if scope_error:
        return jsonify({"error": scope_error}), 400

    menu_opcion_error = _validate_menu_opcion(menu_id, opcion_id)
    if menu_opcion_error:
        return jsonify({"error": menu_opcion_error}), 400

    unique_error = _validate_unique_combination(perfil_id, coe_id, mesa_id, menu_id, opcion_id)
    if unique_error:
        return jsonify({"error": unique_error}), 409

    now = datetime.now(timezone.utc)
    creador = data.get("creador", "Sistema")
    modificador = data.get("modificador", creador)
    activo = data.get("activo", True)

    result = db.session.execute(
        db.text(
            """
            INSERT INTO perfil_coe_mesa_menu_opcion (
                perfil_id, coe_id, mesa_id, menu_id, opcion_id, activo,
                creador, creacion, modificador, modificacion
            )
            VALUES (
                :perfil_id, :coe_id, :mesa_id, :menu_id, :opcion_id, :activo,
                :creador, :creacion, :modificador, :modificacion
            )
            RETURNING id
            """
        ),
        {
            "perfil_id": perfil_id,
            "coe_id": coe_id,
            "mesa_id": mesa_id,
            "menu_id": menu_id,
            "opcion_id": opcion_id,
            "activo": activo,
            "creador": creador,
            "creacion": now,
            "modificador": modificador,
            "modificacion": now,
        },
    )

    row = result.fetchone()
    if row is None:
        db.session.rollback()
        return jsonify({"error": "No se pudo crear el permiso"}), 500

    db.session.commit()
    created = _get_item_with_details_by_id(row[0])
    if created is None:
        return jsonify({"error": "Permiso creado pero no encontrado"}), 500

    return jsonify(_row_to_dict(created)), 201


@perfil_coe_mesa_menu_opcion_bp.route("/api/perfil-coe-mesa-menu-opcion/<int:item_id>", methods=["PUT"])
def update_perfil_coe_mesa_menu_opcion(item_id):
    """Actualiza un permiso existente.

    Args:
        item_id (int): id del permiso.

    Body:
        Campos opcionales para actualizar: perfil_id, coe_id, mesa_id, menu_id, opcion_id,
        activo, modificador.

    Returns:
        200: permiso actualizado.
        400: datos invalidos.
        404: permiso no encontrado.
        409: combinacion duplicada.
    """
    data = request.get_json() or {}
    current = db.session.execute(
        db.text("SELECT * FROM perfil_coe_mesa_menu_opcion WHERE id = :id"),
        {"id": item_id},
    ).fetchone()
    if current is None:
        return jsonify({"error": "Permiso no encontrado"}), 404

    perfil_id = data.get("perfil_id", current.perfil_id)
    coe_id = data.get("coe_id", current.coe_id)
    mesa_id = data.get("mesa_id", current.mesa_id)
    menu_id = data.get("menu_id", current.menu_id)
    opcion_id = data.get("opcion_id", current.opcion_id)

    scope_error = _validate_scope(perfil_id, coe_id, mesa_id)
    if scope_error:
        return jsonify({"error": scope_error}), 400

    menu_opcion_error = _validate_menu_opcion(menu_id, opcion_id)
    if menu_opcion_error:
        return jsonify({"error": menu_opcion_error}), 400

    unique_error = _validate_unique_combination(
        perfil_id, coe_id, mesa_id, menu_id, opcion_id, current_id=item_id
    )
    if unique_error:
        return jsonify({"error": unique_error}), 409

    now = datetime.now(timezone.utc)
    result = db.session.execute(
        db.text(
            """
            UPDATE perfil_coe_mesa_menu_opcion
            SET
                perfil_id = :perfil_id,
                coe_id = :coe_id,
                mesa_id = :mesa_id,
                menu_id = :menu_id,
                opcion_id = :opcion_id,
                activo = :activo,
                modificador = :modificador,
                modificacion = :modificacion
            WHERE id = :id
            """
        ),
        {
            "id": item_id,
            "perfil_id": perfil_id,
            "coe_id": coe_id,
            "mesa_id": mesa_id,
            "menu_id": menu_id,
            "opcion_id": opcion_id,
            "activo": data.get("activo", current.activo),
            "modificador": data.get("modificador", "Sistema"),
            "modificacion": now,
        },
    )

    if getattr(result, "rowcount", 0) == 0:
        db.session.rollback()
        return jsonify({"error": "Permiso no encontrado"}), 404

    db.session.commit()
    updated = _get_item_with_details_by_id(item_id)
    if updated is None:
        return jsonify({"error": "Permiso no encontrado despues de actualizar"}), 404

    return jsonify(_row_to_dict(updated))


@perfil_coe_mesa_menu_opcion_bp.route("/api/perfil-coe-mesa-menu-opcion/<int:item_id>", methods=["DELETE"])
def delete_perfil_coe_mesa_menu_opcion(item_id):
    """Elimina un permiso por id.

    Args:
        item_id (int): id del permiso.

    Returns:
        200: permiso eliminado.
        404: permiso no encontrado.
    """
    result = db.session.execute(
        db.text("DELETE FROM perfil_coe_mesa_menu_opcion WHERE id = :id"),
        {"id": item_id},
    )

    if getattr(result, "rowcount", 0) == 0:
        return jsonify({"error": "Permiso no encontrado"}), 404

    db.session.commit()
    return jsonify({"mensaje": "Permiso eliminado correctamente"})


@perfil_coe_mesa_menu_opcion_bp.route(
    "/api/perfil-coe-mesa-menu-opcion/perfil/<int:perfil_id>/coe/<int:coe_id>/mesa/<int:mesa_id>/sincronizar",
    methods=["PUT"],
)
def sync_permisos_by_scope(perfil_id, coe_id, mesa_id):
    """Sincroniza permisos de un perfil en un COE y mesa.

    Reglas:
        - Inserta permisos nuevos.
        - Actualiza permisos existentes.
        - Desactiva permisos no enviados en la lista de entrada.

    Args:
        perfil_id (int): id del perfil.
        coe_id (int): id del COE.
        mesa_id (int): id de la mesa.

    Body:
        permisos (list): lista de objetos con menu_id, opcion_id y activo opcional.

    Returns:
        200: permisos sincronizados y estado final del ambito.
        400: validaciones de entrada.
        500: error de base de datos.
    """
    data = request.get_json() or {}
    permisos = data.get("permisos")
    if not isinstance(permisos, list):
        return jsonify({"error": 'El campo "permisos" debe ser una lista'}), 400

    scope_error = _validate_scope(perfil_id, coe_id, mesa_id)
    if scope_error:
        return jsonify({"error": scope_error}), 400

    normalized = []
    seen_pairs = set()
    for index, permiso in enumerate(permisos):
        if not isinstance(permiso, dict):
            return jsonify({"error": f"El permiso en posicion {index} debe ser un objeto"}), 400
        if "menu_id" not in permiso or "opcion_id" not in permiso:
            return jsonify({"error": f"Falta menu_id u opcion_id en la posicion {index}"}), 400

        menu_id = permiso["menu_id"]
        opcion_id = permiso["opcion_id"]
        pair = (menu_id, opcion_id)
        if pair in seen_pairs:
            return jsonify(
                {"error": f"Combinacion duplicada menu_id/opcion_id en la posicion {index}"}
            ), 400
        seen_pairs.add(pair)

        menu_opcion_error = _validate_menu_opcion(menu_id, opcion_id)
        if menu_opcion_error:
            return jsonify({"error": f"{menu_opcion_error} en la posicion {index}"}), 400

        activo_value = permiso.get("activo", True)
        normalized.append(
            {
                "menu_id": menu_id,
                "opcion_id": opcion_id,
                "activo": bool(activo_value),
            }
        )

    now = datetime.now(timezone.utc)
    creador = data.get("creador", "Sistema")
    modificador = data.get("modificador", creador)

    existing_rows = db.session.execute(
        db.text(
            """
            SELECT id, menu_id, opcion_id
            FROM perfil_coe_mesa_menu_opcion
            WHERE perfil_id = :perfil_id AND coe_id = :coe_id AND mesa_id = :mesa_id
            """
        ),
        {"perfil_id": perfil_id, "coe_id": coe_id, "mesa_id": mesa_id},
    ).fetchall()

    existing_by_pair = {(row.menu_id, row.opcion_id): row.id for row in existing_rows}
    incoming_pairs = {(item["menu_id"], item["opcion_id"]) for item in normalized}

    try:
        for permiso in normalized:
            pair = (permiso["menu_id"], permiso["opcion_id"])
            existing_id = existing_by_pair.get(pair)
            if existing_id is not None:
                db.session.execute(
                    db.text(
                        """
                        UPDATE perfil_coe_mesa_menu_opcion
                        SET activo = :activo,
                            modificador = :modificador,
                            modificacion = :modificacion
                        WHERE id = :id
                        """
                    ),
                    {
                        "id": existing_id,
                        "activo": permiso["activo"],
                        "modificador": modificador,
                        "modificacion": now,
                    },
                )
            else:
                db.session.execute(
                    db.text(
                        """
                        INSERT INTO perfil_coe_mesa_menu_opcion (
                            perfil_id, coe_id, mesa_id, menu_id, opcion_id, activo,
                            creador, creacion, modificador, modificacion
                        )
                        VALUES (
                            :perfil_id, :coe_id, :mesa_id, :menu_id, :opcion_id, :activo,
                            :creador, :creacion, :modificador, :modificacion
                        )
                        """
                    ),
                    {
                        "perfil_id": perfil_id,
                        "coe_id": coe_id,
                        "mesa_id": mesa_id,
                        "menu_id": permiso["menu_id"],
                        "opcion_id": permiso["opcion_id"],
                        "activo": permiso["activo"],
                        "creador": creador,
                        "creacion": now,
                        "modificador": modificador,
                        "modificacion": now,
                    },
                )

        for row in existing_rows:
            pair = (row.menu_id, row.opcion_id)
            if pair not in incoming_pairs:
                db.session.execute(
                    db.text(
                        """
                        UPDATE perfil_coe_mesa_menu_opcion
                        SET activo = false,
                            modificador = :modificador,
                            modificacion = :modificacion
                        WHERE id = :id
                        """
                    ),
                    {
                        "id": row.id,
                        "modificador": modificador,
                        "modificacion": now,
                    },
                )

        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "Error de base de datos", "details": str(e)}), 500

    result_rows = db.session.execute(
        db.text(
            """
            SELECT
                x.id,
                x.perfil_id,
                p.nombre AS perfil_nombre,
                x.coe_id,
                c.nombre AS coe_nombre,
                x.mesa_id,
                m.nombre AS mesa_nombre,
                x.menu_id,
                mn.nombre AS menu_nombre,
                x.opcion_id,
                o.nombre AS opcion_nombre,
                x.activo,
                x.creador,
                x.creacion,
                x.modificador,
                x.modificacion
            FROM perfil_coe_mesa_menu_opcion x
            INNER JOIN perfiles p ON p.id = x.perfil_id
            INNER JOIN coes c ON c.id = x.coe_id
            INNER JOIN mesas m ON m.id = x.mesa_id
            INNER JOIN menus mn ON mn.id = x.menu_id
            INNER JOIN opciones o ON o.id = x.opcion_id
            WHERE x.perfil_id = :perfil_id
              AND x.coe_id = :coe_id
              AND x.mesa_id = :mesa_id
            ORDER BY x.menu_id, x.opcion_id
            """
        ),
        {"perfil_id": perfil_id, "coe_id": coe_id, "mesa_id": mesa_id},
    )

    return jsonify([_row_to_dict(row) for row in result_rows])


@perfil_coe_mesa_menu_opcion_bp.route(
    "/api/perfil-coe-mesa-menu-opcion/matriz/coe/<int:coe_id>/mesa/<int:mesa_id>",
    methods=["GET"],
)
def get_permisos_matriz(coe_id, mesa_id):
    """Obtiene la matriz de permisos por COE y mesa.

    Args:
        coe_id (int): id del COE.
        mesa_id (int): id de la mesa.

    Query params:
        solo_activos_perfil (bool, opcional, default=true): incluye solo perfiles activos.

    Returns:
        200: estructura de matriz (perfiles, opciones, grupos y filas).
        400: coe/mesa invalidos o parametro incorrecto.
    """
    scope_error = _validate_coe_mesa(coe_id, mesa_id)
    if scope_error:
        return jsonify({"error": scope_error}), 400

    solo_activos_param = request.args.get("solo_activos_perfil", "true")
    solo_activos = _to_bool(solo_activos_param)
    if solo_activos is None:
        return jsonify({"error": 'El parametro "solo_activos_perfil" debe ser true o false'}), 400

    perfiles_query = "SELECT id, nombre, activo FROM perfiles"
    if solo_activos:
        perfiles_query += " WHERE activo = true"
    perfiles_query += " ORDER BY nombre"
    perfiles_rows = db.session.execute(db.text(perfiles_query)).fetchall()

    perfiles = [
        {"perfil_id": row.id, "perfil_nombre": row.nombre, "perfil_activo": row.activo}
        for row in perfiles_rows
    ]
    perfil_ids = [row.id for row in perfiles_rows]

    opciones_rows = db.session.execute(
        db.text(
            """
            SELECT id, nombre, abreviatura
            FROM opciones
            WHERE activo = true
            ORDER BY id
            """
        )
    ).fetchall()
    opciones = [
        {
            "opcion_id": row.id,
            "opcion_nombre": row.nombre,
            "opcion_abreviatura": row.abreviatura if row.abreviatura else row.nombre,
        }
        for row in opciones_rows
    ]

    menus_rows = db.session.execute(
        db.text(
            """
            SELECT id, padre_id, orden, nombre, abreviatura
            FROM menus
            WHERE activo = true
            ORDER BY padre_id, orden, nombre
            """
        )
    ).fetchall()

    menu_by_id = {row.id: row for row in menus_rows}
    grupos_menus = [row for row in menus_rows if row.orden == 0]
    hijos = [row for row in menus_rows if row.orden != 0]

    hijos_by_padre = {}
    for row in hijos:
        hijos_by_padre.setdefault(row.padre_id, []).append(row)
    for children in hijos_by_padre.values():
        children.sort(key=lambda x: (x.orden, x.nombre))

    permisos_rows = db.session.execute(
        db.text(
            """
            SELECT id, perfil_id, menu_id, opcion_id, activo
            FROM perfil_coe_mesa_menu_opcion
            WHERE coe_id = :coe_id AND mesa_id = :mesa_id
            """
        ),
        {"coe_id": coe_id, "mesa_id": mesa_id},
    ).fetchall()

    permisos_map = {}
    for row in permisos_rows:
        permisos_map[(row.perfil_id, row.menu_id, row.opcion_id)] = {
            "id": row.id,
            "activo": bool(row.activo),
        }

    grupos = []
    included_menu_ids = set()

    for grupo in sorted(grupos_menus, key=lambda x: (x.nombre, x.id)):
        children = hijos_by_padre.get(grupo.id, [])
        if not children:
            continue

        items = []
        for menu_item in children:
            included_menu_ids.add(menu_item.id)
            celdas = []
            for perfil_id in perfil_ids:
                botones = []
                for opcion in opciones:
                    key = (perfil_id, menu_item.id, opcion["opcion_id"])
                    permiso = permisos_map.get(key)
                    botones.append(
                        {
                            "opcion_id": opcion["opcion_id"],
                            "opcion_abreviatura": opcion["opcion_abreviatura"],
                            "opcion_nombre": opcion["opcion_nombre"],
                            "permiso_id": permiso["id"] if permiso else None,
                            "activo": permiso["activo"] if permiso else False,
                        }
                    )
                celdas.append({"perfil_id": perfil_id, "botones": botones})

            items.append(
                {
                    "menu_id": menu_item.id,
                    "menu_nombre": menu_item.nombre,
                    "menu_abreviatura": menu_item.abreviatura,
                    "menu_orden": menu_item.orden,
                    "celdas": celdas,
                }
            )

        grupos.append(
            {
                "menu_grupo_id": grupo.id,
                "menu_grupo_nombre": grupo.nombre,
                "menu_grupo_abreviatura": grupo.abreviatura,
                "menu_grupo_orden": grupo.orden,
                "items": items,
            }
        )

    # Menus sin grupo (padre_id sin cabecera orden 0 o padre_id=0)
    items_sin_grupo = []
    for menu_item in hijos:
        if menu_item.id in included_menu_ids:
            continue
        padre = menu_by_id.get(menu_item.padre_id)
        if padre is not None and padre.orden == 0:
            continue

        celdas = []
        for perfil_id in perfil_ids:
            botones = []
            for opcion in opciones:
                key = (perfil_id, menu_item.id, opcion["opcion_id"])
                permiso = permisos_map.get(key)
                botones.append(
                    {
                        "opcion_id": opcion["opcion_id"],
                        "opcion_abreviatura": opcion["opcion_abreviatura"],
                        "opcion_nombre": opcion["opcion_nombre"],
                        "permiso_id": permiso["id"] if permiso else None,
                        "activo": permiso["activo"] if permiso else False,
                    }
                )
            celdas.append({"perfil_id": perfil_id, "botones": botones})

        items_sin_grupo.append(
            {
                "menu_id": menu_item.id,
                "menu_nombre": menu_item.nombre,
                "menu_abreviatura": menu_item.abreviatura,
                "menu_orden": menu_item.orden,
                "celdas": celdas,
            }
        )

    if items_sin_grupo:
        items_sin_grupo.sort(key=lambda x: (x["menu_orden"], x["menu_nombre"]))
        grupos.append(
            {
                "menu_grupo_id": 0,
                "menu_grupo_nombre": "SIN GRUPO",
                "menu_grupo_abreviatura": "SG",
                "menu_grupo_orden": 9999,
                "items": items_sin_grupo,
            }
        )

    # Salida plana para compatibilidad con implementaciones previas
    filas = []
    for grupo in grupos:
        for item in grupo["items"]:
            for opcion in opciones:
                celdas = []
                for celda in item["celdas"]:
                    boton = next(
                        (b for b in celda["botones"] if b["opcion_id"] == opcion["opcion_id"]),
                        None,
                    )
                    celdas.append(
                        {
                            "perfil_id": celda["perfil_id"],
                            "permiso_id": boton["permiso_id"] if boton else None,
                            "activo": boton["activo"] if boton else False,
                        }
                    )
                filas.append(
                    {
                        "menu_grupo_id": grupo["menu_grupo_id"],
                        "menu_grupo_nombre": grupo["menu_grupo_nombre"],
                        "menu_id": item["menu_id"],
                        "menu_nombre": item["menu_nombre"],
                        "menu_orden": item["menu_orden"],
                        "opcion_id": opcion["opcion_id"],
                        "opcion_nombre": opcion["opcion_nombre"],
                        "opcion_abreviatura": opcion["opcion_abreviatura"],
                        "celdas": celdas,
                    }
                )

    return jsonify(
        {
            "coe_id": coe_id,
            "mesa_id": mesa_id,
            "perfiles": perfiles,
            "opciones": opciones,
            "grupos": grupos,
            "filas": filas,
        }
    )


@perfil_coe_mesa_menu_opcion_bp.route(
    "/api/perfil-coe-mesa-menu-opcion/matriz/coe/<int:coe_id>/mesa/<int:mesa_id>",
    methods=["PUT"],
)
def upsert_permisos_matriz(coe_id, mesa_id):
    """Crea o actualiza celdas de la matriz de permisos.

    Args:
        coe_id (int): id del COE.
        mesa_id (int): id de la mesa.

    Body:
        celdas (list): elementos con perfil_id, menu_id, opcion_id y activo.
        reemplazar (bool, opcional): si es true, desactiva celdas omitidas para perfiles
            involucrados.
        creador (str, opcional), modificador (str, opcional).

    Returns:
        200: resumen de actualizacion de matriz.
        400: datos invalidos.
        500: error de base de datos.
    """
    data = request.get_json() or {}
    celdas = data.get("celdas")
    reemplazar = bool(data.get("reemplazar", False))
    modificador = data.get("modificador", "Sistema")
    creador = data.get("creador", modificador)

    if not isinstance(celdas, list):
        return jsonify({"error": 'El campo "celdas" debe ser una lista'}), 400

    scope_error = _validate_coe_mesa(coe_id, mesa_id)
    if scope_error:
        return jsonify({"error": scope_error}), 400

    normalized = []
    seen = set()
    perfiles_involucrados = set()
    for index, celda in enumerate(celdas):
        if not isinstance(celda, dict):
            return jsonify({"error": f"La celda en posicion {index} debe ser un objeto"}), 400
        required = ["perfil_id", "menu_id", "opcion_id", "activo"]
        missing = [field for field in required if field not in celda]
        if missing:
            return jsonify({"error": f"Faltan campos {', '.join(missing)} en la posicion {index}"}), 400

        perfil_id = celda["perfil_id"]
        menu_id = celda["menu_id"]
        opcion_id = celda["opcion_id"]
        activo = bool(celda["activo"])
        key = (perfil_id, menu_id, opcion_id)
        if key in seen:
            return jsonify({"error": f"Celda duplicada en posicion {index}"}), 400
        seen.add(key)

        perfil_error = _validate_perfil(perfil_id)
        if perfil_error:
            return jsonify({"error": f"{perfil_error} en la posicion {index}"}), 400
        menu_opcion_error = _validate_menu_opcion(menu_id, opcion_id)
        if menu_opcion_error:
            return jsonify({"error": f"{menu_opcion_error} en la posicion {index}"}), 400

        perfiles_involucrados.add(perfil_id)
        normalized.append(
            {
                "perfil_id": perfil_id,
                "menu_id": menu_id,
                "opcion_id": opcion_id,
                "activo": activo,
            }
        )

    now = datetime.now(timezone.utc)

    existing_rows = db.session.execute(
        db.text(
            """
            SELECT id, perfil_id, menu_id, opcion_id
            FROM perfil_coe_mesa_menu_opcion
            WHERE coe_id = :coe_id AND mesa_id = :mesa_id
            """
        ),
        {"coe_id": coe_id, "mesa_id": mesa_id},
    ).fetchall()
    existing_by_key = {(r.perfil_id, r.menu_id, r.opcion_id): r.id for r in existing_rows}
    incoming_keys = {
        (item["perfil_id"], item["menu_id"], item["opcion_id"])
        for item in normalized
    }

    try:
        for celda in normalized:
            key = (celda["perfil_id"], celda["menu_id"], celda["opcion_id"])
            existing_id = existing_by_key.get(key)
            if existing_id is None:
                db.session.execute(
                    db.text(
                        """
                        INSERT INTO perfil_coe_mesa_menu_opcion (
                            perfil_id, coe_id, mesa_id, menu_id, opcion_id, activo,
                            creador, creacion, modificador, modificacion
                        )
                        VALUES (
                            :perfil_id, :coe_id, :mesa_id, :menu_id, :opcion_id, :activo,
                            :creador, :creacion, :modificador, :modificacion
                        )
                        """
                    ),
                    {
                        "perfil_id": celda["perfil_id"],
                        "coe_id": coe_id,
                        "mesa_id": mesa_id,
                        "menu_id": celda["menu_id"],
                        "opcion_id": celda["opcion_id"],
                        "activo": celda["activo"],
                        "creador": creador,
                        "creacion": now,
                        "modificador": modificador,
                        "modificacion": now,
                    },
                )
            else:
                db.session.execute(
                    db.text(
                        """
                        UPDATE perfil_coe_mesa_menu_opcion
                        SET activo = :activo,
                            modificador = :modificador,
                            modificacion = :modificacion
                        WHERE id = :id
                        """
                    ),
                    {
                        "id": existing_id,
                        "activo": celda["activo"],
                        "modificador": modificador,
                        "modificacion": now,
                    },
                )

        if reemplazar and perfiles_involucrados:
            for row in existing_rows:
                key = (row.perfil_id, row.menu_id, row.opcion_id)
                if row.perfil_id in perfiles_involucrados and key not in incoming_keys:
                    db.session.execute(
                        db.text(
                            """
                            UPDATE perfil_coe_mesa_menu_opcion
                            SET activo = false,
                                modificador = :modificador,
                                modificacion = :modificacion
                            WHERE id = :id
                            """
                        ),
                        {
                            "id": row.id,
                            "modificador": modificador,
                            "modificacion": now,
                        },
                    )

        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "Error de base de datos", "details": str(e)}), 500

    return jsonify(
        {
            "mensaje": "Matriz de permisos actualizada",
            "coe_id": coe_id,
            "mesa_id": mesa_id,
            "celdas_procesadas": len(normalized),
            "reemplazar": reemplazar,
        }
    )
