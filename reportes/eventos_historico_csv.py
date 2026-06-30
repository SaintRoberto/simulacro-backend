import csv
import io
import os
import threading
from datetime import date, datetime

from flask import Blueprint, Response, current_app, jsonify, request, stream_with_context

import config as app_config
from config import MYSQL_DB, MYSQL_HOST, MYSQL_PASS, MYSQL_PORT, MYSQL_USER

eventos_historico_csv_bp = Blueprint("eventos_historico_csv", __name__)

SOURCE_VIEW = "1. RED-M Eventos Historico 2024+"
CACHE_TABLE = "eventos_historico_json_cache"
CACHE_NEW_TABLE = "eventos_historico_json_cache_new"
CACHE_OLD_TABLE = "eventos_historico_json_cache_old"
CACHE_LOCK_NAME = "eventos_historico_json_cache_refresh"
MAX_JSON_LIMIT = 1000


class CacheRefreshInProgress(Exception):
    pass


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
            connect_timeout=15,
            read_timeout=600,
            write_timeout=600,
        )
    connect_kwargs = {
        "host": MYSQL_HOST,
        "user": MYSQL_USER,
        "password": MYSQL_PASS,
        "database": MYSQL_DB,
        "port": MYSQL_PORT,
        "connection_timeout": 15,
        "read_timeout": 600,
        "write_timeout": 600,
        "charset": "utf8mb4",
    }
    try:
        return impl.connect(**connect_kwargs)
    except TypeError:
        connect_kwargs.pop("read_timeout", None)
        connect_kwargs.pop("write_timeout", None)
        return impl.connect(**connect_kwargs)


def _open_mysql_cursor(conn, mysql_impl, unbuffered=False):
    impl_name, impl = mysql_impl
    if impl_name == "mysql-connector":
        return conn.cursor(buffered=not unbuffered)
    if impl_name == "pymysql" and unbuffered:
        return conn.cursor(impl.cursors.SSCursor)
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
    provided = request.args.get("token") or request.args.get("api_key")
    if not provided:
        return False, "Token requerido"
    if provided != configured:
        return False, "Token invalido"
    return True, None


def _quote_identifier(identifier):
    return f"`{identifier.replace('`', '``')}`"


def _parse_int_arg(name, default, minimum=None, maximum=None):
    raw_value = request.args.get(name, default)
    try:
        value = int(raw_value)
    except (TypeError, ValueError):
        raise ValueError(f"{name} debe ser numerico")
    if minimum is not None and value < minimum:
        value = minimum
    if maximum is not None and value > maximum:
        value = maximum
    return value


def _is_missing_table_error(exc):
    error_code = getattr(exc, "errno", None)
    if error_code == 1146:
        return True
    args = getattr(exc, "args", ())
    return bool(args and args[0] == 1146)


def _execute_session_timeouts(cur):
    cur.execute("SET SESSION net_read_timeout = 600")
    cur.execute("SET SESSION net_write_timeout = 600")
    cur.execute("SET SESSION wait_timeout = 28800")


def _table_exists(cur, table_name):
    cur.execute(
        """
        SELECT COUNT(*)
        FROM information_schema.tables
        WHERE table_schema = DATABASE()
            AND table_name = %s
        """,
        (table_name,)
    )
    row = cur.fetchone()
    return bool(row and row[0] > 0)


def _fetch_table_count(cur, table_name):
    cur.execute(f"SELECT COUNT(*) FROM {_quote_identifier(table_name)}")
    row = cur.fetchone()
    return row[0] if row else 0


def _acquire_refresh_lock(cur):
    cur.execute("SELECT GET_LOCK(%s, 0)", (CACHE_LOCK_NAME,))
    row = cur.fetchone()
    return row[0] if row else None


def _release_refresh_lock(cur):
    cur.execute("SELECT RELEASE_LOCK(%s)", (CACHE_LOCK_NAME,))


def _close_quietly(resource):
    try:
        if resource is not None:
            resource.close()
    except Exception:
        pass


def _refresh_eventos_historico_cache(mysql_impl):
    conn = None
    cur = None
    lock_acquired = False

    try:
        conn = _open_mysql_connection(mysql_impl)
        cur = _open_mysql_cursor(conn, mysql_impl)
        _execute_session_timeouts(cur)

        lock_result = _acquire_refresh_lock(cur)
        if lock_result != 1:
            raise CacheRefreshInProgress()
        lock_acquired = True

        source_view = _quote_identifier(SOURCE_VIEW)
        cache_table = _quote_identifier(CACHE_TABLE)
        cache_new_table = _quote_identifier(CACHE_NEW_TABLE)
        cache_old_table = _quote_identifier(CACHE_OLD_TABLE)

        cur.execute(f"DROP TABLE IF EXISTS {cache_new_table}")
        cur.execute(f"CREATE TABLE {cache_new_table} AS SELECT * FROM {source_view}")
        cur.execute(
            f"ALTER TABLE {cache_new_table} "
            "ADD COLUMN `__cache_id` BIGINT NOT NULL AUTO_INCREMENT PRIMARY KEY FIRST"
        )

        row_count = _fetch_table_count(cur, CACHE_NEW_TABLE)
        cache_exists = _table_exists(cur, CACHE_TABLE)

        cur.execute(f"DROP TABLE IF EXISTS {cache_old_table}")
        if cache_exists:
            cur.execute(
                f"RENAME TABLE {cache_table} TO {cache_old_table}, "
                f"{cache_new_table} TO {cache_table}"
            )
            cur.execute(f"DROP TABLE IF EXISTS {cache_old_table}")
        else:
            cur.execute(f"RENAME TABLE {cache_new_table} TO {cache_table}")

        if hasattr(conn, "commit"):
            conn.commit()

        return row_count
    except Exception:
        if conn is not None and hasattr(conn, "rollback"):
            try:
                conn.rollback()
            except Exception:
                pass
        raise
    finally:
        if lock_acquired and cur is not None:
            try:
                _release_refresh_lock(cur)
            except Exception:
                current_app.logger.exception("No se pudo liberar lock de cache de eventos historico")
        _close_quietly(cur)
        _close_quietly(conn)


def _fetch_eventos_historico_cache_page(mysql_impl, last_id, limit):
    conn = None
    cur = None

    try:
        conn = _open_mysql_connection(mysql_impl)
        cur = _open_mysql_cursor(conn, mysql_impl)
        sql = (
            f"SELECT * FROM {_quote_identifier(CACHE_TABLE)} "
            "WHERE `__cache_id` > %s "
            "ORDER BY `__cache_id` "
            "LIMIT %s"
        )
        cur.execute(sql, (last_id, limit))

        raw_columns = [d[0] for d in cur.description]
        cache_id_index = raw_columns.index("__cache_id")
        columns = [column for column in raw_columns if column != "__cache_id"]
        rows = cur.fetchall()

        data_rows = []
        next_last_id = last_id
        for row in rows:
            next_last_id = row[cache_id_index]
            data_rows.append([
                _format_value(value)
                for index, value in enumerate(row)
                if index != cache_id_index
            ])

        return {
            "limit": limit,
            "count": len(data_rows),
            "last_id": last_id,
            "next_last_id": next_last_id,
            "has_more": len(data_rows) == limit,
            "columns": columns,
            "rows": data_rows,
        }
    finally:
        _close_quietly(cur)
        _close_quietly(conn)


def _run_cache_refresh_background(app, mysql_impl):
    with app.app_context():
        try:
            row_count = _refresh_eventos_historico_cache(mysql_impl)
            current_app.logger.info(
                "Cache de eventos historico refrescada en background: %s filas",
                row_count
            )
        except CacheRefreshInProgress:
            current_app.logger.info("Refresh de cache de eventos historico ya esta en ejecucion")
        except Exception:
            current_app.logger.exception("Error refrescando cache de eventos historico en background")


def _start_cache_refresh_background(mysql_impl):
    app = current_app._get_current_object()
    thread = threading.Thread(
        target=_run_cache_refresh_background,
        args=(app, mysql_impl),
        daemon=True
    )
    thread.start()


def _get_eventos_historico_cache_status(mysql_impl):
    conn = None
    cur = None

    try:
        conn = _open_mysql_connection(mysql_impl)
        cur = _open_mysql_cursor(conn, mysql_impl)

        cur.execute("SELECT IS_FREE_LOCK(%s)", (CACHE_LOCK_NAME,))
        lock_row = cur.fetchone()
        lock_value = lock_row[0] if lock_row else None
        is_refreshing = lock_value == 0

        cache_exists = _table_exists(cur, CACHE_TABLE)
        row_count = None
        max_cache_id = None
        if cache_exists:
            cur.execute(
                f"SELECT COUNT(*), COALESCE(MAX(`__cache_id`), 0) "
                f"FROM {_quote_identifier(CACHE_TABLE)}"
            )
            cache_row = cur.fetchone()
            if cache_row:
                row_count = cache_row[0]
                max_cache_id = cache_row[1]

        return {
            "cache_table": CACHE_TABLE,
            "exists": cache_exists,
            "refreshing": is_refreshing,
            "rows": row_count,
            "max_cache_id": max_cache_id,
        }
    finally:
        _close_quietly(cur)
        _close_quietly(conn)


@eventos_historico_csv_bp.route("/api/admin/eventos_historico_cache/refresh", methods=["POST"])
def refresh_eventos_historico_cache():
    ok, msg = _validate_token()
    if not ok:
        return jsonify({"error": msg}), 401

    try:
        mysql_impl = _get_mysql_impl()
        status = _get_eventos_historico_cache_status(mysql_impl)
        if status["refreshing"]:
            return jsonify({
                "status": "refreshing",
                "message": "Refresh de cache ya en ejecucion",
                "cache": status
            }), 202

        _start_cache_refresh_background(mysql_impl)
        return jsonify({
            "status": "refreshing",
            "message": "Refresh de cache iniciado",
            "cache_table": CACHE_TABLE,
            "source_view": SOURCE_VIEW,
            "check_status_url": "/api/admin/eventos_historico_cache/status"
        }), 202
    except ImportError:
        current_app.logger.exception("No MySQL client library installed")
        return jsonify({"error": "No MySQL client library installed"}), 500
    except Exception as exc:
        current_app.logger.exception("Error refrescando cache de eventos historico")
        return jsonify({
            "error": "No se pudo iniciar el refresh de cache de eventos historico",
            "detail": str(exc)
        }), 500


@eventos_historico_csv_bp.route("/api/admin/eventos_historico_cache/status", methods=["GET"])
def get_eventos_historico_cache_status():
    ok, msg = _validate_token()
    if not ok:
        return jsonify({"error": msg}), 401

    try:
        mysql_impl = _get_mysql_impl()
        status = _get_eventos_historico_cache_status(mysql_impl)
        if status["refreshing"]:
            status["status"] = "refreshing"
        elif status["exists"]:
            status["status"] = "ready"
        else:
            status["status"] = "missing"
        return jsonify(status), 200
    except ImportError:
        current_app.logger.exception("No MySQL client library installed")
        return jsonify({"error": "No MySQL client library installed"}), 500
    except Exception as exc:
        current_app.logger.exception("Error consultando estado de cache de eventos historico")
        return jsonify({
            "error": "No se pudo consultar el estado de cache de eventos historico",
            "detail": str(exc)
        }), 500


@eventos_historico_csv_bp.route("/api/public/eventos_historico_json", methods=["GET"])
def eventos_historico_json():
    ok, msg = _validate_token()
    if not ok:
        return jsonify({"error": msg}), 401

    try:
        limit = _parse_int_arg("limit", 1000, minimum=1, maximum=MAX_JSON_LIMIT)
        last_id = _parse_int_arg("last_id", 0, minimum=0)
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400

    conn = None
    cur = None

    try:
        mysql_impl = _get_mysql_impl()
        conn = _open_mysql_connection(mysql_impl)
        cur = _open_mysql_cursor(conn, mysql_impl)

        # Mantener el orden natural del SELECT * (no inventar orden alfabético)
        sql = (
            f"SELECT * FROM {_quote_identifier(CACHE_TABLE)} "
            "WHERE `__cache_id` > %s "
            "ORDER BY `__cache_id` "
            "LIMIT %s"
        )
        cur.execute(sql, (last_id, limit))

        raw_columns = [d[0] for d in cur.description]
        cache_id_index = raw_columns.index("__cache_id")
        columns = [column for column in raw_columns if column != "__cache_id"]
        rows = cur.fetchall()

        data_rows = []
        next_last_id = last_id
        for row in rows:
            next_last_id = row[cache_id_index]
            data_rows.append([
                _format_value(value)
                for index, value in enumerate(row)
                if index != cache_id_index
            ])

        return jsonify({
            "limit": limit,
            "count": len(data_rows),
            "last_id": last_id,
            "next_last_id": next_last_id,
            "has_more": len(data_rows) == limit,
            "columns": columns,
            "rows": data_rows,
        })
    except ImportError:
        current_app.logger.exception("No MySQL client library installed")
        return jsonify({"error": "No MySQL client library installed"}), 500
    except Exception as exc:
        if _is_missing_table_error(exc):
            return jsonify({
                "error": "Cache de eventos historico no disponible",
                "detail": "Ejecute primero POST /api/admin/eventos_historico_cache/refresh."
            }), 503
        current_app.logger.exception("Error consultando cache de eventos historico")
        return jsonify({
            "error": "No se pudo consultar la cache de eventos historico",
            "detail": str(exc)
        }), 500
    finally:
        _close_quietly(cur)
        _close_quietly(conn)


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
            cursor = _open_mysql_cursor(conn, mysql_impl, unbuffered=True)
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
