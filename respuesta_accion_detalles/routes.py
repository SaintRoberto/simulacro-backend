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

@respuesta_accion_detalles_bp.route('/api/respuesta-accion-detalles', methods=['GET'])
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
              detalle: {type: string}
              activo: {type: boolean}
              creador: {type: string}
              creacion: {type: string}
              modificador: {type: string}
              modificacion: {type: string}
    """
    result = db.session.execute(db.text("SELECT * FROM respuesta_accion_detalles"))
    items = [_row_to_dict(row) for row in result]
    return jsonify(items)

@respuesta_accion_detalles_bp.route('/api/respuesta-accion-detalles', methods=['POST'])
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
          properties:
            respuesta_accion_id: {type: integer}
            detalle: {type: string}
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

    # Ensure default audit fields
    data.setdefault('activo', True)
    data.setdefault('creador', data.get('creador', 'Sistema'))
    data.setdefault('creacion', now)
    data.setdefault('modificador', data.get('creador', 'Sistema'))
    data.setdefault('modificacion', now)

    # Build columns and params
    cols = []
    params = {}
    for k, v in data.items():
        cols.append(k)
        params[k] = v

    cols_sql = ', '.join(cols)
    vals_sql = ', '.join([f":{c}" for c in cols])

    query = db.text(f"INSERT INTO respuesta_accion_detalles ({cols_sql}) VALUES ({vals_sql}) RETURNING id")

    result = db.session.execute(query, params)
    row = result.fetchone()
    if not row:
        return jsonify({'error': 'Insert failed'}), 500
    new_id = row[0]
    db.session.commit()

    created = db.session.execute(db.text("SELECT * FROM respuesta_accion_detalles WHERE id = :id"), {'id': new_id}).fetchone()
    if not created:
        return jsonify({'error': 'Created row not found'}), 500

    return jsonify(_row_to_dict(created)), 201

@respuesta_accion_detalles_bp.route('/api/respuesta-accion-detalles/<int:id>', methods=['GET'])
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
    return jsonify(_row_to_dict(row))

@respuesta_accion_detalles_bp.route('/api/respuesta-accion-detalles/<int:id>', methods=['PUT'])
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
            detalle: {type: string}
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

    # Build SET clause dynamically
    set_parts = []
    params = {'id': id}
    for k, v in data.items():
        set_parts.append(f"{k} = :{k}")
        params[k] = v

    set_sql = ', '.join(set_parts)
    query = db.text(f"UPDATE respuesta_accion_detalles SET {set_sql} WHERE id = :id")
    result = db.session.execute(query, params)

    if getattr(result, 'rowcount', 0) == 0:
        return jsonify({'error': 'No encontrado'}), 404

    db.session.commit()
    updated = db.session.execute(db.text("SELECT * FROM respuesta_accion_detalles WHERE id = :id"), {'id': id}).fetchone()
    if not updated:
        return jsonify({'error': 'No encontrado después de actualizar'}), 404

    return jsonify(_row_to_dict(updated))

@respuesta_accion_detalles_bp.route('/api/respuesta-accion-detalles/<int:id>', methods=['DELETE'])
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