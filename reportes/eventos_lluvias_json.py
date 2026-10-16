import os
from datetime import date, datetime, time, timedelta, timezone
from decimal import Decimal

from flask import Blueprint, current_app, jsonify, request

import config as app_config
from config import MYSQL_HOST, MYSQL_PASS, MYSQL_PORT, MYSQL_USER


eventos_lluvias_json_bp = Blueprint("eventos_lluvias_json", __name__)

SOURCE_SCHEMA = "dmeva"
SOURCE_PROCEDURE = "spEventosLluvia-rango"
START_DATETIME = "2026-08-29 00:00:00"
ECUADOR_TIMEZONE = timezone(timedelta(hours=-5))
MAX_JSON_LIMIT = 1000


def _get_mysql_impl():
    try:
        import pymysql  # type: ignore

        return "pymysql", pymysql
    except Exception:
        pass

    try:
        import mysql.connector  # type: ignore

        return "mysql-connector", mysql.connector
    except Exception as exc:  # pragma: no cover - depende del entorno
        raise ImportError("No MySQL client library installed") from exc


def _open_mysql_connection(mysql_impl):
    impl_name, impl = mysql_impl
    if impl_name == "pymysql":
        return impl.connect(
            host=MYSQL_HOST,
            user=MYSQL_USER,
            password=MYSQL_PASS,
            database=SOURCE_SCHEMA,
            port=MYSQL_PORT,
            charset="utf8mb4",
            cursorclass=impl.cursors.DictCursor,
        )

    return impl.connect(
        host=MYSQL_HOST,
        user=MYSQL_USER,
        password=MYSQL_PASS,
        database=SOURCE_SCHEMA,
        port=MYSQL_PORT,
    )


def _open_mysql_cursor(conn, mysql_impl):
    impl_name, _ = mysql_impl
    if impl_name == "mysql-connector":
        return conn.cursor(dictionary=True)
    return conn.cursor()


def _close_quietly(resource):
    try:
        if resource is not None:
            resource.close()
    except Exception:
        pass


def _format_value(value):
    if value is None:
        return ""
    if isinstance(value, datetime):
        return value.strftime("%Y-%m-%d %H:%M:%S")
    if isinstance(value, date):
        return value.strftime("%Y-%m-%d")
    if isinstance(value, time):
        return value.isoformat()
    if isinstance(value, Decimal):
        return str(value)
    if isinstance(value, bytes):
        return value.decode("utf-8", errors="replace")
    return value


def _current_cutoff():
    """Devuelve la fecha y hora actual de Ecuador para p_corte."""
    return datetime.now(ECUADOR_TIMEZONE).strftime("%Y-%m-%d %H:%M:%S")


def _validate_api_key():
    configured = os.environ.get("PUBLIC_API_KEYS")
    if configured is None:
        configured = getattr(app_config, "PUBLIC_API_KEYS", "")

    valid_keys = [key.strip() for key in configured.split(",") if key.strip()]
    if not valid_keys:
        return False, "API keys no configuradas"

    provided = request.headers.get("X-API-Key") or request.args.get("api_key")
    if not provided:
        return False, "API key requerida"
    if provided not in valid_keys:
        return False, "API key invalida"
    return True, None


def _parse_int_arg(name, default, minimum=None, maximum=None):
    raw_value = request.args.get(name, default)
    try:
        value = int(raw_value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{name} debe ser numerico") from exc
    if minimum is not None and value < minimum:
        value = minimum
    if maximum is not None and value > maximum:
        value = maximum
    return value


@eventos_lluvias_json_bp.route("/api/public/eventos_lluvias_json", methods=["GET"])
def eventos_lluvias_json():
    """Consulta paginada de eventos por lluvias mediante procedimiento almacenado.
    ---
    tags:
      - Reportes Publicos
    summary: Consultar eventos por lluvias en formato JSON
    produces:
      - application/json
    security: []
    parameters:
      - in: header
        name: X-API-Key
        type: string
        required: true
      - in: query
        name: limit
        type: integer
        minimum: 1
        maximum: 1000
        default: 1000
      - in: query
        name: last_id
        type: integer
        minimum: 0
        default: 0
        description: Posicion desde la cual continuar la consulta
    responses:
      200:
        description: Datos consultados correctamente
      400:
        description: Parametros de paginacion invalidos
      401:
        description: API key ausente o invalida
      500:
        description: Error consultando el procedimiento almacenado
    """
    ok, message = _validate_api_key()
    if not ok:
        return jsonify({"error": message}), 401

    try:
        limit = _parse_int_arg("limit", 1000, minimum=1, maximum=MAX_JSON_LIMIT)
        last_id = _parse_int_arg("last_id", 0, minimum=0)
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400

    conn = None
    cursor = None
    try:
        mysql_impl = _get_mysql_impl()
        conn = _open_mysql_connection(mysql_impl)
        cursor = _open_mysql_cursor(conn, mysql_impl)
        cutoff = _current_cutoff()
        cursor.execute(
            f"CALL `{SOURCE_SCHEMA}`.`{SOURCE_PROCEDURE}`(%s, %s)",
            (START_DATETIME, cutoff),
        )

        columns = [description[0] for description in cursor.description]
        all_rows = cursor.fetchall()
        rows = all_rows[last_id:last_id + limit]
        data_rows = [
            [_format_value(row.get(column)) for column in columns]
            for row in rows
        ]
        next_last_id = last_id + len(data_rows)

        return jsonify({
            "limit": limit,
            "count": len(data_rows),
            "last_id": last_id,
            "next_last_id": next_last_id,
            "has_more": next_last_id < len(all_rows),
            "columns": columns,
            "rows": data_rows,
        })
    except ImportError:
        return jsonify({"error": "No MySQL client library installed"}), 500
    except Exception as exc:
        current_app.logger.exception("Error consultando eventos por lluvias")
        return jsonify({
            "error": "No se pudo consultar el procedimiento de eventos por lluvias",
            "detail": str(exc),
        }), 500
    finally:
        _close_quietly(cursor)
        _close_quietly(conn)
