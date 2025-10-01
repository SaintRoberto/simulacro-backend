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

@respuesta_acciones_bp.route('/api/respuesta-acciones', methods=['GET'])
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
              respuesta_accion_id: {type: integer}
              descripcion: {type: string}
              activo: {type: boolean}
              creador: {type: string}
              creacion: {type: string}
              modificador: {type: string}
              modificacion: {type: string}
    """
    result = db.session.execute(db.text("SELECT * FROM respuesta_acciones"))
    items = [_row_to_dict(row) for row in result]
    return jsonify(items)

@respuesta_acciones_bp.route('/api/respuesta-acciones', methods=['POST'])
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
          properties:
            respuesta_accion_id: {type: integer}
            descripcion: {type: string}
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

    query = db.text(f"INSERT INTO respuesta_acciones ({cols_sql}) VALUES ({vals_sql}) RETURNING id")

    result = db.session.execute(query, params)
    row = result.fetchone()
    if not row:
        return jsonify({'error': 'Insert failed'}), 500
    new_id = row[0]
    db.session.commit()

    created = db.session.execute(db.text("SELECT * FROM respuesta_acciones WHERE id = :id"), {'id': new_id}).fetchone()
    if not created:
        return jsonify({'error': 'Created row not found'}), 500

    return jsonify(_row_to_dict(created)), 201

@respuesta_acciones_bp.route('/api/respuesta-acciones/<int:id>', methods=['GET'])
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

@respuesta_acciones_bp.route('/api/respuesta-acciones/<int:id>', methods=['PUT'])
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
            descripcion: {type: string}
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

    # Build SET clause dynamically
    set_parts = []
    params = {'id': id}
    for k, v in data.items():
        set_parts.append(f"{k} = :{k}")
        params[k] = v

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

@respuesta_acciones_bp.route('/api/respuesta-acciones/<int:id>', methods=['DELETE'])
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