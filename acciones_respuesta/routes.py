from flask import request, jsonify
from acciones_respuesta import acciones_respuesta_bp
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

@acciones_respuesta_bp.route('/api/acciones_respuesta', methods=['GET'])
def get_acciones_respuesta():
    """Listar acciones de respuesta
    ---
    tags:
      - Acciones Respuesta
    responses:
      200:
        description: Lista de acciones de respuesta
        schema:
          type: array
          items:
            type: object
            properties:
              id: {type: integer}
              coe_acta_resolucion_mesa_id: {type: integer}
              usuario_id: {type: integer}
              accion_respuesta_origen_id: {type: integer}
              detalle: {type: string}
              accion_respuesta_estado_id: {type: integer}
              fecha_final: {type: string}
              activo: {type: boolean}
              creador: {type: string}
              creacion: {type: string}
              modificador: {type: string}
              modificacion: {type: string}
    """
    result = db.session.execute(db.text("SELECT * FROM acciones_respuesta"))
    items = [_row_to_dict(row) for row in result]
    return jsonify(items)

@acciones_respuesta_bp.route('/api/acciones_respuesta/usuario/<int:usuario_id>', methods=['GET'])
def get_acciones_respuesta_by_usuario(usuario_id):
    """Listar acciones de respuesta por usuario
    ---
    tags:
      - Acciones Respuesta
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
              accion_respuesta_id: {type: integer}
              coe_acta_resolucion_mesa_id: {type: integer}
              detalle: {type: string}
              origen_id: {type: integer}
              origen_nombre: {type: string}
              estado_id: {type: integer}
              estado_nombre: {type: string}
              fecha_final: {type: string}
    """
    query = db.text("""
        SELECT ar.id accion_respuesta_id, ar.coe_acta_resolucion_mesa_id, ar.detalle,
               ar.accion_respuesta_origen_id origen_id, o.nombre origen_nombre,
               ar.accion_respuesta_estado_id estado_id, e.nombre estado_nombre, ar.fecha_final
        FROM public.acciones_respuesta ar
        LEFT JOIN public.accion_respuesta_origenes o ON ar.accion_respuesta_origen_id = o.id
        LEFT JOIN public.accion_respuesta_estados e ON ar.accion_respuesta_estado_id = e.id
        WHERE ar.usuario_id = :usuario_id
        ORDER BY ar.id ASC
    """)
    result = db.session.execute(query, {'usuario_id': usuario_id})
    items = []
    for row in result:
        items.append({
            'accion_respuesta_id': row.accion_respuesta_id,
            'coe_acta_resolucion_mesa_id': row.coe_acta_resolucion_mesa_id,
            'detalle': row.detalle,
            'origen_id': row.origen_id,
            'origen_nombre': row.origen_nombre,
            'estado_id': row.estado_id,
            'estado_nombre': row.estado_nombre,
            'fecha_final': row.fecha_final.isoformat() if row.fecha_final else None
        })
    return jsonify(items)

@acciones_respuesta_bp.route('/api/acciones_respuesta/usuario/<int:usuario_id>/propia_gestion', methods=['GET'])
def get_accion_respuesta_by_usuario_by_propia_gestion(usuario_id):
    """Verificar existencia de acciones de respuesta de propia gestión para un usuario
    ---
    tags:
      - Acciones Respuesta
    parameters:
      - name: usuario_id
        in: path
        type: integer
        required: true
    responses:
      200:
        description: Cantidad de acciones de respuesta con origen propia gestión (accion_respuesta_origen_id = 0)
        schema:
          type: object
          properties:
            existe: {type: integer}
    """
    query = db.text("""
        SELECT COUNT(id) AS existe
        FROM public.acciones_respuesta
        WHERE accion_respuesta_origen_id = 0
          AND usuario_id = :usuario_id
    """)

    result = db.session.execute(query, {'usuario_id': usuario_id})
    row = result.fetchone()
    count = row.existe if row is not None else 0

    return jsonify({'existe': count})

@acciones_respuesta_bp.route('/api/acciones_respuesta', methods=['POST'])
def create_accion_respuesta():
    """Crear acción de respuesta
    ---
    tags:
      - Acciones Respuesta
    consumes:
      - application/json
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          required: [usuario_id, accion_respuesta_origen_id, accion_respuesta_estado_id]
          properties:
            coe_acta_resolucion_mesa_id: {type: integer}
            usuario_id: {type: integer}
            accion_respuesta_origen_id: {type: integer}
            detalle: {type: string}
            accion_respuesta_estado_id: {type: integer}
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
    required = ['usuario_id', 'accion_respuesta_origen_id', 'accion_respuesta_estado_id']
    missing = [f for f in required if f not in data]
    if missing:
        return jsonify({'error': 'Missing required fields', 'missing': missing}), 400

    # Prepare insert with explicit columns to match DB schema
    coe_acta_resolucion_mesa_id = data.get('coe_acta_resolucion_mesa_id', 0)
    usuario_id = data['usuario_id']
    accion_respuesta_origen_id = data['accion_respuesta_origen_id']
    detalle = data.get('detalle')
    accion_respuesta_estado_id = data['accion_respuesta_estado_id']
    fecha_final = data.get('fecha_final')
    activo = data.get('activo', True)
    creador = data.get('creador', 'Sistema')
    modificador = data.get('modificador', creador)

    query = db.text("""
        INSERT INTO acciones_respuesta (
            coe_acta_resolucion_mesa_id, usuario_id, accion_respuesta_origen_id,
            detalle, accion_respuesta_estado_id, fecha_final,
            activo, creador, creacion, modificador, modificacion
        )
        VALUES (
            :coe_acta_resolucion_mesa_id, :usuario_id, :accion_respuesta_origen_id,
            :detalle, :accion_respuesta_estado_id, :fecha_final,
            :activo, :creador, :creacion, :modificador, :modificacion
        )
        RETURNING id
    """)

    params = {
        'coe_acta_resolucion_mesa_id': coe_acta_resolucion_mesa_id,
        'usuario_id': usuario_id,
        'accion_respuesta_origen_id': accion_respuesta_origen_id,
        'detalle': detalle,
        'accion_respuesta_estado_id': accion_respuesta_estado_id,
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

    created = db.session.execute(db.text("SELECT * FROM acciones_respuesta WHERE id = :id"), {'id': new_id}).fetchone()
    if not created:
        return jsonify({'error': 'Created row not found'}), 500

    return jsonify(_row_to_dict(created)), 201

@acciones_respuesta_bp.route('/api/acciones_respuesta/<int:id>', methods=['GET'])
def get_accion_respuesta(id):
    """Obtener acción de respuesta por ID
    ---
    tags:
      - Acciones Respuesta
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
    result = db.session.execute(db.text("SELECT * FROM acciones_respuesta WHERE id = :id"), {'id': id})
    row = result.fetchone()
    if not row:
        return jsonify({'error': 'No encontrado'}), 404
    return jsonify(_row_to_dict(row))

@acciones_respuesta_bp.route('/api/acciones_respuesta/<int:id>', methods=['PUT'])
def update_accion_respuesta(id):
    """Actualizar acción de respuesta
    ---
    tags:
      - Acciones Respuesta
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
            coe_acta_resolucion_mesa_id: {type: integer}
            usuario_id: {type: integer}
            accion_respuesta_origen_id: {type: integer}
            detalle: {type: string}
            accion_respuesta_estado_id: {type: integer}
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
        'coe_acta_resolucion_id',
        'usuario_id',
        'accion_respuesta_origen_id',
        'detalle',
        'accion_respuesta_estado_id',
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
    query = db.text(f"UPDATE acciones_respuesta SET {set_sql} WHERE id = :id")
    result = db.session.execute(query, params)

    if getattr(result, 'rowcount', 0) == 0:
        return jsonify({'error': 'No encontrado'}), 404

    db.session.commit()
    updated = db.session.execute(db.text("SELECT * FROM acciones_respuesta WHERE id = :id"), {'id': id}).fetchone()
    if not updated:
        return jsonify({'error': 'No encontrado después de actualizar'}), 404

    return jsonify(_row_to_dict(updated))

@acciones_respuesta_bp.route('/api/acciones_respuesta/<int:id>', methods=['DELETE'])
def delete_accion_respuesta(id):
    """Eliminar acción de respuesta
    ---
    tags:
      - Acciones Respuesta
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
    result = db.session.execute(db.text("DELETE FROM acciones_respuesta WHERE id = :id"), {'id': id})
    if getattr(result, 'rowcount', 0) == 0:
        return jsonify({'error': 'No encontrado'}), 404
    db.session.commit()
    return jsonify({'mensaje': 'Eliminado correctamente'})