import csv
import io
import os
from datetime import date, datetime

from flask import Blueprint, Response, jsonify, request, stream_with_context

import config as app_config
from config import MYSQL_DB, MYSQL_HOST, MYSQL_PASS, MYSQL_PORT, MYSQL_USER

geoJson_afectaciones_script_bp = Blueprint("get_geoJson_afectaciones", __name__)


def _get_mysql_impl():
    try:
        import pymysql  # type: ignore
        return ("pymysql", pymysql)
    except Exception:
        pass
    try:
        import mysql.connector  # type: ignore
        return ("mysql-connector", mysql.connector)
    except Exception as exc:  # pragma: no cover - runtime only
        raise ImportError("No MySQL client library installed") from exc


def _open_mysql_connection(mysql_impl):
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


def _open_mysql_cursor(conn, mysql_impl):
    impl_name, _ = mysql_impl
    if impl_name == "mysql-connector":
        return conn.cursor(buffered=False)
    return conn.cursor()


def _format_value(value):
    if value is None:
        return ""
    if isinstance(value, datetime):
        return value.strftime("%Y-%m-%d %H:%M:%S")
    if isinstance(value, date):
        return value.strftime("%Y-%m-%d")
    return value

def _to_float(v):
    if v is None:
        return None
    if isinstance(v, (int, float)):
        return float(v)
    if isinstance(v, str):
        s = v.strip()
        if not s:
            return None
        s = s.replace(",", ".")
        try:
            return float(s)
        except Exception:
            return None
    return None



def _validate_token():
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


from flask import jsonify, request

@geoJson_afectaciones_script_bp.route("/api/public/get_geoJson_afectaciones", methods=["GET"])
def get_geoJson_afectaciones():
    ok, msg = _validate_token()
    if not ok:
        return jsonify({"error": msg}), 401

    page = int(request.args.get("page", 1))
    limit = int(request.args.get("limit", 5000))
    offset = (page - 1) * limit

    mysql_impl = _get_mysql_impl()
    conn = _open_mysql_connection(mysql_impl)
    cur = _open_mysql_cursor(conn, mysql_impl)

    try:
        sql = "SELECT * FROM dmeva.`RED-M-2026-GeoJSON-Afectaciones` LIMIT %s OFFSET %s"
        cur.execute(sql, (limit, offset))

        columns = [d[0] for d in cur.description]
        rows = cur.fetchall()

        # Validación mínima: existen las columnas
        if "latitud" not in [c.lower() for c in columns] and "latitud" not in columns:
            # por si viniera con otro case, abajo lo resolvemos con map
            pass

        # Mapa por índice (respeta el orden del SELECT *)
        idx = {col: i for i, col in enumerate(columns)}

        # Soporta case distinto (Latitud/LATITUD/etc.)
        lat_col = next((c for c in columns if c.lower() == "latitud"), None)
        lon_col = next((c for c in columns if c.lower() == "longitud"), None)

        if not lat_col or not lon_col:
            return jsonify({
                "error": "No encuentro columnas 'latitud' y/o 'longitud' en el SELECT",
                "columns": columns
            }), 400

        features = []
        for r in rows:
            # Convertir campos numéricos específicos a números
            props = {}
            numeric_fields = {
                "AnimalesAfetados", "AnimalesMuertos", "BienesPrivadosAfectados", "BienesPrivadosDestruidos",
                "BienesPublicosAfectados", "BienesPublicosDestruidos", "CentrosDeSaludAfectados", "CentrosDeSaludDestruidos",
                "EstablecimientosEducativosAfectacionFuncional", "EstablecimientosEducativosAfectados", "EstablecimientosEducativosDestruidos",
                "FamiliasAfectadas", "FamiliasDamnificadas", "HaCultivoAfectados", "HaCultivoPerdidos",
                "HaDeCoberturaVegetalQuemada", "KilometrosLinealesDeViasAfectadas", "MetrosLinealesDeViasAfectadas",
                "PersonasAfectadasDirectamente", "PersonasAfectadasIndirectamente", "PersonasDamnificadas",
                "PersonasEvacuadas", "PersonasExtraviadas", "PersonasFallecidas", "PersonasHeridas", "PersonasImpactadas",
                "PuentesAfectados", "PuentesDestruidos", "ViviendasAfectadas", "ViviendasDestruidas", "Zona"
            }
            
            for i, col in enumerate(columns):
                val = r[i]
                if col in numeric_fields:
                    if val is None or val == "":
                        props[col] = 0
                    elif isinstance(val, (int, float)):
                        props[col] = val
                    else:
                        try:
                            props[col] = int(str(val).strip())
                        except ValueError:
                            try:
                                props[col] = float(str(val).strip().replace(',', '.'))
                            except ValueError:
                                props[col] = _format_value(val)
                else:
                    props[col] = _format_value(val)

            lat = _to_float(props.get(lat_col))
            lon = _to_float(props.get(lon_col))

            geometry = None
            if lat is not None and lon is not None:
                geometry = {"type": "Point", "coordinates": [lon, lat]}  # [longitud, latitud]

            features.append({
                "type": "Feature",
                "geometry": geometry,   # null si faltan coords
                "properties": props
            })

        geojson = {
            "type": "FeatureCollection",
            "features": features,
            "metadata": {
                "page": page,
                "limit": limit,
                "count": len(features),
                "lat_column": lat_col,
                "lon_column": lon_col
            }
        }

        resp = jsonify(geojson)
        resp.mimetype = "application/geo+json"  # opcional pero recomendado
        return resp

    finally:
        cur.close()
        conn.close()

