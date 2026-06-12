from datetime import datetime, timezone

from flask import jsonify, request

from barridos import barridos_bp
from models import db


TABLE_NAME = "public.barridos"


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


def _barrido_estado_existe(barrido_estado_id):
    row = db.session.execute(
        db.text("SELECT 1 FROM public.barrido_estado WHERE id = :id"),
        {"id": barrido_estado_id},
    ).fetchone()
    return row is not None


def _volcan_accidente_geografico_existe(accidente_geografico_id):
    if accidente_geografico_id in (None, "", 0, "0"):
        return True

    row = db.session.execute(
        db.text(
            """
            SELECT 1
            FROM public.accidentes_geograficos ag
            INNER JOIN public.accidente_geografico_tipos agt
                ON agt.id = ag.accidente_geografico_tipo_id
            WHERE ag.id = :id
              AND agt.codigo = 'VOLCAN'
              AND COALESCE(ag.activo, true) = true
              AND COALESCE(agt.activo, true) = true
            """
        ),
        {"id": accidente_geografico_id},
    ).fetchone()
    return row is not None


def _serialize_barrido(row):
    item = {
        "id": getattr(row, "id", None),
        "emergencia_id": getattr(row, "emergencia_id", None),
        "evento_tipo_id": getattr(row, "evento_tipo_id", None),
        "evento_fecha": _to_iso_optional(getattr(row, "evento_fecha", None)),
        "provincia_id": getattr(row, "provincia_id", None),
        "canton_id": getattr(row, "canton_id", None),
        "parroquia_id": getattr(row, "parroquia_id", None),
        "sector": getattr(row, "sector", None),
        "longitud": _to_float_optional(getattr(row, "longitud", None)),
        "latitud": _to_float_optional(getattr(row, "latitud", None)),
        "accidente_geografico_id": getattr(row, "accidente_geografico_id", None),
        "volcan_id": getattr(row, "volcan_id", None),
        "volcan_nombre": getattr(row, "volcan_nombre", None),
        "volcan_descripcion": getattr(row, "volcan_descripcion", None),
        "volcan_longitud": _to_float_optional(getattr(row, "volcan_longitud", None)),
        "volcan_latitud": _to_float_optional(getattr(row, "volcan_latitud", None)),
        "magnitud": _to_float_optional(getattr(row, "magnitud", None)),
        "profundidad": _to_float_optional(getattr(row, "profundidad", None)),
        "epicentro": getattr(row, "epicentro", None),
        "barrido_estado_id": getattr(row, "barrido_estado_id", None),
        "barrido_estado_codigo": getattr(row, "barrido_estado_codigo", None),
        "barrido_estado_nombre": getattr(row, "barrido_estado_nombre", None),
        "barrido_estado_descripcion": getattr(row, "barrido_estado_descripcion", None),
        "barrido_estado_permite_edicion": getattr(row, "barrido_estado_permite_edicion", None),
        "barrido_estado_permite_registro_monitoreo": getattr(row, "barrido_estado_permite_registro_monitoreo", None),
        "barrido_estado_es_estado_final": getattr(row, "barrido_estado_es_estado_final", None),
        "activo": getattr(row, "activo", None),
        "creador": getattr(row, "creador", None),
        "creacion": _to_iso_optional(getattr(row, "creacion", None)),
        "modificador": getattr(row, "modificador", None),
        "modificacion": _to_iso_optional(getattr(row, "modificacion", None)),
    }

    optional_fields = [
        "emergencia_nombre",
        "evento_tipo_nombre",
        "provincia_nombre",
        "canton_nombre",
        "parroquia_nombre",
    ]
    for field in optional_fields:
        if hasattr(row, field):
            item[field] = getattr(row, field)

    return item


def _get_barrido_by_id(item_id):
    query = db.text(
        f"""
        SELECT
            b.id,
            b.emergencia_id,
            e.nombre AS emergencia_nombre,
            b.evento_tipo_id,
            et.nombre AS evento_tipo_nombre,
            b.evento_fecha,
            b.provincia_id,
            p.nombre AS provincia_nombre,
            b.canton_id,
            c.nombre AS canton_nombre,
            b.parroquia_id,
            q.nombre AS parroquia_nombre,
            b.sector,
            b.longitud,
            b.latitud,
            b.accidente_geografico_id,
            CASE WHEN vt.codigo = 'VOLCAN' THEN v.id END AS volcan_id,
            CASE WHEN vt.codigo = 'VOLCAN' THEN v.nombre END AS volcan_nombre,
            CASE WHEN vt.codigo = 'VOLCAN' THEN v.descripcion END AS volcan_descripcion,
            CASE WHEN vt.codigo = 'VOLCAN' THEN v.longitud END AS volcan_longitud,
            CASE WHEN vt.codigo = 'VOLCAN' THEN v.latitud END AS volcan_latitud,
            b.magnitud,
            b.profundidad,
            b.epicentro,
            b.barrido_estado_id,
            be.codigo AS barrido_estado_codigo,
            be.nombre AS barrido_estado_nombre,
            be.descripcion AS barrido_estado_descripcion,
            be.permite_edicion AS barrido_estado_permite_edicion,
            be.permite_registro_monitoreo AS barrido_estado_permite_registro_monitoreo,
            be.es_estado_final AS barrido_estado_es_estado_final,
            b.activo,
            b.creador,
            b.creacion,
            b.modificador,
            b.modificacion
        FROM {TABLE_NAME} b
        LEFT JOIN public.emergencias e
            ON e.id = b.emergencia_id
        LEFT JOIN public.evento_tipos et
            ON et.id = b.evento_tipo_id
        LEFT JOIN public.provincias p
            ON p.id = b.provincia_id
        LEFT JOIN public.cantones c
            ON c.provincia_id = b.provincia_id
           AND c.id = b.canton_id
        LEFT JOIN public.parroquias q
            ON q.provincia_id = b.provincia_id
           AND q.canton_id = b.canton_id
           AND q.id = b.parroquia_id
        LEFT JOIN public.barrido_estado be
            ON be.id = b.barrido_estado_id
        LEFT JOIN public.accidentes_geograficos v
            ON v.id = b.accidente_geografico_id
        LEFT JOIN public.accidente_geografico_tipos vt
            ON vt.id = v.accidente_geografico_tipo_id
        WHERE b.id = :id
        """
    )
    return db.session.execute(query, {"id": item_id}).fetchone()


def _select_barridos(where_clause="", order_by="b.id ASC"):
    query = db.text(
        f"""
        SELECT
            b.id,
            b.emergencia_id,
            e.nombre AS emergencia_nombre,
            b.evento_tipo_id,
            et.nombre AS evento_tipo_nombre,
            b.evento_fecha,
            b.provincia_id,
            p.nombre AS provincia_nombre,
            b.canton_id,
            c.nombre AS canton_nombre,
            b.parroquia_id,
            q.nombre AS parroquia_nombre,
            b.sector,
            b.longitud,
            b.latitud,
            b.accidente_geografico_id,
            CASE WHEN vt.codigo = 'VOLCAN' THEN v.id END AS volcan_id,
            CASE WHEN vt.codigo = 'VOLCAN' THEN v.nombre END AS volcan_nombre,
            CASE WHEN vt.codigo = 'VOLCAN' THEN v.descripcion END AS volcan_descripcion,
            CASE WHEN vt.codigo = 'VOLCAN' THEN v.longitud END AS volcan_longitud,
            CASE WHEN vt.codigo = 'VOLCAN' THEN v.latitud END AS volcan_latitud,
            b.magnitud,
            b.profundidad,
            b.epicentro,
            b.barrido_estado_id,
            be.codigo AS barrido_estado_codigo,
            be.nombre AS barrido_estado_nombre,
            be.descripcion AS barrido_estado_descripcion,
            be.permite_edicion AS barrido_estado_permite_edicion,
            be.permite_registro_monitoreo AS barrido_estado_permite_registro_monitoreo,
            be.es_estado_final AS barrido_estado_es_estado_final,
            b.activo,
            b.creador,
            b.creacion,
            b.modificador,
            b.modificacion
        FROM {TABLE_NAME} b
        LEFT JOIN public.emergencias e
            ON e.id = b.emergencia_id
        LEFT JOIN public.evento_tipos et
            ON et.id = b.evento_tipo_id
        LEFT JOIN public.provincias p
            ON p.id = b.provincia_id
        LEFT JOIN public.cantones c
            ON c.provincia_id = b.provincia_id
           AND c.id = b.canton_id
        LEFT JOIN public.parroquias q
            ON q.provincia_id = b.provincia_id
           AND q.canton_id = b.canton_id
           AND q.id = b.parroquia_id
        LEFT JOIN public.barrido_estado be
            ON be.id = b.barrido_estado_id
        LEFT JOIN public.accidentes_geograficos v
            ON v.id = b.accidente_geografico_id
        LEFT JOIN public.accidente_geografico_tipos vt
            ON vt.id = v.accidente_geografico_tipo_id
        {where_clause}
        ORDER BY {order_by}
        """
    )
    return query


@barridos_bp.route("/api/barridos", methods=["GET"])
def get_barridos():
    """Listar barridos.
    ---
    tags:
      - Barridos
    summary: Listar barridos
    description: Devuelve todos los registros de `barridos` ordenados por `id` ascendente. Incluye datos de emergencia, tipo de evento, ubicacion del epicentro, coordenadas, datos complementarios, estado de barrido y auditoria.
    responses:
      200:
        description: Lista de barridos
        schema:
          type: array
          items:
            type: object
            properties:
              id: {type: integer, description: Identificador unico del barrido}
              emergencia_id: {type: integer, description: ID de la emergencia relacionada}
              emergencia_nombre: {type: string, description: Nombre de la emergencia, nullable: true}
              evento_tipo_id: {type: integer, description: ID del tipo de evento}
              evento_tipo_nombre: {type: string, description: Nombre del tipo de evento, nullable: true}
              evento_fecha: {type: string, format: date-time, description: Fecha y hora del evento}
              provincia_id: {type: integer, description: ID de la provincia del epicentro}
              provincia_nombre: {type: string, description: Nombre de la provincia, nullable: true}
              canton_id: {type: integer, description: ID del canton del epicentro}
              canton_nombre: {type: string, description: Nombre del canton, nullable: true}
              parroquia_id: {type: integer, description: ID de la parroquia del epicentro}
              parroquia_nombre: {type: string, description: Nombre de la parroquia, nullable: true}
              sector: {type: string, description: Sector del epicentro}
              longitud: {type: number, format: float, description: Longitud del epicentro}
              latitud: {type: number, format: float, description: Latitud del epicentro}
              accidente_geografico_id: {type: integer, description: Para erupcion volcanica contiene el ID de `accidentes_geograficos` cuyo tipo tiene codigo VOLCAN; para sismo se mantiene en 0}
              volcan_id: {type: integer, description: ID del accidente geografico tipo VOLCAN asociado al barrido, nullable: true}
              volcan_nombre: {type: string, description: Nombre del volcan asociado, nullable: true}
              volcan_descripcion: {type: string, description: Descripcion del volcan asociado, nullable: true}
              volcan_longitud: {type: number, format: float, description: Longitud del volcan asociado, nullable: true}
              volcan_latitud: {type: number, format: float, description: Latitud del volcan asociado, nullable: true}
              magnitud: {type: number, format: float, description: Magnitud para sismo}
              profundidad: {type: number, format: float, description: Profundidad para sismo}
              epicentro: {type: string, description: Epicentro textual para sismo, nullable: true}
              barrido_estado_id: {type: integer, description: ID del estado del barrido}
              barrido_estado_codigo: {type: string, description: Codigo del estado del barrido, nullable: true}
              barrido_estado_nombre: {type: string, description: Nombre del estado del barrido, nullable: true}
              barrido_estado_descripcion: {type: string, description: Descripcion del estado del barrido, nullable: true}
              barrido_estado_permite_edicion: {type: boolean, description: Indica si el estado permite editar el barrido, nullable: true}
              barrido_estado_permite_registro_monitoreo: {type: boolean, description: Indica si el estado permite registrar monitoreo, nullable: true}
              barrido_estado_es_estado_final: {type: boolean, description: Indica si el estado finaliza el barrido, nullable: true}
              activo: {type: boolean, description: Estado activo del barrido}
              creador: {type: string, description: Usuario creador, nullable: true}
              creacion: {type: string, format: date-time, description: Fecha de creacion}
              modificador: {type: string, description: Usuario modificador, nullable: true}
              modificacion: {type: string, format: date-time, description: Fecha de modificacion, nullable: true}
      500:
        description: Error inesperado al consultar los barridos
    """
    result = db.session.execute(_select_barridos())
    return jsonify([_serialize_barrido(row) for row in result])


@barridos_bp.route("/api/barridos/emergencia/<int:emergencia_id>", methods=["GET"])
def get_barridos_by_emergencia(emergencia_id):
    """Listar barridos por emergencia.
    ---
    tags:
      - Barridos
    summary: Listar barridos por emergencia
    description: Devuelve las cabeceras de barrido activas asociadas a la emergencia indicada. Este endpoint permite que los clientes consulten los barridos solicitados antes de registrar el detalle de monitoreo territorial.
    parameters:
      - name: emergencia_id
        in: path
        type: integer
        required: true
        description: Identificador de la emergencia a consultar
    responses:
      200:
        description: Lista de barridos activos de la emergencia
        schema:
          type: array
          items:
            type: object
            properties:
              id: {type: integer, description: Identificador unico del barrido}
              emergencia_id: {type: integer, description: ID de la emergencia relacionada}
              emergencia_nombre: {type: string, description: Nombre de la emergencia, nullable: true}
              evento_tipo_id: {type: integer, description: ID del tipo de evento}
              evento_tipo_nombre: {type: string, description: Nombre del tipo de evento, nullable: true}
              evento_fecha: {type: string, format: date-time, description: Fecha y hora del evento}
              provincia_id: {type: integer, description: ID de la provincia del epicentro}
              provincia_nombre: {type: string, description: Nombre de la provincia, nullable: true}
              canton_id: {type: integer, description: ID del canton del epicentro}
              canton_nombre: {type: string, description: Nombre del canton, nullable: true}
              parroquia_id: {type: integer, description: ID de la parroquia del epicentro}
              parroquia_nombre: {type: string, description: Nombre de la parroquia, nullable: true}
              sector: {type: string, description: Sector del epicentro}
              longitud: {type: number, format: float, description: Longitud del epicentro}
              latitud: {type: number, format: float, description: Latitud del epicentro}
              accidente_geografico_id: {type: integer, description: Para erupcion volcanica contiene el ID de `accidentes_geograficos` cuyo tipo tiene codigo VOLCAN; para sismo se mantiene en 0}
              volcan_id: {type: integer, description: ID del accidente geografico tipo VOLCAN asociado al barrido, nullable: true}
              volcan_nombre: {type: string, description: Nombre del volcan asociado, nullable: true}
              volcan_descripcion: {type: string, description: Descripcion del volcan asociado, nullable: true}
              volcan_longitud: {type: number, format: float, description: Longitud del volcan asociado, nullable: true}
              volcan_latitud: {type: number, format: float, description: Latitud del volcan asociado, nullable: true}
              magnitud: {type: number, format: float, description: Magnitud para sismo}
              profundidad: {type: number, format: float, description: Profundidad para sismo}
              epicentro: {type: string, description: Epicentro textual para sismo, nullable: true}
              barrido_estado_id: {type: integer, description: ID del estado del barrido}
              barrido_estado_codigo: {type: string, description: Codigo del estado del barrido, nullable: true}
              barrido_estado_nombre: {type: string, description: Nombre del estado del barrido, nullable: true}
              barrido_estado_descripcion: {type: string, description: Descripcion del estado del barrido, nullable: true}
              barrido_estado_permite_edicion: {type: boolean, description: Indica si el estado permite editar el barrido, nullable: true}
              barrido_estado_permite_registro_monitoreo: {type: boolean, description: Indica si el estado permite registrar monitoreo, nullable: true}
              barrido_estado_es_estado_final: {type: boolean, description: Indica si el estado finaliza el barrido, nullable: true}
              activo: {type: boolean, description: Estado activo del barrido}
              creador: {type: string, description: Usuario creador, nullable: true}
              creacion: {type: string, format: date-time, description: Fecha de creacion}
              modificador: {type: string, description: Usuario modificador, nullable: true}
              modificacion: {type: string, format: date-time, description: Fecha de modificacion, nullable: true}
      500:
        description: Error inesperado al consultar los barridos por emergencia
    """
    query = _select_barridos(
        "WHERE b.emergencia_id = :emergencia_id AND COALESCE(b.activo, true) = true",
        "b.evento_fecha DESC, b.id DESC",
    )
    result = db.session.execute(query, {"emergencia_id": emergencia_id})
    return jsonify([_serialize_barrido(row) for row in result])


@barridos_bp.route("/api/barridos/<int:id>", methods=["GET"])
def get_barrido(id):
    """Obtener barrido por ID.
    ---
    tags:
      - Barridos
    summary: Obtener barrido por ID
    description: Devuelve la cabecera de barrido identificada por `id`, incluyendo nombres descriptivos de emergencia, tipo de evento y ubicacion cuando existan.
    parameters:
      - name: id
        in: path
        type: integer
        required: true
        description: Identificador unico del barrido
    responses:
      200:
        description: Barrido encontrado
        schema:
          type: object
          properties:
            id: {type: integer, description: Identificador unico del barrido}
            emergencia_id: {type: integer, description: ID de la emergencia relacionada}
            emergencia_nombre: {type: string, description: Nombre de la emergencia, nullable: true}
            evento_tipo_id: {type: integer, description: ID del tipo de evento}
            evento_tipo_nombre: {type: string, description: Nombre del tipo de evento, nullable: true}
            evento_fecha: {type: string, format: date-time, description: Fecha y hora del evento}
            provincia_id: {type: integer, description: ID de la provincia del epicentro}
            provincia_nombre: {type: string, description: Nombre de la provincia, nullable: true}
            canton_id: {type: integer, description: ID del canton del epicentro}
            canton_nombre: {type: string, description: Nombre del canton, nullable: true}
            parroquia_id: {type: integer, description: ID de la parroquia del epicentro}
            parroquia_nombre: {type: string, description: Nombre de la parroquia, nullable: true}
            sector: {type: string, description: Sector del epicentro}
            longitud: {type: number, format: float, description: Longitud del epicentro}
            latitud: {type: number, format: float, description: Latitud del epicentro}
            accidente_geografico_id: {type: integer, description: Para erupcion volcanica contiene el ID de `accidentes_geograficos` cuyo tipo tiene codigo VOLCAN; para sismo se mantiene en 0}
            volcan_id: {type: integer, description: ID del accidente geografico tipo VOLCAN asociado al barrido, nullable: true}
            volcan_nombre: {type: string, description: Nombre del volcan asociado, nullable: true}
            volcan_descripcion: {type: string, description: Descripcion del volcan asociado, nullable: true}
            volcan_longitud: {type: number, format: float, description: Longitud del volcan asociado, nullable: true}
            volcan_latitud: {type: number, format: float, description: Latitud del volcan asociado, nullable: true}
            magnitud: {type: number, format: float, description: Magnitud para sismo}
            profundidad: {type: number, format: float, description: Profundidad para sismo}
            epicentro: {type: string, description: Epicentro textual para sismo, nullable: true}
            barrido_estado_id: {type: integer, description: ID del estado del barrido}
            barrido_estado_codigo: {type: string, description: Codigo del estado del barrido, nullable: true}
            barrido_estado_nombre: {type: string, description: Nombre del estado del barrido, nullable: true}
            barrido_estado_descripcion: {type: string, description: Descripcion del estado del barrido, nullable: true}
            barrido_estado_permite_edicion: {type: boolean, description: Indica si el estado permite editar el barrido, nullable: true}
            barrido_estado_permite_registro_monitoreo: {type: boolean, description: Indica si el estado permite registrar monitoreo, nullable: true}
            barrido_estado_es_estado_final: {type: boolean, description: Indica si el estado finaliza el barrido, nullable: true}
            activo: {type: boolean, description: Estado activo del barrido}
            creador: {type: string, description: Usuario creador, nullable: true}
            creacion: {type: string, format: date-time, description: Fecha de creacion}
            modificador: {type: string, description: Usuario modificador, nullable: true}
            modificacion: {type: string, format: date-time, description: Fecha de modificacion, nullable: true}
      404:
        description: Barrido no encontrado
      500:
        description: Error inesperado al consultar el barrido
    """
    item = _get_barrido_by_id(id)
    if not item:
        return jsonify({"error": "Barrido no encontrado"}), 404
    return jsonify(_serialize_barrido(item))


@barridos_bp.route("/api/barridos", methods=["POST"])
def create_barrido():
    """Crear barrido.
    ---
    tags:
      - Barridos
    summary: Crear barrido
    description: Inserta una cabecera de barrido en `barridos` con la emergencia, tipo y fecha de evento, ubicacion del epicentro, coordenadas, datos complementarios, estado de barrido y campos de auditoria.
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
            - evento_tipo_id
            - provincia_id
            - canton_id
            - parroquia_id
            - sector
            - barrido_estado_id
          properties:
            emergencia_id: {type: integer, description: ID de la emergencia relacionada}
            evento_tipo_id: {type: integer, description: ID del tipo de evento}
            evento_fecha: {type: string, format: date-time, description: Fecha y hora del evento. Si no se envia, usa la fecha actual del servidor}
            provincia_id: {type: integer, description: ID de la provincia del epicentro}
            canton_id: {type: integer, description: ID del canton del epicentro}
            parroquia_id: {type: integer, description: ID de la parroquia del epicentro}
            sector: {type: string, description: Sector del epicentro}
            longitud: {type: number, format: float, default: 0, description: Longitud del epicentro}
            latitud: {type: number, format: float, default: 0, description: Latitud del epicentro}
            accidente_geografico_id: {type: integer, default: 0, description: Para erupcion volcanica contiene el ID de `accidentes_geograficos` cuyo tipo tiene codigo VOLCAN; para sismo se mantiene en 0}
            magnitud: {type: number, format: float, default: 0, description: Magnitud para sismo}
            profundidad: {type: number, format: float, default: 0, description: Profundidad para sismo}
            epicentro: {type: string, description: Epicentro textual para sismo, nullable: true}
            barrido_estado_id: {type: integer, description: ID del estado del barrido}
            activo: {type: boolean, default: true, description: Estado activo del barrido}
            creador: {type: string, description: Usuario creador}
            modificador: {type: string, description: Usuario modificador}
    responses:
      201:
        description: Barrido creado correctamente
        schema:
          type: object
          properties:
            id: {type: integer, description: Identificador unico del barrido}
            emergencia_id: {type: integer, description: ID de la emergencia relacionada}
            evento_tipo_id: {type: integer, description: ID del tipo de evento}
            evento_fecha: {type: string, format: date-time, description: Fecha y hora del evento}
            provincia_id: {type: integer, description: ID de la provincia del epicentro}
            canton_id: {type: integer, description: ID del canton del epicentro}
            parroquia_id: {type: integer, description: ID de la parroquia del epicentro}
            sector: {type: string, description: Sector del epicentro}
            longitud: {type: number, format: float, description: Longitud del epicentro}
            latitud: {type: number, format: float, description: Latitud del epicentro}
            accidente_geografico_id: {type: integer, description: ID del accidente geografico tipo VOLCAN asociado para erupcion volcanica; para sismo se mantiene en 0}
            volcan_id: {type: integer, description: ID del accidente geografico tipo VOLCAN asociado al barrido, nullable: true}
            volcan_nombre: {type: string, description: Nombre del volcan asociado, nullable: true}
            volcan_descripcion: {type: string, description: Descripcion del volcan asociado, nullable: true}
            volcan_longitud: {type: number, format: float, description: Longitud del volcan asociado, nullable: true}
            volcan_latitud: {type: number, format: float, description: Latitud del volcan asociado, nullable: true}
            magnitud: {type: number, format: float, description: Magnitud para sismo}
            profundidad: {type: number, format: float, description: Profundidad para sismo}
            epicentro: {type: string, description: Epicentro textual para sismo, nullable: true}
            barrido_estado_id: {type: integer, description: ID del estado del barrido}
            barrido_estado_codigo: {type: string, description: Codigo del estado del barrido, nullable: true}
            barrido_estado_nombre: {type: string, description: Nombre del estado del barrido, nullable: true}
            barrido_estado_descripcion: {type: string, description: Descripcion del estado del barrido, nullable: true}
            barrido_estado_permite_edicion: {type: boolean, description: Indica si el estado permite editar el barrido, nullable: true}
            barrido_estado_permite_registro_monitoreo: {type: boolean, description: Indica si el estado permite registrar monitoreo, nullable: true}
            barrido_estado_es_estado_final: {type: boolean, description: Indica si el estado finaliza el barrido, nullable: true}
            activo: {type: boolean, description: Estado activo del barrido}
            creador: {type: string, description: Usuario creador, nullable: true}
            creacion: {type: string, format: date-time, description: Fecha de creacion}
            modificador: {type: string, description: Usuario modificador, nullable: true}
            modificacion: {type: string, format: date-time, description: Fecha de modificacion, nullable: true}
      400:
        description: Campos requeridos faltantes, cuerpo JSON invalido, barrido_estado_id inexistente o accidente_geografico_id no corresponde a un volcan
      500:
        description: Error inesperado al crear el barrido
    """
    data = request.get_json(silent=True) or {}
    required_fields = [
        "emergencia_id",
        "evento_tipo_id",
        "provincia_id",
        "canton_id",
        "parroquia_id",
        "sector",
        "barrido_estado_id",
    ]
    missing_fields = [field for field in required_fields if data.get(field) is None]
    if missing_fields:
        return jsonify({"error": f"Campos requeridos faltantes: {', '.join(missing_fields)}"}), 400

    if not _barrido_estado_existe(data["barrido_estado_id"]):
        return jsonify({"error": "barrido_estado_id no existe en barrido_estado"}), 400

    if not _volcan_accidente_geografico_existe(data.get("accidente_geografico_id", 0)):
        return jsonify({"error": "accidente_geografico_id debe ser un accidente_geografico activo de tipo VOLCAN"}), 400

    now = datetime.now(timezone.utc)
    creador = data.get("creador", "Sistema")
    modificador = data.get("modificador", creador)

    query = db.text(
        f"""
        INSERT INTO {TABLE_NAME} (
            emergencia_id,
            evento_tipo_id,
            evento_fecha,
            provincia_id,
            canton_id,
            parroquia_id,
            sector,
            longitud,
            latitud,
            accidente_geografico_id,
            magnitud,
            profundidad,
            epicentro,
            barrido_estado_id,
            activo,
            creador,
            creacion,
            modificador,
            modificacion
        )
        VALUES (
            :emergencia_id,
            :evento_tipo_id,
            :evento_fecha,
            :provincia_id,
            :canton_id,
            :parroquia_id,
            :sector,
            :longitud,
            :latitud,
            :accidente_geografico_id,
            :magnitud,
            :profundidad,
            :epicentro,
            :barrido_estado_id,
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
                "emergencia_id": data["emergencia_id"],
                "evento_tipo_id": data["evento_tipo_id"],
                "evento_fecha": data.get("evento_fecha", now),
                "provincia_id": data["provincia_id"],
                "canton_id": data["canton_id"],
                "parroquia_id": data["parroquia_id"],
                "sector": data["sector"],
                "longitud": data.get("longitud", 0),
                "latitud": data.get("latitud", 0),
                "accidente_geografico_id": data.get("accidente_geografico_id", 0),
                "magnitud": data.get("magnitud", 0),
                "profundidad": data.get("profundidad", 0),
                "epicentro": data.get("epicentro"),
                "barrido_estado_id": data["barrido_estado_id"],
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
            return jsonify({"error": "No se pudo crear el barrido"}), 500

        item_id = row[0]
        db.session.commit()
    except Exception as exc:
        db.session.rollback()
        return jsonify({"error": "Error al crear el barrido", "detalle": str(exc)}), 500

    item = _get_barrido_by_id(item_id)
    if not item:
        return jsonify({"error": "Barrido no encontrado"}), 404

    return jsonify(_serialize_barrido(item)), 201


@barridos_bp.route("/api/barridos/<int:id>", methods=["PUT"])
def update_barrido(id):
    """Actualizar barrido.
    ---
    tags:
      - Barridos
    summary: Actualizar barrido
    description: Actualiza de forma parcial los campos editables de la cabecera de barrido identificada por `id`.
    consumes:
      - application/json
    parameters:
      - name: id
        in: path
        type: integer
        required: true
        description: Identificador unico del barrido
      - in: body
        name: body
        required: true
        schema:
          type: object
          properties:
            emergencia_id: {type: integer, description: ID de la emergencia relacionada}
            evento_tipo_id: {type: integer, description: ID del tipo de evento}
            evento_fecha: {type: string, format: date-time, description: Fecha y hora del evento}
            provincia_id: {type: integer, description: ID de la provincia del epicentro}
            canton_id: {type: integer, description: ID del canton del epicentro}
            parroquia_id: {type: integer, description: ID de la parroquia del epicentro}
            sector: {type: string, description: Sector del epicentro}
            longitud: {type: number, format: float, description: Longitud del epicentro}
            latitud: {type: number, format: float, description: Latitud del epicentro}
            accidente_geografico_id: {type: integer, description: Para erupcion volcanica contiene el ID de `accidentes_geograficos` cuyo tipo tiene codigo VOLCAN; para sismo se mantiene en 0}
            magnitud: {type: number, format: float, description: Magnitud para sismo}
            profundidad: {type: number, format: float, description: Profundidad para sismo}
            epicentro: {type: string, description: Epicentro textual para sismo, nullable: true}
            barrido_estado_id: {type: integer, description: ID del estado del barrido}
            activo: {type: boolean, description: Estado activo del barrido}
            modificador: {type: string, description: Usuario modificador}
    responses:
      200:
        description: Barrido actualizado correctamente
        schema:
          type: object
          properties:
            id: {type: integer, description: Identificador unico del barrido}
            emergencia_id: {type: integer, description: ID de la emergencia relacionada}
            evento_tipo_id: {type: integer, description: ID del tipo de evento}
            evento_fecha: {type: string, format: date-time, description: Fecha y hora del evento}
            provincia_id: {type: integer, description: ID de la provincia del epicentro}
            canton_id: {type: integer, description: ID del canton del epicentro}
            parroquia_id: {type: integer, description: ID de la parroquia del epicentro}
            sector: {type: string, description: Sector del epicentro}
            longitud: {type: number, format: float, description: Longitud del epicentro}
            latitud: {type: number, format: float, description: Latitud del epicentro}
            accidente_geografico_id: {type: integer, description: ID del accidente geografico tipo VOLCAN asociado para erupcion volcanica; para sismo se mantiene en 0}
            volcan_id: {type: integer, description: ID del accidente geografico tipo VOLCAN asociado al barrido, nullable: true}
            volcan_nombre: {type: string, description: Nombre del volcan asociado, nullable: true}
            volcan_descripcion: {type: string, description: Descripcion del volcan asociado, nullable: true}
            volcan_longitud: {type: number, format: float, description: Longitud del volcan asociado, nullable: true}
            volcan_latitud: {type: number, format: float, description: Latitud del volcan asociado, nullable: true}
            magnitud: {type: number, format: float, description: Magnitud para sismo}
            profundidad: {type: number, format: float, description: Profundidad para sismo}
            epicentro: {type: string, description: Epicentro textual para sismo, nullable: true}
            barrido_estado_id: {type: integer, description: ID del estado del barrido}
            barrido_estado_codigo: {type: string, description: Codigo del estado del barrido, nullable: true}
            barrido_estado_nombre: {type: string, description: Nombre del estado del barrido, nullable: true}
            barrido_estado_descripcion: {type: string, description: Descripcion del estado del barrido, nullable: true}
            barrido_estado_permite_edicion: {type: boolean, description: Indica si el estado permite editar el barrido, nullable: true}
            barrido_estado_permite_registro_monitoreo: {type: boolean, description: Indica si el estado permite registrar monitoreo, nullable: true}
            barrido_estado_es_estado_final: {type: boolean, description: Indica si el estado finaliza el barrido, nullable: true}
            activo: {type: boolean, description: Estado activo del barrido}
            creador: {type: string, description: Usuario creador, nullable: true}
            creacion: {type: string, format: date-time, description: Fecha de creacion}
            modificador: {type: string, description: Usuario modificador, nullable: true}
            modificacion: {type: string, format: date-time, description: Fecha de modificacion, nullable: true}
      400:
        description: No se enviaron campos validos, barrido_estado_id es invalido o accidente_geografico_id no corresponde a un volcan
      404:
        description: Barrido no encontrado
      500:
        description: Error inesperado al actualizar el barrido
    """
    data = request.get_json(silent=True) or {}
    if "barrido_estado_id" in data:
        if data["barrido_estado_id"] is None:
            return jsonify({"error": "barrido_estado_id no puede ser null"}), 400
        if not _barrido_estado_existe(data["barrido_estado_id"]):
            return jsonify({"error": "barrido_estado_id no existe en barrido_estado"}), 400

    if "accidente_geografico_id" in data and not _volcan_accidente_geografico_existe(data["accidente_geografico_id"]):
        return jsonify({"error": "accidente_geografico_id debe ser un accidente_geografico activo de tipo VOLCAN"}), 400

    now = datetime.now(timezone.utc)

    updatable_fields = [
        "emergencia_id",
        "evento_tipo_id",
        "evento_fecha",
        "provincia_id",
        "canton_id",
        "parroquia_id",
        "sector",
        "longitud",
        "latitud",
        "accidente_geografico_id",
        "magnitud",
        "profundidad",
        "epicentro",
        "barrido_estado_id",
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
            return jsonify({"error": "Barrido no encontrado"}), 404
        db.session.commit()
    except Exception as exc:
        db.session.rollback()
        return jsonify({"error": "Error al actualizar el barrido", "detalle": str(exc)}), 500

    item = _get_barrido_by_id(id)
    if not item:
        return jsonify({"error": "Barrido no encontrado"}), 404

    return jsonify(_serialize_barrido(item))


@barridos_bp.route("/api/barridos/<int:id>", methods=["DELETE"])
def delete_barrido(id):
    """Eliminar barrido.
    ---
    tags:
      - Barridos
    summary: Eliminar barrido
    description: Elimina fisicamente la cabecera de barrido identificada por `id`.
    parameters:
      - name: id
        in: path
        type: integer
        required: true
        description: Identificador unico del barrido
    responses:
      200:
        description: Barrido eliminado correctamente
        schema:
          type: object
          properties:
            mensaje: {type: string, description: Mensaje de confirmacion}
      404:
        description: Barrido no encontrado
      500:
        description: Error inesperado al eliminar el barrido
    """
    try:
        result = db.session.execute(
            db.text(f"DELETE FROM {TABLE_NAME} WHERE id = :id"),
            {"id": id},
        )
        if getattr(result, "rowcount", 0) == 0:
            db.session.rollback()
            return jsonify({"error": "Barrido no encontrado"}), 404

        db.session.commit()
    except Exception as exc:
        db.session.rollback()
        return jsonify({"error": "Error al eliminar el barrido", "detalle": str(exc)}), 500

    return jsonify({"mensaje": "Barrido eliminado correctamente"})
