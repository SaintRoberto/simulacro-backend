import csv
import io
import os
from datetime import date, datetime

from flask import Blueprint, Response, jsonify, request, stream_with_context

import config as app_config
from config import MYSQL_DB, MYSQL_HOST, MYSQL_PASS, MYSQL_PORT, MYSQL_USER

eventos_historico_csv_bp = Blueprint("eventos_historico_csv", __name__)


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
    configured = os.environ.get("EVENTOS_HISTORICO_TOKEN")
    if configured is None:
        configured = getattr(app_config, "EVENTOS_HISTORICO_TOKEN", None)
    if configured is None:
        return True, None
    provided = request.args.get("token")
    if not provided:
        return False, "Token requerido"
    if provided != configured:
        return False, "Token invalido"
    return True, None


@eventos_historico_csv_bp.route("/api/public/eventos_historico", methods=["GET"])
def export_eventos_historico_csv():
    ok, msg = _validate_token()
    if not ok:
        return jsonify({"error": msg}), 401

    try:
        mysql_impl = _get_mysql_impl()
    except ImportError:
        return jsonify({"error": "No MySQL client library installed"}), 500

    def generate():
        conn = None
        cursor = None
        try:
            conn = _open_mysql_connection(mysql_impl)
            cursor = _open_mysql_cursor(conn, mysql_impl)
            cursor.execute("SELECT * FROM `1. RED-M Eventos Historico 2024+`")

            columns = [desc[0] for desc in cursor.description]
            yield _csv_line(columns)

            while True:
                rows = cursor.fetchmany(1000)
                if not rows:
                    break
                for row in rows:
                    yield _csv_line([_format_value(v) for v in row])
        finally:
            try:
                if cursor is not None:
                    cursor.close()
            finally:
                if conn is not None:
                    conn.close()

    return Response(stream_with_context(generate()), mimetype="text/csv")
