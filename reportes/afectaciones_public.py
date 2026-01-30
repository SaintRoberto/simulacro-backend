import os
from flask import Blueprint, jsonify, request
from models import db
from config import PUBLIC_API_KEYS as CONFIG_PUBLIC_API_KEYS

afectaciones_public_bp = Blueprint('afectaciones_public', __name__)


def _validate_api_key():
    keys_env = os.environ.get('PUBLIC_API_KEYS') or CONFIG_PUBLIC_API_KEYS or ''
    allowed = [k.strip() for k in keys_env.split(',') if k.strip()]
    provided = request.headers.get('X-API-Key') or request.args.get('api_key')
    if not allowed:
        return False, 'Server misconfiguration: PUBLIC_API_KEYS not set'
    if not provided:
        return False, 'API key required (header X-API-Key or query param api_key)'
    if provided not in allowed:
        return False, 'Invalid API key'
    return True, None


@afectaciones_public_bp.route('/api/public/afectaciones_version1', methods=['GET'])
def get_afectaciones_version1():
    """Public endpoint (secured by API key): devuelve todos los registros de la vista afectaciones_version1"""
    ok, msg = _validate_api_key()
    if not ok:
        return jsonify({'error': msg}), 401

    result = db.session.execute(db.text("SELECT * FROM afectaciones_version1"))
    registros = []
    for row in result:
        try:
            mapping = row._mapping
        except Exception:
            mapping = dict(row)
        record = {}
        for k, v in mapping.items():
            if hasattr(v, 'isoformat'):
                try:
                    record[k] = v.isoformat()
                except Exception:
                    record[k] = v
            else:
                record[k] = v
        registros.append(record)
    return jsonify(registros)


@afectaciones_public_bp.route('/api/public/localidad_eventos/<int:emergencia_id>', methods=['GET'])
def get_localidad_eventos_by_emergencia(emergencia_id):
    """Public endpoint (secured by API key): devuelve los registros de la vista
    vw_localidad_eventos asociados a una emergencia dada por su ID.
    """
    ok, msg = _validate_api_key()
    if not ok:
        return jsonify({'error': msg}), 401

    query = db.text("SELECT * FROM vw_localidad_eventos WHERE emergencia_id = :emergencia_id")
    result = db.session.execute(query, {'emergencia_id': emergencia_id})

    registros = []
    for row in result:
        try:
            mapping = row._mapping
        except Exception:
            mapping = dict(row)
        record = {}
        for k, v in mapping.items():
            if hasattr(v, 'isoformat'):
                try:
                    record[k] = v.isoformat()
                except Exception:
                    record[k] = v
            else:
                record[k] = v
        registros.append(record)

    return jsonify(registros)


@afectaciones_public_bp.route('/api/public/acciones_respuesta/<int:emergencia_id>', methods=['GET'])
def get_acciones_respuesta_by_emergencia(emergencia_id):
    """Public endpoint (secured by API key): devuelve las acciones de respuesta y
    sus actividades asociadas para una emergencia dada.

    La información proviene de las tablas acciones_respuesta, actividades_ejecucion
    y tablas relacionadas, filtrando por emergencia_id.

    ---
    tags:
      - Reportes Publicos
    parameters:
      - name: emergencia_id
        in: path
        type: integer
        required: true
    responses:
      200:
        description: Lista de acciones de respuesta y sus actividades asociadas
        schema:
          type: array
          items:
            type: object
            properties:
              emergencia_id: {type: integer}
              resolucion_origen: {type: integer, description: "ID de la resolución origen (coe_acta_resolucion_mesa_id)"}
              usuario_id: {type: integer}
              origen: {type: string, description: "Gestión Propia o Por Resolución"}
              detalle_accion: {type: string}
              accion_respuesta_estado_id: {type: integer}
              estado: {type: string}
              fecha_final: {type: string, format: date-time}
              nombre: {type: string, description: "Nombre de la institución ejecutora"}
              fecha_inicio: {type: string, format: date-time}
              porcentaje_avance_id: {type: integer}
              instituciones_apoyo: {type: string}
              ubicaciones_atendidas: {type: string}
              actividad_fecha_final: {type: string, format: date-time}
              actividad_ejecucion_estado_id: {type: integer}
              detalle_actividad: {type: string}
      401:
        description: API key inválida o ausente
    """
    ok, msg = _validate_api_key()
    if not ok:
        return jsonify({'error': msg}), 401

    query = db.text("""
        SELECT a.emergencia_id,
               a.coe_acta_resolucion_mesa_id AS resolucion_origen,
               a.usuario_id,
               CASE a.accion_respuesta_origen_id
                   WHEN 0 THEN 'Gestión Propia'
                   ELSE 'Por Resolución'
               END AS origen,
               a.detalle AS detalle_accion,
               a.accion_respuesta_estado_id,
               e.nombre AS estado,
               a.fecha_final,
               i.nombre,
               ae.fecha_inicio,
               ae.porcentaje_avance_id,
               ae.instituciones_apoyo,
               ae.ubicaciones_atendidas,
               ae.fecha_final,
               ae.actividad_ejecucion_estado_id,
               ae.detalle AS detalle_actividad
        FROM public.acciones_respuesta a
        INNER JOIN public.accion_respuesta_estados e ON a.accion_respuesta_estado_id = e.id
        LEFT JOIN public.actividades_ejecucion ae ON a.id = ae.accion_respuesta_id
        LEFT JOIN public.actividad_ejecucion_funciones f ON ae.actividad_ejecucion_funcion_id = f.id
        LEFT JOIN public.instituciones i ON ae.institucion_ejecutora_id = i.id
        WHERE a.emergencia_id = :emergencia_id
    """)

    result = db.session.execute(query, {'emergencia_id': emergencia_id})

    registros = []
    for row in result:
        try:
            mapping = row._mapping
        except Exception:
            mapping = dict(row)
        record = {}
        for k, v in mapping.items():
            if hasattr(v, 'isoformat'):
                try:
                    record[k] = v.isoformat()
                except Exception:
                    record[k] = v
            else:
                record[k] = v
        registros.append(record)

    return jsonify(registros)


@afectaciones_public_bp.route('/api/public/alojamientos/<int:emergencia_id>', methods=['GET'])
def get_alojamientos_by_emergencia(emergencia_id):
    """Public endpoint (secured by API key): devuelve los registros de la vista
    vw_alojamientos asociados a una emergencia dada por su ID.
    """
    ok, msg = _validate_api_key()
    if not ok:
        return jsonify({'error': msg}), 401

    query = db.text("SELECT * FROM vw_alojamientos WHERE emergencia_id = :emergencia_id")
    result = db.session.execute(query, {'emergencia_id': emergencia_id})

    registros = []
    for row in result:
        try:
            mapping = row._mapping
        except Exception:
            mapping = dict(row)
        record = {}
        for k, v in mapping.items():
            if hasattr(v, 'isoformat'):
                try:
                    record[k] = v.isoformat()
                except Exception:
                    record[k] = v
            else:
                record[k] = v
        registros.append(record)

    return jsonify(registros)


@afectaciones_public_bp.route('/api/public/requerimientos/<int:emergencia_id>', methods=['GET'])
def get__requerimietnos_by_emergencia(emergencia_id):
    """Public endpoint (secured by API key): devuelve los registros de la vista
    vw_requerimientos asociados a una emergencia dada por su ID.
    """
    ok, msg = _validate_api_key()
    if not ok:
        return jsonify({'error': msg}), 401

    query = db.text("SELECT * FROM vw_requerimientos WHERE emergencia_id = :emergencia_id")
    result = db.session.execute(query, {'emergencia_id': emergencia_id})

    registros = []
    for row in result:
        try:
            mapping = row._mapping
        except Exception:
            mapping = dict(row)
        record = {}
        for k, v in mapping.items():
            if hasattr(v, 'isoformat'):
                try:
                    record[k] = v.isoformat()
                except Exception:
                    record[k] = v
            else:
                record[k] = v
        registros.append(record)

    return jsonify(registros)


@afectaciones_public_bp.route('/api/public/afectaciones_version1/<int:registro_id>', methods=['GET'])
def get_afectacion_version1_by_id(registro_id):
    """Public endpoint (secured by API key): devuelve un registro por id de la vista afectaciones_version1"""
    ok, msg = _validate_api_key()
    if not ok:
        return jsonify({'error': msg}), 401

    result = db.session.execute(db.text("SELECT * FROM afectaciones_version1 WHERE id = :id"), {'id': registro_id})
    row = result.fetchone()
    if not row:
        return jsonify({'error': 'Registro no encontrado'}), 404
    try:
        mapping = row._mapping
    except Exception:
        mapping = dict(row)
    record = {}
    for k, v in mapping.items():
        if hasattr(v, 'isoformat'):
            try:
                record[k] = v.isoformat()
            except Exception:
                record[k] = v
        else:
            record[k] = v
    return jsonify(record)


@afectaciones_public_bp.route('/api/public/afectacion_infraestructura/<int:emergencia_id>', methods=['GET'])
def get_afectacion_infraestructura_by_emergencia(emergencia_id):
    """Public endpoint (secured by API key): devuelve los registros de la vista
    vw_afectacion_infraestructura asociados a una emergencia dada por su ID.
    """
    ok, msg = _validate_api_key()
    if not ok:
        return jsonify({'error': msg}), 401

    query = db.text("SELECT * FROM vw_afectacion_infraestructura WHERE emergencia_id = :emergencia_id")
    result = db.session.execute(query, {'emergencia_id': emergencia_id})

    registros = []
    for row in result:
        try:
            mapping = row._mapping
        except Exception:
            mapping = dict(row)
        record = {}
        for k, v in mapping.items():
            if hasattr(v, 'isoformat'):
                try:
                    record[k] = v.isoformat()
                except Exception:
                    record[k] = v
            else:
                record[k] = v
        registros.append(record)

    return jsonify(registros)
