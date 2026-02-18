import csv
import io
import os
import json
import time
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
            read_timeout=600,   # ✅ evita cortes por socket lento
            write_timeout=600,
            connect_timeout=15,
        )
    return impl.connect(
        host=MYSQL_HOST,
        user=MYSQL_USER,
        password=MYSQL_PASS,
        database=MYSQL_DB,
        port=MYSQL_PORT,
        connection_timeout=15,
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
    provided = request.args.get("token") or request.args.get("api_key")
    if not provided:
        return False, "Token requerido"
    if provided != configured:
        return False, "Token invalido"
    return True, None


# =========================
# 1) Endpoint normal (igual al tuyo, pero sin fetchall para no reventar memoria)
# =========================
@eventos_dashboard_csv_bp.route("/api/public/eventos_dashboard_json", methods=["GET"])
def eventos_dashboard_json():
    ok, msg = _validate_token()
    if not ok:
        return jsonify({"error": msg}), 401

    page = int(request.args.get("page", 1))
    limit = int(request.args.get("limit", 5000))
    if page < 1:
        page = 1
    if limit < 1:
        limit = 1
    if limit > 10000:
        limit = 10000

    offset = (page - 1) * limit

    mysql_impl = _get_mysql_impl()
    conn = _open_mysql_connection(mysql_impl)
    cur = _open_mysql_cursor(conn, mysql_impl)

    try:
        sql = "SELECT * FROM `2. RED-M Eventos Dashboard 2024+` LIMIT %s OFFSET %s"
        cur.execute(sql, (limit, offset))

        columns = [d[0] for d in cur.description]

        # ✅ leer por chunks (en vez de fetchall)
        data_rows = []
        while True:
            chunk = cur.fetchmany(500)
            if not chunk:
                break
            for r in chunk:
                data_rows.append([_format_value(v) for v in r])

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


# =========================
# 2) Endpoint DEBUG streaming (para ver progreso y saber si sigue vivo)
# =========================
@eventos_dashboard_csv_bp.route("/api/public/eventos_dashboard_json_stream", methods=["GET"])
def eventos_dashboard_json_stream():
    ok, msg = _validate_token()
    if not ok:
        return jsonify({"error": msg}), 401

    page = int(request.args.get("page", 1))
    limit = int(request.args.get("limit", 5000))
    if page < 1:
        page = 1
    if limit < 1:
        limit = 1
    if limit > 10000:
        limit = 10000

    offset = (page - 1) * limit

    mysql_impl = _get_mysql_impl()

    def generate():
        conn = None
        cur = None
        t0 = time.time()
        sent = 0

        # ✅ primer byte rápido (si esto no sale, ni Flask/NGINX respondió)
        yield json.dumps({"type": "starting", "ts": int(time.time())}) + "\n"

        try:
            conn = _open_mysql_connection(mysql_impl)
            cur = _open_mysql_cursor(conn, mysql_impl)

            sql = "SELECT * FROM `2. RED-M Eventos Dashboard 2024+` LIMIT %s OFFSET %s"
            yield json.dumps({"type": "executing_sql"}) + "\n"

            cur.execute(sql, (limit, offset))

            columns = [d[0] for d in cur.description]
            yield json.dumps({
                "type": "meta",
                "page": page,
                "limit": limit,
                "columns": columns
            }) + "\n"

            while True:
                chunk = cur.fetchmany(500)
                if not chunk:
                    break

                for r in chunk:
                    row = [_format_value(v) for v in r]
                    yield json.dumps({"type": "row", "row": row}) + "\n"
                    sent += 1

                yield json.dumps({
                    "type": "progress",
                    "rows_sent": sent,
                    "seconds": round(time.time() - t0, 2)
                }) + "\n"

            yield json.dumps({
                "type": "done",
                "rows_sent": sent,
                "seconds": round(time.time() - t0, 2)
            }) + "\n"

        finally:
            try:
                if cur is not None:
                    cur.close()
            finally:
                if conn is not None:
                    conn.close()

    return Response(
        stream_with_context(generate()),
        mimetype="application/x-ndjson",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",  # ayuda con nginx
        },
    )
