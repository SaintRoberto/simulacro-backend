import os
import threading
from datetime import date, datetime

from flask import Blueprint, current_app, jsonify, request

import config as app_config
from config import MYSQL_DB, MYSQL_HOST, MYSQL_PASS, MYSQL_PORT, MYSQL_USER

asistencia_humanitaria_bp = Blueprint("asistencia_humanitaria_json", __name__)

SOURCE_VIEW = "3. RED-M-2026-Asistencia Humanitaria 2026+"
CACHE_TABLE = "asistencia_humanitaria_json_cache"
CACHE_NEW_TABLE = "asistencia_humanitaria_json_cache_new"
CACHE_OLD_TABLE = "asistencia_humanitaria_json_cache_old"
CACHE_LOCK_NAME = "asistencia_humanitaria_json_cache_refresh"
MAX_JSON_LIMIT = 5000


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
            read_timeout=1800,
            write_timeout=1800,
        )

    connect_kwargs = {
        "host": MYSQL_HOST,
        "user": MYSQL_USER,
        "password": MYSQL_PASS,
        "database": MYSQL_DB,
        "port": MYSQL_PORT,
        "connection_timeout": 15,
        "read_timeout": 1800,
        "write_timeout": 1800,
        "charset": "utf8mb4",
    }
    try:
        return impl.connect(**connect_kwargs)
    except TypeError:
        connect_kwargs.pop("read_timeout", None)
        connect_kwargs.pop("write_timeout", None)
        return impl.connect(**connect_kwargs)


def _open_mysql_cursor(conn, mysql_impl):
    impl_name, _ = mysql_impl
    if impl_name == "mysql-connector":
        return conn.cursor(buffered=True)
    return conn.cursor()


def _format_value(value):
    if value is None:
        return ""
    if isinstance(value, datetime):
        return value.strftime("%Y-%m-%d %H:%M:%S")
    if isinstance(value, date):
        return value.strftime("%Y-%m-%d")
    return value


def _validate_token():
    configured = os.environ.get("asistencia_humanitaria_TOKEN")
    if configured is None:
        configured = getattr(app_config, "asistencia_humanitaria_TOKEN", None)
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
    cur.execute("SET SESSION net_read_timeout = 1800")
    cur.execute("SET SESSION net_write_timeout = 1800")
    cur.execute("SET SESSION wait_timeout = 28800")


def _table_exists(cur, table_name):
    cur.execute(
        """
        SELECT COUNT(*)
        FROM information_schema.tables
        WHERE table_schema = DATABASE()
            AND table_name = %s
        """,
        (table_name,),
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


def _refresh_cache(mysql_impl):
    conn = None
    cur = None
    lock_acquired = False

    try:
        conn = _open_mysql_connection(mysql_impl)
        cur = _open_mysql_cursor(conn, mysql_impl)
        _execute_session_timeouts(cur)

        if _acquire_refresh_lock(cur) != 1:
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
                current_app.logger.exception(
                    "No se pudo liberar lock de cache de asistencia humanitaria"
                )
        _close_quietly(cur)
        _close_quietly(conn)


def _run_cache_refresh_background(app, mysql_impl):
    with app.app_context():
        try:
            row_count = _refresh_cache(mysql_impl)
            current_app.logger.info(
                "Cache de asistencia humanitaria refrescada: %s filas", row_count
            )
        except CacheRefreshInProgress:
            current_app.logger.info(
                "Refresh de cache de asistencia humanitaria ya esta en ejecucion"
            )
        except Exception:
            current_app.logger.exception(
                "Error refrescando cache de asistencia humanitaria"
            )


def _start_cache_refresh_background(mysql_impl):
    app = current_app._get_current_object()
    thread = threading.Thread(
        target=_run_cache_refresh_background,
        args=(app, mysql_impl),
        daemon=True,
    )
    thread.start()


def _get_cache_status(mysql_impl):
    conn = None
    cur = None
    try:
        conn = _open_mysql_connection(mysql_impl)
        cur = _open_mysql_cursor(conn, mysql_impl)
        cur.execute("SELECT IS_FREE_LOCK(%s)", (CACHE_LOCK_NAME,))
        lock_row = cur.fetchone()
        refreshing = bool(lock_row and lock_row[0] == 0)

        exists = _table_exists(cur, CACHE_TABLE)
        row_count = None
        if exists:
            row_count = _fetch_table_count(cur, CACHE_TABLE)

        return {
            "cache_table": CACHE_TABLE,
            "source_view": SOURCE_VIEW,
            "exists": exists,
            "refreshing": refreshing,
            "rows": row_count,
        }
    finally:
        _close_quietly(cur)
        _close_quietly(conn)


@asistencia_humanitaria_bp.route(
    "/api/admin/asistencia_humanitaria_cache/refresh", methods=["POST"]
)
def refresh_asistencia_humanitaria_cache():
    ok, msg = _validate_token()
    if not ok:
        return jsonify({"error": msg}), 401

    try:
        mysql_impl = _get_mysql_impl()
        status = _get_cache_status(mysql_impl)
        if status["refreshing"]:
            return jsonify({
                "status": "refreshing",
                "message": "Refresh de cache ya en ejecucion",
                "cache": status,
            }), 202

        _start_cache_refresh_background(mysql_impl)
        return jsonify({
            "status": "refreshing",
            "message": "Refresh de cache iniciado",
            "cache_table": CACHE_TABLE,
            "source_view": SOURCE_VIEW,
            "check_status_url": "/api/admin/asistencia_humanitaria_cache/status",
        }), 202
    except Exception as exc:
        current_app.logger.exception(
            "No se pudo iniciar el refresh de asistencia humanitaria"
        )
        return jsonify({
            "error": "No se pudo iniciar el refresh de cache",
            "detail": str(exc),
        }), 500


@asistencia_humanitaria_bp.route(
    "/api/admin/asistencia_humanitaria_cache/status", methods=["GET"]
)
def get_asistencia_humanitaria_cache_status():
    ok, msg = _validate_token()
    if not ok:
        return jsonify({"error": msg}), 401

    try:
        status = _get_cache_status(_get_mysql_impl())
        if status["refreshing"]:
            status["status"] = "refreshing"
        elif status["exists"]:
            status["status"] = "ready"
        else:
            status["status"] = "missing"
        return jsonify(status)
    except Exception as exc:
        current_app.logger.exception(
            "No se pudo consultar el estado de cache de asistencia humanitaria"
        )
        return jsonify({
            "error": "No se pudo consultar el estado de cache",
            "detail": str(exc),
        }), 500


@asistencia_humanitaria_bp.route(
    "/api/public/asistencia_humanitaria_json", methods=["GET"]
)
def asistencia_humanitaria_json():
    ok, msg = _validate_token()
    if not ok:
        return jsonify({"error": msg}), 401

    try:
        page = _parse_int_arg("page", 1, minimum=1)
        limit = _parse_int_arg(
            "limit", MAX_JSON_LIMIT, minimum=1, maximum=MAX_JSON_LIMIT
        )
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400

    offset = (page - 1) * limit
    conn = None
    cur = None

    try:
        mysql_impl = _get_mysql_impl()
        conn = _open_mysql_connection(mysql_impl)
        cur = _open_mysql_cursor(conn, mysql_impl)
        cur.execute(
            f"SELECT * FROM {_quote_identifier(CACHE_TABLE)} "
            "ORDER BY `__cache_id` LIMIT %s OFFSET %s",
            (limit, offset),
        )

        raw_columns = [description[0] for description in cur.description]
        cache_id_index = raw_columns.index("__cache_id")
        columns = [column for column in raw_columns if column != "__cache_id"]
        rows = cur.fetchall()
        data_rows = [
            [
                _format_value(value)
                for index, value in enumerate(row)
                if index != cache_id_index
            ]
            for row in rows
        ]

        return jsonify({
            "page": page,
            "limit": limit,
            "count": len(data_rows),
            "columns": columns,
            "rows": data_rows,
        })
    except Exception as exc:
        if _is_missing_table_error(exc):
            _start_cache_refresh_background(_get_mysql_impl())
            return jsonify({
                "status": "initializing",
                "message": "La cache se esta construyendo en segundo plano",
                "check_status_url": "/api/admin/asistencia_humanitaria_cache/status",
            }), 202
        current_app.logger.exception(
            "Error consultando cache de asistencia humanitaria"
        )
        return jsonify({
            "error": "No se pudo consultar la cache de asistencia humanitaria",
            "detail": str(exc),
        }), 500
    finally:
        _close_quietly(cur)
        _close_quietly(conn)
