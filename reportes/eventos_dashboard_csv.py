import csv
import io
import os
from datetime import date, datetime

from flask import Blueprint, Response, jsonify, request, stream_with_context

import config as app_config
from config import MYSQL_DB, MYSQL_HOST, MYSQL_PASS, MYSQL_PORT, MYSQL_USER

eventos_dashboard_csv_bp = Blueprint("eventos_dashboard_csv", __name__)


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


def _csv_line(row):
    buffer = io.StringIO()
    writer = csv.writer(buffer)
    writer.writerow(row)
    return buffer.getvalue()


def _validate_token():
    configured = os.environ.get("EVENTOS_DASHBOARD_TOKEN")
    if configured is None:
        configured = getattr(app_config, "EVENTOS_DASHBOARD_TOKEN", None)
    if configured is None:
        return True, None
    provided = request.args.get("token")
    if not provided:
        return False, "Token requerido"
    if provided != configured:
        return False, "Token invalido"
    return True, None


from flask import jsonify, request

@eventos_dashboard_csv_bp.route("/api/public/eventos_dashboard_json", methods=["GET"])
def eventos_dashboard_json():
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
        # Mantener el orden natural del SELECT * (no inventar orden alfabético)
        sql = "SELECT * FROM `2. RED-M Eventos Dashboard 2024+` LIMIT %s OFFSET %s"
        cur.execute(sql, (limit, offset))

        columns = [d[0] for d in cur.description]  # <-- ESTE orden es el que manda
        rows = cur.fetchall()

        # rows como arrays en el mismo orden que columns
        data_rows = [
            [_format_value(v) for v in r]
            for r in rows
        ]

        return jsonify({
            "page": page,
            "limit": limit,
            "count": len(data_rows),
            "columns": columns,
            "rows": data_rows
        })
    finally:
        cur.close()
        conn.close()
