from flask import request, jsonify
from actividades_ejecucion import actividades_ejecucion_bp
from models import db
from datetime import datetime, timezone

def _row_to_dict(row):
    try:
        mapping = dict(row._mapping)  # SQLAlchemy Row
    except Exception:
        mapping = {k: getattr(row, k) for k in row.keys()}
    for k, v in list(mapping.items()):
        if isinstance(v, datetime):
            mapping[k] = v.isoformat()
    return mapping

@actividades_ejecucion_bp.route('/api/actividades_ejecucion', methods=['GET'])
def get_actividades_ejecucion():
    """Listar actividades de ejecución
    ---
    tags:
      - Actividades Ejecucion
    responses:
      200:
        description: Lista de actividades de ejecución
        schema:
          type: array
          items:
            type: object
            properties:
              id: {type: integer}
              accion_respuesta_id: {type: integer}
              ejecucion_actividad_id: {type: integer}
              institucion_ejecutora_id: {type: integer}
              porcentaje_avance_id: {type: integer}
              detalle: {type: string}
              actividad_ejecucion_estado_id: {type: integer}
              fecha_inicio: {type: string}
              fecha_final: {type: string}
              activo: {type: boolean}
              creador: {type: string}
              creacion: {type: string}
              modificador: {type: string}
              modificacion: {type: string}
    """
    result = db.session.execute(db.text("SELECT * FROM actividades_ejecucion"))
    items = []
    for row in result:
        items.append({
            'id': row.id,
            'accion_respuesta_id': row.accion_respuesta_id,
            'ejecucion_actividad_id': row.ejecucion_actividad_id,
            'institucion_ejecutora_id': row.institucion_ejecutora_id,
            'porcentaje_avance_id': row.porcentaje_avance_id,
            'detalle': row.detalle,
            'actividad_ejecucion_estado_id': row.actividad_ejecucion_estado_id,
            'fecha_inicio': row.fecha_inicio.isoformat() if row.fecha_inicio else None,
            'fecha_final': row.fecha_final.isoformat() if row.fecha_final else None,
            'activo': row.activo,
            'creador': row.creador,
            'creacion': row.creacion.isoformat() if row.creacion else None,
            'modificador': row.modificador,
            'modificacion': row.modificacion.isoformat() if row.modificacion else None
        })
    return jsonify(items)

@actividades_ejecucion_bp.route('/api/actividades_ejecucion/accion_respuesta/<int:accion_respuesta_id>', methods=['GET'])
def get_actividades_ejecucion_by_accion_respuesta(accion_respuesta_id):
    """Listar actividades de ejecución por accion_respuesta_id
    ---
    tags:
      - Actividades Ejecucion
    parameters:
      - name: accion_respuesta_id
        in: path
        type: integer
        required: true
    responses:
      200:
        description: Lista de actividades para la acción de respuesta
        schema:
          type: array
          items:
            type: object
            properties:
              actividad_ejecucion_id: {type: integer}
              accion_respuesta_id: {type: integer}
              ejecucion_actividad_id: {type: integer}
              ejecucion_actividad_nombre: {type: string}
              institucion_ejecutora_id: {type: integer}
              institucion_ejecutora_nombre: {type: string}
              institucion_ejecutora_siglas: {type: string}
              porcentaje_avance_id: {type: integer}
              actividad_ejecucion_avance: {type: string}
              detalle: {type: string}
              fecha_inicio: {type: string}
              fecha_final: {type: string}
              actividad_ejecucion_estado_id: {type: integer}
              actividad_ejecucion_estado: {type: string}
    """
    query = db.text("""
        SELECT d.id actividad_ejecucion_id, d.accion_respuesta_id,
               d.ejecucion_actividad_id, x.nombre ejecucion_actividad_nombre,
               d.institucion_ejecutora_id, i.nombre institucion_ejecutora_nombre, i.siglas institucion_ejecutora_siglas,
               d.porcentaje_avance_id, a.nombre actividad_ejecucion_avance,
               d.detalle, d.fecha_inicio, d.fecha_final,
               d.actividad_ejecucion_estado_id, e.nombre actividad_ejecucion_estado
        FROM public.actividades_ejecucion d
        INNER JOIN public.instituciones i ON d.institucion_ejecutora_id = i.id
        INNER JOIN public.ejecucion_actividades x ON d.ejecucion_actividad_id = x.id
        INNER JOIN public.accion_respuesta_estados e ON d.actividad_ejecucion_estado_id = e.id
        INNER JOIN public.respuesta_avances a ON d.porcentaje_avance_id = a.id
        WHERE d.accion_respuesta_id = :accion_respuesta_id
        ORDER BY d.id ASC
    """)
    result = db.session.execute(query, {'accion_respuesta_id': accion_respuesta_id})
    items = []
    for row in result:
        items.append({
            'actividad_ejecucion_id': row.actividad_ejecucion_id,
            'accion_respuesta_id': row.accion_respuesta_id,
            'ejecucion_actividad_id': row.ejecucion_actividad_id,
            'ejecucion_actividad_nombre': row.ejecucion_actividad_nombre,
            'institucion_ejecutora_id': row.institucion_ejecutora_id,
            'institucion_ejecutora_nombre': row.institucion_ejecutora_nombre,
            'institucion_ejecutora_siglas': row.institucion_ejecutora_siglas,
            'porcentaje_avance_id': row.porcentaje_avance_id,
            'actividad_ejecucion_avance': row.actividad_ejecucion_avance,
            'detalle': row.detalle,
            'fecha_inicio': row.fecha_inicio.isoformat() if row.fecha_inicio else None,
            'fecha_final': row.fecha_final.isoformat() if row.fecha_final else None,
            'actividad_ejecucion_estado_id': row.actividad_ejecucion_estado_id,
            'actividad_ejecucion_estado': row.actividad_ejecucion_estado
        })
    return jsonify(items)

@actividades_ejecucion_bp.route('/api/actividades_ejecucion', methods=['POST'])
def create_actividad_ejecucion():
    """Crear actividad de ejecución
    ---
    tags:
      - Actividades Ejecucion
    consumes:
      - application/json
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          required: [accion_respuesta_id, ejecucion_actividad_id, institucion_ejecutora_id, actividad_ejecucion_estado_id, fecha_inicio]
          properties:
            accion_respuesta_id: {type: integer}
            ejecucion_actividad_id: {type: integer}
            institucion_ejecutora_id: {type: integer}
            porcentaje_avance_id: {type: integer}
            detalle: {type: string}
            actividad_ejecucion_estado_id: {type: integer}
            fecha_inicio: {type: string, format: date-time}
            fecha_final: {type: string, format: date-time}
            activo: {type: boolean}
            creador: {type: string}
    responses:
      201:
        description: Actividad de ejecución creada
    """
    data = request.get_json() or {}
    if not data:
        return jsonify({'error': 'Request body required'}), 400

    now = datetime.now(timezone.utc)

    # Validate required fields
    required = ['accion_respuesta_id', 'ejecucion_actividad_id', 'institucion_ejecutora_id', 'actividad_ejecucion_estado_id', 'fecha_inicio']
    missing = [f for f in required if f not in data]
    if missing:
        return jsonify({'error': 'Missing required fields', 'missing': missing}), 400

    accion_respuesta_id = data['accion_respuesta_id']
    ejecucion_actividad_id = data['ejecucion_actividad_id']
    institucion_ejecutora_id = data['institucion_ejecutora_id']
    porcentaje_avance_id = data.get('porcentaje_avance_id', 0)
    detalle = data.get('detalle')
    actividad_ejecucion_estado_id = data['actividad_ejecucion_estado_id']
    fecha_inicio = data['fecha_inicio']
    fecha_final = data.get('fecha_final')
    activo = data.get('activo', True)
    creador = data.get('creador', 'Sistema')
    modificador = data.get('modificador', creador)

    query = db.text("""
        INSERT INTO actividades_ejecucion (
            accion_respuesta_id, ejecucion_actividad_id, institucion_ejecutora_id,
            porcentaje_avance_id, detalle, actividad_ejecucion_estado_id,
            fecha_inicio, fecha_final, activo, creador, creacion, modificador, modificacion
        )
        VALUES (
            :accion_respuesta_id, :ejecucion_actividad_id, :institucion_ejecutora_id,
            :porcentaje_avance_id, :detalle, :actividad_ejecucion_estado_id,
            :fecha_inicio, :fecha_final, :activo, :creador, :creacion, :modificador, :modificacion
        )
        RETURNING id
    """)
    params = {
        'accion_respuesta_id': accion_respuesta_id,
        'ejecucion_actividad_id': ejecucion_actividad_id,
        'institucion_ejecutora_id': institucion_ejecutora_id,
        'porcentaje_avance_id': porcentaje_avance_id,
        'detalle': detalle,
        'actividad_ejecucion_estado_id': actividad_ejecucion_estado_id,
        'fecha_inicio': fecha_inicio,
        'fecha_final': fecha_final,
        'activo': activo,
        'creador': creador,
        'creacion': now,
        'modificador': modificador,
        'modificacion': now
    }
    result = db.session.execute(query, params)
    row = result.fetchone()
    if not row:
        db.session.rollback()
        return jsonify({'error': 'Insert failed'}), 500
    new_id = row[0]
    db.session.commit()

    created = db.session.execute(db.text("SELECT * FROM actividades_ejecucion WHERE id = :id"), {'id': new_id}).fetchone()
    if not created:
        return jsonify({'error': 'Created row not found'}), 500

    return jsonify({
        'id': created.id,
        'accion_respuesta_id': created.accion_respuesta_id,
        'ejecucion_actividad_id': created.ejecucion_actividad_id,
        'institucion_ejecutora_id': created.institucion_ejecutora_id,
        'porcentaje_avance_id': created.porcentaje_avance_id,
        'detalle': created.detalle,
        'actividad_ejecucion_estado_id': created.actividad_ejecucion_estado_id,
        'fecha_inicio': created.fecha_inicio.isoformat() if created.fecha_inicio else None,
        'fecha_final': created.fecha_final.isoformat() if created.fecha_final else None,
        'activo': created.activo,
        'creador': created.creador,
        'creacion': created.creacion.isoformat() if created.creacion else None,
        'modificador': created.modificador,
        'modificacion': created.modificacion.isoformat() if created.modificacion else None
    }), 201

@actividades_ejecucion_bp.route('/api/actividades_ejecucion/<int:id>', methods=['GET'])
def get_actividad_ejecucion(id):
    """Obtener actividad de ejecución por ID
    ---
    tags:
      - Actividades Ejecucion
    parameters:
      - name: id
        in: path
        type: integer
        required: true
    responses:
      200:
        description: Actividad de ejecución
      404:
        description: No encontrado
    """
    result = db.session.execute(db.text("SELECT * FROM actividades_ejecucion WHERE id = :id"), {'id': id})
    row = result.fetchone()
    if not row:
        return jsonify({'error': 'No encontrado'}), 404
    return jsonify({
        'id': row.id,
        'accion_respuesta_id': row.accion_respuesta_id,
        'ejecucion_actividad_id': row.ejecucion_actividad_id,
        'institucion_ejecutora_id': row.institucion_ejecutora_id,
        'porcentaje_avance_id': row.porcentaje_avance_id,
        'detalle': row.detalle,
        'actividad_ejecucion_estado_id': row.actividad_ejecucion_estado_id,
        'fecha_inicio': row.fecha_inicio.isoformat() if row.fecha_inicio else None,
        'fecha_final': row.fecha_final.isoformat() if row.fecha_final else None,
        'activo': row.activo,
        'creador': row.creador,
        'creacion': row.creacion.isoformat() if row.creacion else None,
        'modificador': row.modificador,
        'modificacion': row.modificacion.isoformat() if row.modificacion else None
    })

@actividades_ejecucion_bp.route('/api/actividades_ejecucion/<int:id>', methods=['PUT'])
def update_actividad_ejecucion(id):
    """Actualizar actividad de ejecución
    ---
    tags:
      - Actividades Ejecucion
    consumes:
      - application/json
    parameters:
      - name: id
        in: path
        type: integer
        required: true
      - in: body
        name: body
        required: true
        schema:
          type: object
          properties:
            ejecucion_actividad_id: {type: integer}
            institucion_ejecutora_id: {type: integer}
            porcentaje_avance_id: {type: integer}
            detalle: {type: string}
            actividad_ejecucion_estado_id: {type: integer}
            fecha_inicio: {type: string, format: date-time}
            fecha_final: {type: string, format: date-time}
            activo: {type: boolean}
            modificador: {type: string}
    responses:
      200:
        description: Actividad de ejecución actualizada
      404:
        description: No encontrado
    """
    data = request.get_json() or {}
    if not data:
        return jsonify({'error': 'Request body required'}), 400

    now = datetime.now(timezone.utc)
    data['modificador'] = data.get('modificador', 'Sistema')
    data['modificacion'] = now

    # Only allow these fields to be updated
    allowed = {
        'ejecucion_actividad_id',
        'institucion_ejecutora_id',
        'porcentaje_avance_id',
        'detalle',
        'actividad_ejecucion_estado_id',
        'fecha_inicio',
        'fecha_final',
        'activo',
        'modificador',
        'modificacion'
    }

    set_parts = []
    params = {'id': id}
    for k, v in data.items():
        if k in allowed:
            set_parts.append(f"{k} = :{k}")
            params[k] = v

    if not set_parts:
        return jsonify({'error': 'No updatable fields provided'}), 400

    set_sql = ', '.join(set_parts)
    query = db.text(f"UPDATE actividades_ejecucion SET {set_sql} WHERE id = :id")
    result = db.session.execute(query, params)

    if getattr(result, 'rowcount', 0) == 0:
        return jsonify({'error': 'No encontrado'}), 404

    db.session.commit()
    updated = db.session.execute(db.text("SELECT * FROM actividades_ejecucion WHERE id = :id"), {'id': id}).fetchone()
    if not updated:
        return jsonify({'error': 'No encontrado después de actualizar'}), 404

    return jsonify({
        'id': updated.id,
        'accion_respuesta_id': updated.accion_respuesta_id,
        'ejecucion_actividad_id': updated.ejecucion_actividad_id,
        'institucion_ejecutora_id': updated.institucion_ejecutora_id,
        'porcentaje_avance_id': updated.porcentaje_avance_id,
        'detalle': updated.detalle,
        'actividad_ejecucion_estado_id': updated.actividad_ejecucion_estado_id,
        'fecha_inicio': updated.fecha_inicio.isoformat() if updated.fecha_inicio else None,
        'fecha_final': updated.fecha_final.isoformat() if updated.fecha_final else None,
        'activo': updated.activo,
        'creador': updated.creador,
        'creacion': updated.creacion.isoformat() if updated.creacion else None,
        'modificador': updated.modificador,
        'modificacion': updated.modificacion.isoformat() if updated.modificacion else None
    })

@actividades_ejecucion_bp.route('/api/actividades_ejecucion/<int:id>', methods=['DELETE'])
def delete_actividad_ejecucion(id):
    """Eliminar actividad de ejecución
    ---
    tags:
      - Actividades Ejecucion
    parameters:
      - name: id
        in: path
        type: integer
        required: true
    responses:
      200:
        description: Eliminado
      404:
        description: No encontrado
    """
    result = db.session.execute(db.text("DELETE FROM actividades_ejecucion WHERE id = :id"), {'id': id})
    if getattr(result, 'rowcount', 0) == 0:
        return jsonify({'error': 'No encontrado'}), 404
    db.session.commit()
    return jsonify({'mensaje': 'Eliminado correctamente'})