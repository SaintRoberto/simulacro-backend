from decimal import Decimal, InvalidOperation

from flask import Blueprint, current_app, jsonify, request

from reportes.eventos_lluvias_json import (
    MAX_JSON_LIMIT,
    SOURCE_PROCEDURE,
    SOURCE_SCHEMA,
    START_DATETIME,
    _close_quietly,
    _current_cutoff,
    _format_value,
    _get_mysql_impl,
    _open_mysql_connection,
    _open_mysql_cursor,
    _parse_int_arg,
    _validate_api_key,
)


eventos_lluvias_geojson_bp = Blueprint("eventos_lluvias_geojson", __name__)

BENEFICIARIES_COLUMN = "Personas Beneficiadas AH"


def _find_column(columns, expected_name):
    expected_name = expected_name.casefold()
    return next(
        (column for column in columns if column.casefold() == expected_name),
        None,
    )


def _to_coordinate(value):
    if value is None or isinstance(value, bool):
        return None

    try:
        if isinstance(value, str):
            value = value.strip().replace(",", ".")
            if not value:
                return None
        return float(value)
    except (TypeError, ValueError):
        return None


def _sum_beneficiaries(rows, column):
    total = Decimal("0")
    for row in rows:
        value = row.get(column)
        if value is None or value == "":
            continue
        try:
            if isinstance(value, str):
                value = value.strip().replace(",", ".")
            total += Decimal(str(value))
        except (InvalidOperation, TypeError, ValueError):
            continue

    if total == total.to_integral_value():
        return int(total)
    return float(total)


@eventos_lluvias_geojson_bp.route(
    "/api/public/eventos_lluvias_geojson",
    methods=["GET"],
)
def eventos_lluvias_geojson():
    """Consulta paginada de eventos por lluvias en formato GeoJSON.
    ---
    tags:
      - Reportes Publicos
    summary: Consultar eventos por lluvias en formato GeoJSON
    produces:
      - application/geo+json
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
        description: FeatureCollection consultada correctamente
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
        latitude_column = _find_column(columns, "latitud")
        longitude_column = _find_column(columns, "longitud")
        beneficiaries_column = _find_column(columns, BENEFICIARIES_COLUMN)

        if latitude_column is None or longitude_column is None:
            return jsonify({
                "error": (
                    "El procedimiento no devolvio las columnas "
                    "'latitud' y 'longitud'"
                ),
                "columns": columns,
            }), 500

        features = []
        for row in rows:
            latitude = _to_coordinate(row.get(latitude_column))
            longitude = _to_coordinate(row.get(longitude_column))
            geometry = None
            if latitude is not None and longitude is not None:
                geometry = {
                    "type": "Point",
                    "coordinates": [longitude, latitude],
                }

            features.append({
                "type": "Feature",
                "geometry": geometry,
                "properties": {
                    column: _format_value(row.get(column))
                    for column in columns
                },
            })

        next_last_id = last_id + len(features)
        total_beneficiaries = (
            _sum_beneficiaries(all_rows, beneficiaries_column)
            if beneficiaries_column is not None
            else 0
        )
        response = jsonify({
            "type": "FeatureCollection",
            "features": features,
            "metadata": {
                "limit": limit,
                "count": len(features),
                "last_id": last_id,
                "next_last_id": next_last_id,
                "has_more": next_last_id < len(all_rows),
                "latitude_column": latitude_column,
                "longitude_column": longitude_column,
                "total_beneficiarios": total_beneficiaries,
            },
        })
        response.mimetype = "application/geo+json"
        return response
    except ImportError:
        return jsonify({"error": "No MySQL client library installed"}), 500
    except Exception as exc:
        current_app.logger.exception(
            "Error consultando eventos por lluvias en formato GeoJSON"
        )
        return jsonify({
            "error": (
                "No se pudo consultar el procedimiento de eventos por lluvias"
            ),
            "detail": str(exc),
        }), 500
    finally:
        _close_quietly(cursor)
        _close_quietly(conn)
