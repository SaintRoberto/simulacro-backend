from flask import request, jsonify
from alojamiento_estados import alojamiento_estados_bp
from models import db
from datetime import datetime, timezone


@alojamiento_estados_bp.route('/api/alojamiento-estados', methods=['GET'])
def get_alojamiento_estados():
    """Listar estados de alojamiento
    ---
    tags:
      - Alojamiento Estados
    responses:
      200:
        description: Lista de estados de alojamiento
        schema:
          type: array
          items:
            type: object
            properties:
              id: {type: integer}
              nombre: {type: string}
              descripcion: {type: string}
              activo: {type: boolean}
              creador: {type: string}
              creacion: {type: string}
              modificador: {type: string}
              modificacion: {type: string}
    """
    result = db.session.execute(db.text("SELECT * FROM alojamiento_estados"))
    estados = []
    for row in result:
        estados.append({
            'id': row.id,
            'nombre': row.nombre,
            'descripcion': row.descripcion,
            'activo': row.activo,
            'creador': row.creador,
            'creacion': row.creacion.isoformat() if getattr(row, 'creacion', None) else None,
            'modificador': row.modificador,
            'modificacion': row.modificacion.isoformat() if getattr(row, 'modificacion', None) else None,
        })
    return jsonify(estados)


@alojamiento_estados_bp.route('/api/alojamiento-estados', methods=['POST'])
def create_alojamiento_estado():
    """Crear estado de alojamiento
    ---
    tags:
      - Alojamiento Estados
    consumes:
      - application/json
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          required: [nombre]
          properties:
            nombre: {type: string}
            descripcion: {type: string}
            activo: {type: boolean}
            creador: {type: string}
    responses:
      201:
        description: Estado de alojamiento creado
        schema:
          type: object
          properties:
            id: {type: integer}
            nombre: {type: string}
            descripcion: {type: string}
            activo: {type: boolean}
            creador: {type: string}
            creacion: {type: string}
            modificador: {type: string}
            modificacion: {type: string}
    """
    data = request.get_json()
    if not data:
        return jsonify({'error': 'Invalid JSON body'}), 400

    if 'nombre' not in data:
        return jsonify({'error': 'nombre is required'}), 400

    now = datetime.now(timezone.utc)

    query = db.text("""
        INSERT INTO alojamiento_estados (
            nombre, descripcion, activo, creador, creacion, modificador, modificacion
        )
        VALUES (
            :nombre, :descripcion, :activo, :creador, :creacion, :modificador, :modificacion
        )
        RETURNING id
    """)

    result = db.session.execute(query, {
        'nombre': data['nombre'],
        'descripcion': data.get('descripcion'),
        'activo': data.get('activo', True),
        'creador': data.get('creador', 'Sistema'),
        'creacion': now,
        'modificador': data.get('creador', 'Sistema'),
        'modificacion': now,
    })

    row = result.fetchone()
    if row is None:
        return jsonify({'error': 'No se pudo crear el registro'}), 500
    estado_id = row[0]
    db.session.commit()

    estado = db.session.execute(
        db.text("SELECT * FROM alojamiento_estados WHERE id = :id"),
        {'id': estado_id}
    ).fetchone()

    return jsonify({
        'id': estado.id,
        'nombre': estado.nombre,
        'descripcion': estado.descripcion,
        'activo': estado.activo,
        'creador': estado.creador,
        'creacion': estado.creacion.isoformat() if getattr(estado, 'creacion', None) else None,
        'modificador': estado.modificador,
        'modificacion': estado.modificacion.isoformat() if getattr(estado, 'modificacion', None) else None,
    }), 201


@alojamiento_estados_bp.route('/api/alojamiento-estados/<int:id>', methods=['GET'])
def get_alojamiento_estado(id):
    """Obtener estado de alojamiento por ID
    ---
    tags:
      - Alojamiento Estados
    parameters:
      - name: id
        in: path
        type: integer
        required: true
    responses:
      200:
        description: Estado de alojamiento
        schema:
          type: object
          properties:
            id: {type: integer}
            nombre: {type: string}
            descripcion: {type: string}
            activo: {type: boolean}
            creador: {type: string}
            creacion: {type: string}
            modificador: {type: string}
            modificacion: {type: string}
      404:
        description: No encontrado
    """
    result = db.session.execute(
        db.text("SELECT * FROM alojamiento_estados WHERE id = :id"),
        {'id': id}
    )
    estado = result.fetchone()

    if not estado:
        return jsonify({'error': 'Estado de alojamiento no encontrado'}), 404

    return jsonify({
        'id': estado.id,
        'nombre': estado.nombre,
        'descripcion': estado.descripcion,
        'activo': estado.activo,
        'creador': estado.creador,
        'creacion': estado.creacion.isoformat() if getattr(estado, 'creacion', None) else None,
        'modificador': estado.modificador,
        'modificacion': estado.modificacion.isoformat() if getattr(estado, 'modificacion', None) else None,
    })


@alojamiento_estados_bp.route('/api/alojamiento-estados/<int:id>', methods=['PUT'])
def update_alojamiento_estado(id):
    """Actualizar estado de alojamiento
    ---
    tags:
      - Alojamiento Estados
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
            nombre: {type: string}
            descripcion: {type: string}
            activo: {type: boolean}
            modificador: {type: string}
    responses:
      200:
        description: Estado de alojamiento actualizado
        schema:
          type: object
    """
    data = request.get_json()
    now = datetime.now(timezone.utc)

    fields = ['nombre', 'descripcion', 'activo']

    update_fields = []
    params = {'id': id, 'modificador': data.get('modificador', 'Sistema'), 'modificacion': now}

    for field in fields:
        if field in data:
            update_fields.append(f"{field} = :{field}")
            params[field] = data[field]

    update_fields.append('modificador = :modificador')
    update_fields.append('modificacion = :modificacion')

    if not update_fields:
        return jsonify({'error': 'No fields to update'}), 400

    query = db.text(f"""
        UPDATE alojamiento_estados
        SET {', '.join(update_fields)}
        WHERE id = :id
    """)

    result = db.session.execute(query, params)

    if getattr(result, 'rowcount', 0) == 0:
        return jsonify({'error': 'Estado de alojamiento no encontrado'}), 404

    db.session.commit()

    estado = db.session.execute(
        db.text("SELECT * FROM alojamiento_estados WHERE id = :id"),
        {'id': id}
    ).fetchone()

    if not estado:
        return jsonify({'error': 'Estado de alojamiento no encontrado'}), 404

    return jsonify({
        'id': estado.id,
        'nombre': estado.nombre,
        'descripcion': estado.descripcion,
        'activo': estado.activo,
        'creador': estado.creador,
        'creacion': estado.creacion.isoformat() if getattr(estado, 'creacion', None) else None,
        'modificador': estado.modificador,
        'modificacion': estado.modificacion.isoformat() if getattr(estado, 'modificacion', None) else None,
    })


@alojamiento_estados_bp.route('/api/alojamiento-estados/<int:id>', methods=['DELETE'])
def delete_alojamiento_estado(id):
    """Eliminar estado de alojamiento
    ---
    tags:
      - Alojamiento Estados
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
    result = db.session.execute(
        db.text("DELETE FROM alojamiento_estados WHERE id = :id"),
        {'id': id}
    )

    if getattr(result, 'rowcount', 0) == 0:
        return jsonify({'error': 'Estado de alojamiento no encontrado'}), 404

    db.session.commit()
    return jsonify({'mensaje': 'Estado de alojamiento eliminado correctamente'})
