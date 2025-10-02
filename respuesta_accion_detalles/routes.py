from flask import request, jsonify
from respuesta_accion_detalles import respuesta_accion_detalles_bp
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

@respuesta_accion_detalles_bp.route('/api/respuesta_accion_detalles', methods=['GET'])
def get_respuesta_accion_detalles():
    """Listar detalles de acciones de respuesta
    ---
    tags:
      - Respuesta Accion Detalles
    responses:
      200:
        description: Lista de detalles de acciones
        schema:
          type: array
          items:
            type: object
            properties:
              id: {type: integer}
              respuesta_accion_id: {type: integer}
              ejecucion_actividad_id: {type: integer}
              institucion_ejecutora_id: {type: integer}
              porcentaje_avance_id: {type: integer}
              detalle: {type: string}
              respuesta_accion_estado_id: {type: integer}
              fecha_inicio: {type: string}
              fecha_final: {type: string}
              activo: {type: boolean}
              creador: {type: string}
              creacion: {type: string}
              modificador: {type: string}
              modificacion: {type: string}
    """
    result = db.session.execute(db.text("SELECT * FROM respuesta_accion_detalles"))
    items = []
    for row in result:
        items.append({
            'id': row.id,
            'respuesta_accion_id': row.respuesta_accion_id,
            'ejecucion_actividad_id': row.ejecucion_actividad_id,
            'institucion_ejecutora_id': row.institucion_ejecutora_id,
            'porcentaje_avance_id': row.porcentaje_avance_id,
            'detalle': row.detalle,
            'respuesta_accion_estado_id': row.respuesta_accion_estado_id,
            'fecha_inicio': row.fecha_inicio.isoformat() if row.fecha_inicio else None,
            'fecha_final': row.fecha_final.isoformat() if row.fecha_final else None,
            'activo': row.activo,
            'creador': row.creador,
            'creacion': row.creacion.isoformat() if row.creacion else None,
            'modificador': row.modificador,
            'modificacion': row.modificacion.isoformat() if row.modificacion else None
        })
    return jsonify(items)

@respuesta_accion_detalles_bp.route('/api/respuesta_accion_detalles/respuesta_accion/<int:respuesta_accion_id>', methods=['GET'])
def get_respuesta_accion_detalles_by_respuesta_accion(respuesta_accion_id):
    """Listar detalles de acciones por respuesta_accion_id
    ---
    tags:
      - Respuesta Accion Detalles
    parameters:
      - name: respuesta_accion_id
        in: path
        type: integer
        required: true
    responses:
      200:
        description: Lista de detalles para la acción de respuesta
        schema:
          type: array
          items:
            type: object
            properties:
              respuesta_accion_detalle_id: {type: integer}
              respuesta_accion_id: {type: integer}
              ejecucion_actividad_id: {type: integer}
              ejecucion_actividad_nombre: {type: string}
              institucion_ejecutora_id: {type: integer}
              institucion_ejecutora_nombre: {type: string}
              institucion_ejecutora_siglas: {type: string}
              porcentaje_avance_id: {type: integer}
              respuesta_accion_detalle_avance: {type: string}
              detalle: {type: string}
              fecha_inicio: {type: string}
              fecha_final: {type: string}
              respuesta_accion_estado_id: {type: integer}
              respuesta_accion_detalle_estado: {type: string}
    """
    query = db.text("""
        SELECT d.id respuesta_accion_detalle_id, d.respuesta_accion_id,
               d.ejecucion_actividad_id, x.nombre ejecucion_actividad_nombre,
               d.institucion_ejecutora_id, i.nombre institucion_ejecutora_nombre, i.siglas institucion_ejecutora_siglas,
               d.porcentaje_avance_id, a.nombre respuesta_accion_detalle_avance,
               d.detalle, d.fecha_inicio, d.fecha_final,
               d.respuesta_accion_estado_id, e.nombre respuesta_accion_detalle_estado
        FROM public.respuesta_accion_detalles d
        INNER JOIN public.instituciones i ON d.institucion_ejecutora_id = i.id
        INNER JOIN public.ejecucion_actividades x ON d.ejecucion_actividad_id = x.id
        INNER JOIN public.respuesta_estados e ON d.respuesta_accion_estado_id = e.id
        INNER JOIN public.respuesta_avances a ON d.porcentaje_avance_id = a.id
        WHERE d.respuesta_accion_id = :respuesta_accion_id
        ORDER BY d.id ASC
    """)
    result = db.session.execute(query, {'respuesta_accion_id': respuesta_accion_id})
    items = []
    for row in result:
        items.append({
            'respuesta_accion_detalle_id': row.respuesta_accion_detalle_id,
            'respuesta_accion_id': row.respuesta_accion_id,
            'ejecucion_actividad_id': row.ejecucion_actividad_id,
            'ejecucion_actividad_nombre': row.ejecucion_actividad_nombre,
            'institucion_ejecutora_id': row.institucion_ejecutora_id,
            'institucion_ejecutora_nombre': row.institucion_ejecutora_nombre,
            'institucion_ejecutora_siglas': row.institucion_ejecutora_siglas,
            'porcentaje_avance_id': row.porcentaje_avance_id,
            'respuesta_accion_detalle_avance': row.respuesta_accion_detalle_avance,
            'detalle': row.detalle,
            'fecha_inicio': row.fecha_inicio.isoformat() if row.fecha_inicio else None,
            'fecha_final': row.fecha_final.isoformat() if row.fecha_final else None,
            'respuesta_accion_estado_id': row.respuesta_accion_estado_id,
            'respuesta_accion_detalle_estado': row.respuesta_accion_detalle_estado
        })
    return jsonify(items)

@respuesta_accion_detalles_bp.route('/api/respuesta_accion_detalles', methods=['POST'])
def create_respuesta_accion_detalle():
    """Crear detalle de acción de respuesta
    ---
    tags:
      - Respuesta Accion Detalles
    consumes:
      - application/json
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          required: [respuesta_accion_id, ejecucion_actividad_id, institucion_ejecutora_id, respuesta_accion_estado_id, fecha_inicio]
          properties:
            respuesta_accion_id: {type: integer}
            ejecucion_actividad_id: {type: integer}
            institucion_ejecutora_id: {type: integer}
            porcentaje_avance_id: {type: integer}
            detalle: {type: string}
            respuesta_accion_estado_id: {type: integer}
            fecha_inicio: {type: string, format: date-time}
            fecha_final: {type: string, format: date-time}
            activo: {type: boolean}
            creador: {type: string}
    responses:
      201:
        description: Detalle creado
    """
    data = request.get_json() or {}
    if not data:
        return jsonify({'error': 'Request body required'}), 400

    now = datetime.now(timezone.utc)

    # Validate required fields
    required = ['respuesta_accion_id', 'ejecucion_actividad_id', 'institucion_ejecutora_id', 'respuesta_accion_estado_id', 'fecha_inicio']
    missing = [f for f in required if f not in data]
    if missing:
        return jsonify({'error': 'Missing required fields', 'missing': missing}), 400

    respuesta_accion_id = data['respuesta_accion_id']
    ejecucion_actividad_id = data['ejecucion_actividad_id']
    institucion_ejecutora_id = data['institucion_ejecutora_id']
    porcentaje_avance_id = data.get('porcentaje_avance_id', 0)
    detalle = data.get('detalle')
    respuesta_accion_estado_id = data['respuesta_accion_estado_id']
    fecha_inicio = data['fecha_inicio']
    fecha_final = data.get('fecha_final')
    activo = data.get('activo', True)
    creador = data.get('creador', 'Sistema')
    modificador = data.get('modificador', creador)

    query = db.text("""
        INSERT INTO respuesta_accion_detalles (
            respuesta_accion_id, ejecucion_actividad_id, institucion_ejecutora_id,
            porcentaje_avance_id, detalle, respuesta_accion_estado_id,
            fecha_inicio, fecha_final, activo, creador, creacion, modificador, modificacion
        )
        VALUES (
            :respuesta_accion_id, :ejecucion_actividad_id, :institucion_ejecutora_id,
            :porcentaje_avance_id, :detalle, :respuesta_accion_estado_id,
            :fecha_inicio, :fecha_final, :activo, :creador, :creacion, :modificador, :modificacion
        )
        RETURNING id
    """)

    params = {
        'respuesta_accion_id': respuesta_accion_id,
        'ejecucion_actividad_id': ejecucion_actividad_id,
        'institucion_ejecutora_id': institucion_ejecutora_id,
        'porcentaje_avance_id': porcentaje_avance_id,
        'detalle': detalle,
        'respuesta_accion_estado_id': respuesta_accion_estado_id,
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

    created = db.session.execute(db.text("SELECT * FROM respuesta_accion_detalles WHERE id = :id"), {'id': new_id}).fetchone()
    if not created:
        return jsonify({'error': 'Created row not found'}), 500

    return jsonify({
        'id': created.id,
        'respuesta_accion_id': created.respuesta_accion_id,
        'ejecucion_actividad_id': created.ejecucion_actividad_id,
        'institucion_ejecutora_id': created.institucion_ejecutora_id,
        'porcentaje_avance_id': created.porcentaje_avance_id,
        'detalle': created.detalle,
        'respuesta_accion_estado_id': created.respuesta_accion_estado_id,
        'fecha_inicio': created.fecha_inicio.isoformat() if created.fecha_inicio else None,
        'fecha_final': created.fecha_final.isoformat() if created.fecha_final else None,
        'activo': created.activo,
        'creador': created.creador,
        'creacion': created.creacion.isoformat() if created.creacion else None,
        'modificador': created.modificador,
        'modificacion': created.modificacion.isoformat() if created.modificacion else None
    }), 201

@respuesta_accion_detalles_bp.route('/api/respuesta_accion_detalles/<int:id>', methods=['GET'])
def get_respuesta_accion_detalle(id):
    """Obtener detalle de acción por ID
    ---
    tags:
      - Respuesta Accion Detalles
    parameters:
      - name: id
        in: path
        type: integer
        required: true
    responses:
      200:
        description: Detalle de acción
      404:
        description: No encontrado
    """
    result = db.session.execute(db.text("SELECT * FROM respuesta_accion_detalles WHERE id = :id"), {'id': id})
    row = result.fetchone()
    if not row:
        return jsonify({'error': 'No encontrado'}), 404
    return jsonify({
        'id': row.id,
        'respuesta_accion_id': row.respuesta_accion_id,
        'ejecucion_actividad_id': row.ejecucion_actividad_id,
        'institucion_ejecutora_id': row.institucion_ejecutora_id,
        'porcentaje_avance_id': row.porcentaje_avance_id,
        'detalle': row.detalle,
        'respuesta_accion_estado_id': row.respuesta_accion_estado_id,
        'fecha_inicio': row.fecha_inicio.isoformat() if row.fecha_inicio else None,
        'fecha_final': row.fecha_final.isoformat() if row.fecha_final else None,
        'activo': row.activo,
        'creador': row.creador,
        'creacion': row.creacion.isoformat() if row.creacion else None,
        'modificador': row.modificador,
        'modificacion': row.modificacion.isoformat() if row.modificacion else None
    })

@respuesta_accion_detalles_bp.route('/api/respuesta_accion_detalles/<int:id>', methods=['PUT'])
def update_respuesta_accion_detalle(id):
    """Actualizar detalle de acción
    ---
    tags:
      - Respuesta Accion Detalles
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
            respuesta_accion_estado_id: {type: integer}
            fecha_inicio: {type: string, format: date-time}
            fecha_final: {type: string, format: date-time}
            activo: {type: boolean}
            modificador: {type: string}
    responses:
      200:
        description: Detalle actualizado
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
        'respuesta_accion_estado_id',
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
    query = db.text(f"UPDATE respuesta_accion_detalles SET {set_sql} WHERE id = :id")
    result = db.session.execute(query, params)

    if getattr(result, 'rowcount', 0) == 0:
        return jsonify({'error': 'No encontrado'}), 404

    db.session.commit()
    updated = db.session.execute(db.text("SELECT * FROM respuesta_accion_detalles WHERE id = :id"), {'id': id}).fetchone()
    if not updated:
        return jsonify({'error': 'No encontrado después de actualizar'}), 404

    return jsonify({
        'id': updated.id,
        'respuesta_accion_id': updated.respuesta_accion_id,
        'ejecucion_actividad_id': updated.ejecucion_actividad_id,
        'institucion_ejecutora_id': updated.institucion_ejecutora_id,
        'porcentaje_avance_id': updated.porcentaje_avance_id,
        'detalle': updated.detalle,
        'respuesta_accion_estado_id': updated.respuesta_accion_estado_id,
        'fecha_inicio': updated.fecha_inicio.isoformat() if updated.fecha_inicio else None,
        'fecha_final': updated.fecha_final.isoformat() if updated.fecha_final else None,
        'activo': updated.activo,
        'creador': updated.creador,
        'creacion': updated.creacion.isoformat() if updated.creacion else None,
        'modificador': updated.modificador,
        'modificacion': updated.modificacion.isoformat() if updated.modificacion else None
    })

@respuesta_accion_detalles_bp.route('/api/respuesta_accion_detalles/<int:id>', methods=['DELETE'])
def delete_respuesta_accion_detalle(id):
    """Eliminar detalle de acción
    ---
    tags:
      - Respuesta Accion Detalles
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
    result = db.session.execute(db.text("DELETE FROM respuesta_accion_detalles WHERE id = :id"), {'id': id})
    if getattr(result, 'rowcount', 0) == 0:
        return jsonify({'error': 'No encontrado'}), 404
    db.session.commit()
    return jsonify({'mensaje': 'Eliminado correctamente'})