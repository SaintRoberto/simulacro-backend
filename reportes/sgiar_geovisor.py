from datetime import datetime

from flask import Blueprint, current_app, jsonify, request

from reportes.eventos_lluvias_json import (
    _close_quietly,
    _format_value,
    _get_mysql_impl,
    _open_mysql_connection,
    _open_mysql_cursor,
    _validate_api_key,
)


sgiar_geovisor_bp = Blueprint("sgiar_geovisor", __name__)

SOURCE_SCHEMA = "dmeva"
SOURCE_PROCEDURE = "spSGIAR-GeoVisor-2026"
DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"
DEFAULT_LIMIT = 5000
MAX_LIMIT = 10000


def _parse_datetime_field(payload, name):
    value = payload.get(name, "")
    if not isinstance(value, str):
        raise ValueError(f"{name} debe ser texto")
    value = value.strip()
    if not value:
        raise ValueError(f"El parametro {name} es requerido")

    try:
        return datetime.strptime(value, DATETIME_FORMAT), value
    except ValueError as exc:
        raise ValueError(
            f"{name} debe tener el formato YYYY-MM-DD HH:MM:SS"
        ) from exc


def _parse_positive_int_field(payload, name, default, maximum=None):
    try:
        value = int(payload.get(name, default))
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{name} debe ser numerico") from exc

    if value < 1:
        raise ValueError(f"{name} debe ser mayor o igual a 1")
    if maximum is not None and value > maximum:
        raise ValueError(f"{name} no puede ser mayor a {maximum}")
    return value


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


@sgiar_geovisor_bp.route(
    "/api/public/get_geoJson_sgiar_geovisor_2026",
    methods=["POST"],
)
def get_geojson_sgiar_geovisor_2026():
    """Consulta el GeoVisor SGIAR 2026 por rango de fechas.
    ---
    tags:
      - Reportes Publicos
    summary: Consultar GeoVisor SGIAR 2026 por rango de fechas
    produces:
      - application/geo+json
    security: []
    parameters:
      - in: query
        name: api_key
        type: string
        required: true
      - in: body
        name: body
        required: true
        schema:
          type: object
          required:
            - fecha_inicio
            - fecha_fin
          properties:
            fecha_inicio:
              type: string
              example: "2026-08-29 00:00:00"
            fecha_fin:
              type: string
              example: "2026-10-30 23:59:59"
            page:
              type: integer
              default: 1
            limit:
              type: integer
              default: 5000
              maximum: 10000
    responses:
      200:
        description: FeatureCollection consultada correctamente
      400:
        description: Parametros invalidos
      401:
        description: API key ausente o invalida
      500:
        description: Error consultando el procedimiento almacenado
    """
    ok, message = _validate_api_key()
    if not ok:
        return jsonify({"error": message}), 401

    try:
        payload = request.get_json(silent=True)
        if not isinstance(payload, dict):
            raise ValueError("El cuerpo debe ser un objeto JSON")

        start_datetime, start_value = _parse_datetime_field(
            payload, "fecha_inicio"
        )
        end_datetime, end_value = _parse_datetime_field(payload, "fecha_fin")
        if start_datetime > end_datetime:
            raise ValueError("fecha_inicio no puede ser mayor a fecha_fin")

        page = _parse_positive_int_field(payload, "page", 1)
        limit = _parse_positive_int_field(
            payload, "limit", DEFAULT_LIMIT, MAX_LIMIT
        )
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400

    conn = None
    cursor = None
    try:
        mysql_impl = _get_mysql_impl()
        conn = _open_mysql_connection(mysql_impl)
        cursor = _open_mysql_cursor(conn, mysql_impl)
        cursor.execute(
            f"CALL `{SOURCE_SCHEMA}`.`{SOURCE_PROCEDURE}`(%s, %s)",
            (start_value, end_value),
        )

        columns = [description[0] for description in cursor.description]
        all_rows = cursor.fetchall()
        offset = (page - 1) * limit
        rows = all_rows[offset:offset + limit]

        latitude_column = _find_column(columns, "latitud")
        longitude_column = _find_column(columns, "longitud")

        features = []
        for row in rows:
            latitude = (
                _to_coordinate(row.get(latitude_column))
                if latitude_column is not None
                else None
            )
            longitude = (
                _to_coordinate(row.get(longitude_column))
                if longitude_column is not None
                else None
            )
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

        response = jsonify({
            "type": "FeatureCollection",
            "features": features,
            "metadata": {
                "fecha_inicio": start_value,
                "fecha_fin": end_value,
                "page": page,
                "limit": limit,
                "count": len(features),
                "total": len(all_rows),
                "has_more": offset + len(features) < len(all_rows),
                "latitude_column": latitude_column,
                "longitude_column": longitude_column,
            },
        })
        response.mimetype = "application/geo+json"
        return response
    except ImportError:
        return jsonify({"error": "No MySQL client library installed"}), 500
    except Exception as exc:
        current_app.logger.exception("Error consultando SGIAR GeoVisor 2026")
        return jsonify({
            "error": "No se pudo consultar el procedimiento SGIAR GeoVisor 2026",
            "detail": str(exc),
        }), 500
    finally:
        _close_quietly(cursor)
        _close_quietly(conn)
