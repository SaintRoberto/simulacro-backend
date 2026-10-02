from datetime import date, datetime, time, timedelta, timezone
from decimal import Decimal

from flask import Blueprint, jsonify, request

from auth import decode_token
from config import MYSQL_DB, MYSQL_HOST, MYSQL_PASS, MYSQL_PORT, MYSQL_USER


eventos_lluvias_bp = Blueprint("eventos_lluvias", __name__)


EVENTOS_LLUVIA_FILTERED_SQL = (
    "CALL `ws2026prc-EventosLluvias`(%s, %s)"
)
DEFAULT_FECHA_INI = date(2026, 8, 29)
ECUADOR_TIMEZONE = timezone(timedelta(hours=-5))


def _get_mysql_impl():
    try:
        import pymysql  # type: ignore

        return ("pymysql", pymysql)
    except Exception:
        pass

    try:
        import mysql.connector  # type: ignore

        return ("mysql-connector", mysql.connector)
    except Exception as exc:  # pragma: no cover - depende del entorno de ejecucion
        raise ImportError("No MySQL client library installed") from exc


def _open_mysql_connection(mysql_impl):
    impl_name, impl = mysql_impl
    if impl_name == "pymysql":
        return impl.connect(
            host=MYSQL_HOST,
            user=MYSQL_USER,
            password=MYSQL_PASS,
            database=MYSQL_DB,
            port=MYSQL_PORT,
            charset="utf8mb4",
            cursorclass=impl.cursors.DictCursor,
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
        return conn.cursor(dictionary=True)
    return conn.cursor()


def _json_value(value):
    if isinstance(value, (datetime, date, time)):
        return value.isoformat()
    if isinstance(value, Decimal):
        return str(value)
    if isinstance(value, bytes):
        return value.decode("utf-8", errors="replace")
    return value


def _parse_optional_date(data, field_name):
    value = data.get(field_name)
    if value is None or value == "":
        return None
    if not isinstance(value, str):
        raise ValueError(f"{field_name} debe tener formato YYYY-MM-DD")
    try:
        parsed_value = date.fromisoformat(value)
    except ValueError as exc:
        raise ValueError(f"{field_name} debe tener formato YYYY-MM-DD") from exc
    if parsed_value.isoformat() != value:
        raise ValueError(f"{field_name} debe tener formato YYYY-MM-DD")
    return parsed_value


@eventos_lluvias_bp.route("/api/public/eventos_lluvias", methods=["POST"])
def get_eventos_lluvias():
    """Consulta los eventos de lluvias.
    ---
    tags:
      - Reportes Publicos
    summary: Consultar eventos de lluvias
    description: >
      Valida el JWT generado por /api/usuarios/login y devuelve los datos
      del procedimiento ws2026prc-EventosLluvias; los limites de fecha son
      inclusivos.
    consumes:
      - application/json
    produces:
      - application/json
    security: []
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          required:
            - token
          properties:
            token:
              type: string
              description: JWT generado por el endpoint de login
              example: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
            fecha_ini:
              type: string
              format: date
              description: Fecha inicial opcional (YYYY-MM-DD). Si no se envian fechas, se usa 2026-08-29.
              example: "2026-09-01"
            fecha_fin:
              type: string
              format: date
              description: Fecha final opcional (YYYY-MM-DD). Si no se envian fechas, se usa la fecha actual.
              example: "2026-09-30"
    responses:
      200:
        description: Datos consultados correctamente
        schema:
          type: object
          properties:
            success:
              type: boolean
              example: true
            count:
              type: integer
              example: 24
            data:
              type: array
              items:
                type: object
      401:
        description: Token ausente, invalido o expirado
      400:
        description: Formato o rango de fechas invalido
    """
    data = request.get_json(silent=True)
    if (
        not isinstance(data, dict)
        or not isinstance(data.get("token"), str)
        or not data["token"].strip()
    ):
        return jsonify({"error": "Token requerido"}), 401

    if not decode_token(data["token"].strip()):
        return jsonify({"error": "Token invalido o expirado"}), 401

    try:
        fecha_ini = _parse_optional_date(data, "fecha_ini")
        fecha_fin = _parse_optional_date(data, "fecha_fin")
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400

    if fecha_ini is None and fecha_fin is None:
        fecha_ini = DEFAULT_FECHA_INI
        fecha_fin = datetime.now(ECUADOR_TIMEZONE).date()

    if fecha_ini is not None and fecha_fin is not None and fecha_ini > fecha_fin:
        return jsonify({
            "error": "fecha_ini no puede ser posterior a fecha_fin"
        }), 400

    mysql_impl = _get_mysql_impl()
    conn = _open_mysql_connection(mysql_impl)
    cursor = _open_mysql_cursor(conn, mysql_impl)

    try:
        cursor.execute(
            EVENTOS_LLUVIA_FILTERED_SQL,
            (fecha_ini, fecha_fin),
        )
        rows = cursor.fetchall()
        while cursor.nextset():
            pass
        registros = [
            {key: _json_value(value) for key, value in row.items()}
            for row in rows
        ]
        return jsonify({
            "success": True,
            "count": len(registros),
            "data": registros,
        })
    finally:
        cursor.close()
        conn.close()
