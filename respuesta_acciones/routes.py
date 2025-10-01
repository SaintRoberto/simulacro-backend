from flask import request, jsonify
from respuesta_acciones import respuesta_acciones_bp
from models import db
from datetime import datetime, timezone

def _row_to_dict(row):
    try:
        mapping = dict(row._mapping)  # SQLAlchemy Row
    except Exception:
        # Fallback: try attribute access
        mapping = {k: getattr(row, k) for k in row.keys()}
    for k, v in list(mapping.items()):
        if isinstance(v, datetime):
            mapping[k] = v.isoformat()
    return mapping

@respuesta_acciones_bp.route('/api/respuesta_acciones', methods=['GET'])
def get_respuesta_acciones():
    """Listar acciones de respuesta
    ---
    tags:
      - Respuesta Acciones
    responses:
      200:
        description: Lista de acciones de respuesta
        schema:
          type: array
          items:
            type: object
            properties:
              id: {type: integer}
              resolucion_id: {type: integer}
              usuario_id: {type: integer}
              respuesta_accion_origen_id: {type: integer}
              detalle: {type: string}
              respuesta_estado_id: {type: integer}
              fecha_final: {type: string}
              activo: {type: boolean}
              creador: {type: string}
              creacion: {type: string}
              modificador: {type: string}
              modificacion: {type: string}
    """
    result = db.session.execute(db.text("SELECT * FROM respuesta_acciones"))
    items = [_row_to_dict(row) for row in result]
    return jsonify(items)

@respuesta_acciones_bp.route('/api/respuesta_acciones/usuario/<int:usuario_id>', methods=['GET'])
def get_respuesta_acciones_by_usuario(usuario_id):
    """Listar acciones de respuesta por usuario
    ---
    tags:
      - Respuesta Acciones
    parameters:
      - name: usuario_id
        in: path
        type: integer
        required: true
    responses:
      200:
        description: Lista de acciones de respuesta para el usuario
        schema:
          type: array
          items:
            type: object
            properties:
              respuesta_accion_id: {type: integer}
              resolucion_id: {type: integer}
              detalle: {type: string}
              origen_id: {type: integer}
              origen_nombre: {type: string}
              estado_id: {type: integer}
              estado_nombre: {type: string}
              fecha_final: {type: string}
    """
    query = db.text("""
        SELECT ar.id respuesta_accion_id, ar.resolucion_id, ar.detalle,
               ar.respuesta_accion_origen_id origen_id, o.nombre origen_nombre,
               ar.respuesta_estado_id estado_id, e.nombre estado_nombre, ar.fecha_final
        FROM public.respuesta_acciones ar
        INNER JOIN public.respuesta_accion_origenes o ON ar.respuesta_accion_origen_id = o.id
        INNER JOIN public.respuesta_estados e ON ar.respuesta_estado_id = e.id
        WHERE ar.usuario_id = :usuario_id
        ORDER BY ar.id ASC
    """)
    result = db.session.execute(query, {'usuario_id': usuario_id})
    items = []
    for row in result:
        items.append({
            'respuesta_accion_id': row.respuesta_accion_id,
            'resolucion_id': row.resolucion_id,
            'detalle': row.detalle,
            'origen_id': row.origen_id,
            'origen_nombre': row.origen_nombre,
            'estado_id': row.estado_id,
            'estado_nombre': row.estado_nombre,
            'fecha_final': row.fecha_final.isoformat() if row.fecha_final else None
        })
    return jsonify(items)

@respuesta_acciones_bp.route('/api/respuesta_acciones', methods=['POST'])
def create_respuesta_accion():
    """Crear acción de respuesta
    ---
    tags:
      - Respuesta Acciones
    consumes:
      - application/json
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          required: [usuario_id, respuesta_accion_origen_id, respuesta_estado_id]
          properties:
            resolucion_id: {type: integer}
            usuario_id: {type: integer}
            respuesta_accion_origen_id: {type: integer}
            detalle: {type: string}
            respuesta_estado_id: {type: integer}
            fecha_final: {type: string, format: date-time}
            activo: {type: boolean}
            creador: {type: string}
    responses:
      201:
        description: Acción creada
    """
    data = request.get_json() or {}
    if not data:
        return jsonify({'error': 'Request body required'}), 400

    now = datetime.now(timezone.utc)

    # Validate required fields
    required = ['usuario_id', 'respuesta_accion_origen_id', 'respuesta_estado_id']
    missing = [f for f in required if f not in data]
    if missing:
        return jsonify({'error': 'Missing required fields', 'missing': missing}), 400

    # Prepare insert with explicit columns to match DB schema
    resolucion_id = data.get('resolucion_id', 0)
    usuario_id = data['usuario_id']
    respuesta_accion_origen_id = data['respuesta_accion_origen_id']
    detalle = data.get('detalle')
    respuesta_estado_id = data['respuesta_estado_id']
    fecha_final = data.get('fecha_final')
    activo = data.get('activo', True)
    creador = data.get('creador', 'Sistema')
    modificador = data.get('modificador', creador)

    query = db.text("""
        INSERT INTO respuesta_acciones (
            resolucion_id, usuario_id, respuesta_accion_origen_id,
            detalle, respuesta_estado_id, fecha_final,
            activo, creador, creacion, modificador, modificacion
        )
        VALUES (
            :resolucion_id, :usuario_id, :respuesta_accion_origen_id,
            :detalle, :respuesta_estado_id, :fecha_final,
            :activo, :creador, :creacion, :modificador, :modificacion
        )
        RETURNING id
    """)

    params = {
        'resolucion_id': resolucion_id,
        'usuario_id': usuario_id,
        'respuesta_accion_origen_id': respuesta_accion_origen_id,
        'detalle': detalle,
        'respuesta_estado_id': respuesta_estado_id,
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

    created = db.session.execute(db.text("SELECT * FROM respuesta_acciones WHERE id = :id"), {'id': new_id}).fetchone()
    if not created:
        return jsonify({'error': 'Created row not found'}), 500

    return jsonify(_row_to_dict(created)), 201

@respuesta_acciones_bp.route('/api/respuesta_acciones/<int:id>', methods=['GET'])
def get_respuesta_accion(id):
    """Obtener acción de respuesta por ID
    ---
    tags:
      - Respuesta Acciones
    parameters:
      - name: id
        in: path
        type: integer
        required: true
    responses:
      200:
        description: Acción de respuesta
      404:
        description: No encontrada
    """
    result = db.session.execute(db.text("SELECT * FROM respuesta_acciones WHERE id = :id"), {'id': id})
    row = result.fetchone()
    if not row:
        return jsonify({'error': 'No encontrado'}), 404
    return jsonify(_row_to_dict(row))

@respuesta_acciones_bp.route('/api/respuesta_acciones/<int:id>', methods=['PUT'])
def update_respuesta_accion(id):
    """Actualizar acción de respuesta
    ---
    tags:
      - Respuesta Acciones
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
            resolucion_id: {type: integer}
            usuario_id: {type: integer}
            respuesta_accion_origen_id: {type: integer}
            detalle: {type: string}
            respuesta_estado_id: {type: integer}
            fecha_final: {type: string, format: date-time}
            activo: {type: boolean}
            modificador: {type: string}
    responses:
      200:
        description: Acción actualizada
      404:
        description: No encontrada
    """
    data = request.get_json() or {}
    if not data:
        return jsonify({'error': 'Request body required'}), 400

    now = datetime.now(timezone.utc)
    data['modificador'] = data.get('modificador', 'Sistema')
    data['modificacion'] = now

    # Only allow these fields to be updated
    allowed = {
        'resolucion_id',
        'usuario_id',
        'respuesta_accion_origen_id',
        'detalle',
        'respuesta_estado_id',
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
    query = db.text(f"UPDATE respuesta_acciones SET {set_sql} WHERE id = :id")
    result = db.session.execute(query, params)

    if getattr(result, 'rowcount', 0) == 0:
        return jsonify({'error': 'No encontrado'}), 404

    db.session.commit()
    updated = db.session.execute(db.text("SELECT * FROM respuesta_acciones WHERE id = :id"), {'id': id}).fetchone()
    if not updated:
        return jsonify({'error': 'No encontrado después de actualizar'}), 404

    return jsonify(_row_to_dict(updated))

@respuesta_acciones_bp.route('/api/respuesta_acciones/<int:id>', methods=['DELETE'])
def delete_respuesta_accion(id):
    """Eliminar acción de respuesta
    ---
    tags:
      - Respuesta Acciones
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
    result = db.session.execute(db.text("DELETE FROM respuesta_acciones WHERE id = :id"), {'id': id})
    if getattr(result, 'rowcount', 0) == 0:
        return jsonify({'error': 'No encontrado'}), 404
    db.session.commit()
    return jsonify({'mensaje': 'Eliminado correctamente'})