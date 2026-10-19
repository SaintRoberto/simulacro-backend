import os
from datetime import date, datetime

from flask import Blueprint, jsonify, request

import config as app_config
from config import MYSQL_DB, MYSQL_HOST, MYSQL_PASS, MYSQL_PORT, MYSQL_USER


geoJson_afectaciones_vs_asistencias_fecha_bp = Blueprint(
    "get_geoJson_afectaciones_vs_asistencias_fecha",
    __name__,
)

FECHA_DESDE = "2026-08-29"
VISTA_AFECTACIONES_VS_ASISTENCIAS = (
    "dmeva.`RED-M-2026-Afectaciones-vs-Asistencias.v2`"
)


def _get_mysql_impl_desde_fecha():
    try:
        import pymysql  # type: ignore

        return "pymysql", pymysql
    except Exception:
        pass

    try:
        import mysql.connector  # type: ignore

        return "mysql-connector", mysql.connector
    except Exception as exc:  # pragma: no cover - runtime only
        raise ImportError("No MySQL client library installed") from exc


def _open_mysql_connection_desde_fecha(mysql_impl):
    impl_name, impl = mysql_impl
    if impl_name == "pymysql":
        return impl.connect(
            host=MYSQL_HOST,
            user=MYSQL_USER,
            password=MYSQL_PASS,
            db=MYSQL_DB,
            port=MYSQL_PORT,
            charset="utf8mb4",
            cursorclass=impl.cursors.SSCursor,
        )

    return impl.connect(
        host=MYSQL_HOST,
        user=MYSQL_USER,
        password=MYSQL_PASS,
        database=MYSQL_DB,
        port=MYSQL_PORT,
    )


def _open_mysql_cursor_desde_fecha(conn, mysql_impl):
    impl_name, _ = mysql_impl
    if impl_name == "mysql-connector":
        return conn.cursor(buffered=False)
    return conn.cursor()


def _format_value_desde_fecha(value):
    if value is None:
        return ""
    if isinstance(value, datetime):
        return value.strftime("%Y-%m-%d %H:%M:%S")
    if isinstance(value, date):
        return value.strftime("%Y-%m-%d")
    return value


def _to_float_desde_fecha(value):
    if value is None:
        return None
    if isinstance(value, (int, float)):
        return float(value)
    if isinstance(value, str):
        normalized = value.strip().replace(",", ".")
        if not normalized:
            return None
        try:
            return float(normalized)
        except ValueError:
            return None
    return None


def _validate_token_desde_fecha():
    configured = os.environ.get("geoJson_afectaciones_TOKEN")
    if configured is None:
        configured = getattr(app_config, "geoJson_afectaciones_TOKEN", None)
    if configured is None:
        return True, None

    provided = request.args.get("token")
    if not provided:
        return False, "Token requerido"
    if provided != configured:
        return False, "Token invalido"
    return True, None


@geoJson_afectaciones_vs_asistencias_fecha_bp.route(
    "/api/public/get_geoJson_afectaciones_vs_asistencias_fecha",
    methods=["GET"],
)
def get_geoJson_afectaciones_vs_asistencias_fecha():
    ok, message = _validate_token_desde_fecha()
    if not ok:
        return jsonify({"error": message}), 401

    page = int(request.args.get("page", 1))
    limit = int(request.args.get("limit", 5000))
    offset = (page - 1) * limit

    mysql_impl = _get_mysql_impl_desde_fecha()
    conn = _open_mysql_connection_desde_fecha(mysql_impl)
    cur = _open_mysql_cursor_desde_fecha(conn, mysql_impl)

    try:
        sql = (
            f"SELECT * FROM {VISTA_AFECTACIONES_VS_ASISTENCIAS} "
            "WHERE Fecha >= %s LIMIT %s OFFSET %s"
        )
        cur.execute(sql, (FECHA_DESDE, limit, offset))

        columns = [description[0] for description in cur.description]
        rows = cur.fetchall()

        lat_col = next(
            (column for column in columns if column.lower() == "latitud"),
            None,
        )
        lon_col = next(
            (column for column in columns if column.lower() == "longitud"),
            None,
        )

        if not lat_col or not lon_col:
            return jsonify({
                "error": "No encuentro columnas 'latitud' y/o 'longitud' en el SELECT",
                "columns": columns,
            }), 400

        numeric_fields = {
            "AnimalesAfetados",
            "AnimalesMuertos",
            "BienesPrivadosAfectados",
            "BienesPrivadosDestruidos",
            "BienesPublicosAfectados",
            "BienesPublicosDestruidos",
            "CentrosDeSaludAfectados",
            "CentrosDeSaludDestruidos",
            "EstablecimientosEducativosAfectacionFuncional",
            "EstablecimientosEducativosAfectados",
            "EstablecimientosEducativosDestruidos",
            "FamiliasAfectadas",
            "FamiliasDamnificadas",
            "HaCultivoAfectados",
            "HaCultivoPerdidos",
            "HaDeCoberturaVegetalQuemada",
            "KilometrosLinealesDeViasAfectadas",
            "MetrosLinealesDeViasAfectadas",
            "PersonasAfectadasDirectamente",
            "PersonasAfectadasIndirectamente",
            "PersonasDamnificadas",
            "PersonasEvacuadas",
            "PersonasExtraviadas",
            "PersonasFallecidas",
            "PersonasHeridas",
            "PersonasImpactadas",
            "PuentesAfectados",
            "PuentesDestruidos",
            "ViviendasAfectadas",
            "ViviendasDestruidas",
            "Familias Beneficiadas",
            "KCA (15 días - 4 personas)",
            "KCAT",
            "KMCC AT",
            "KPRH (para 3 días)",
            "Kit Colación Escolar",
            "Kit Escolar",
            "Kit Medicamentos",
            "Kit Purificadores de Agua",
            "Kit Purificadores\u00a0de\u00a0Agua",
            "Kit Volcán",
            "Kit Volcan",
            "Kit de Alojamiento o herramientas familiar",
            "Kit de Aseo Personal",
            "Kit de Bebé)",
            "Kit de Bebe",
            "Kit de Cocina",
            "Kit de Dormir",
            "Kit de Limpieza (albergue)",
            "Kit de Limpieza)",
            "Kit de Limpieza",
            "Kit de Mujer Embarazada)",
            "Kit de Mujer Embarazada",
            "Kit de Uniforme",
            "Kit de Vajilla",
            "Kit de Vestir",
            "MES DE ENTREGA DE AH",
            "RA (24 horas)",
            "Total Bienes",
            "Personas Beneficiadas",
            "Zona",
            "SecuenciaNacional",
            "SecuenciaProvincial",
            "Kit Colacion Escolar",
            "HectareasAfectadas",
            "HectareasDestruidas",
        }

        features = []
        for row in rows:
            properties = {}
            for index, column in enumerate(columns):
                value = row[index]
                if column not in numeric_fields:
                    properties[column] = _format_value_desde_fecha(value)
                    continue

                if value is None or value == "":
                    properties[column] = 0
                elif isinstance(value, (int, float)):
                    properties[column] = value
                else:
                    try:
                        properties[column] = int(str(value).strip())
                    except ValueError:
                        try:
                            properties[column] = float(
                                str(value).strip().replace(",", ".")
                            )
                        except ValueError:
                            properties[column] = (
                                _format_value_desde_fecha(value)
                            )

            latitude = _to_float_desde_fecha(properties.get(lat_col))
            longitude = _to_float_desde_fecha(properties.get(lon_col))
            geometry = None
            if latitude is not None and longitude is not None:
                geometry = {
                    "type": "Point",
                    "coordinates": [longitude, latitude],
                }

            features.append({
                "type": "Feature",
                "geometry": geometry,
                "properties": properties,
            })

        response = jsonify({
            "type": "FeatureCollection",
            "features": features,
            "metadata": {
                "page": page,
                "limit": limit,
                "count": len(features),
                "lat_column": lat_col,
                "lon_column": lon_col,
            },
        })
        response.mimetype = "application/geo+json"
        return response
    finally:
        cur.close()
        conn.close()
