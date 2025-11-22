from flask import request, jsonify
from alojamiento_tipos import alojamiento_tipos_bp
from models import db
from datetime import datetime, timezone


@alojamiento_tipos_bp.route('/api/alojamiento-tipos', methods=['GET'])
def get_alojamiento_tipos():
    """Listar tipos de alojamiento
    ---
    tags:
      - Alojamiento Tipos
    responses:
      200:
        description: Lista de tipos de alojamiento
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
    result = db.session.execute(db.text("SELECT * FROM alojamiento_tipos"))
    tipos = []
    for row in result:
        tipos.append({
            'id': row.id,
            'nombre': row.nombre,
            'descripcion': row.descripcion,
            'activo': row.activo,
            'creador': row.creador,
            'creacion': row.creacion.isoformat() if getattr(row, 'creacion', None) else None,
            'modificador': row.modificador,
            'modificacion': row.modificacion.isoformat() if getattr(row, 'modificacion', None) else None,
        })
    return jsonify(tipos)


@alojamiento_tipos_bp.route('/api/alojamiento-tipos', methods=['POST'])
def create_alojamiento_tipo():
    """Crear tipo de alojamiento
    ---
    tags:
      - Alojamiento Tipos
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
        description: Tipo de alojamiento creado
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
        INSERT INTO alojamiento_tipos (
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
    tipo_id = row[0]
    db.session.commit()

    tipo = db.session.execute(
        db.text("SELECT * FROM alojamiento_tipos WHERE id = :id"),
        {'id': tipo_id}
    ).fetchone()

    return jsonify({
        'id': tipo.id,
        'nombre': tipo.nombre,
        'descripcion': tipo.descripcion,
        'activo': tipo.activo,
        'creador': tipo.creador,
        'creacion': tipo.creacion.isoformat() if getattr(tipo, 'creacion', None) else None,
        'modificador': tipo.modificador,
        'modificacion': tipo.modificacion.isoformat() if getattr(tipo, 'modificacion', None) else None,
    }), 201


@alojamiento_tipos_bp.route('/api/alojamiento-tipos/<int:id>', methods=['GET'])
def get_alojamiento_tipo(id):
    """Obtener tipo de alojamiento por ID
    ---
    tags:
      - Alojamiento Tipos
    parameters:
      - name: id
        in: path
        type: integer
        required: true
    responses:
      200:
        description: Tipo de alojamiento
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
        db.text("SELECT * FROM alojamiento_tipos WHERE id = :id"),
        {'id': id}
    )
    tipo = result.fetchone()

    if not tipo:
        return jsonify({'error': 'Tipo de alojamiento no encontrado'}), 404

    return jsonify({
        'id': tipo.id,
        'nombre': tipo.nombre,
        'descripcion': tipo.descripcion,
        'activo': tipo.activo,
        'creador': tipo.creador,
        'creacion': tipo.creacion.isoformat() if getattr(tipo, 'creacion', None) else None,
        'modificador': tipo.modificador,
        'modificacion': tipo.modificacion.isoformat() if getattr(tipo, 'modificacion', None) else None,
    })


@alojamiento_tipos_bp.route('/api/alojamiento-tipos/<int:id>', methods=['PUT'])
def update_alojamiento_tipo(id):
    """Actualizar tipo de alojamiento
    ---
    tags:
      - Alojamiento Tipos
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
        description: Tipo de alojamiento actualizado
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
        UPDATE alojamiento_tipos
        SET {', '.join(update_fields)}
        WHERE id = :id
    """)

    result = db.session.execute(query, params)

    if getattr(result, 'rowcount', 0) == 0:
        return jsonify({'error': 'Tipo de alojamiento no encontrado'}), 404

    db.session.commit()

    tipo = db.session.execute(
        db.text("SELECT * FROM alojamiento_tipos WHERE id = :id"),
        {'id': id}
    ).fetchone()

    if not tipo:
        return jsonify({'error': 'Tipo de alojamiento no encontrado'}), 404

    return jsonify({
        'id': tipo.id,
        'nombre': tipo.nombre,
        'descripcion': tipo.descripcion,
        'activo': tipo.activo,
        'creador': tipo.creador,
        'creacion': tipo.creacion.isoformat() if getattr(tipo, 'creacion', None) else None,
        'modificador': tipo.modificador,
        'modificacion': tipo.modificacion.isoformat() if getattr(tipo, 'modificacion', None) else None,
    })


@alojamiento_tipos_bp.route('/api/alojamiento-tipos/<int:id>', methods=['DELETE'])
def delete_alojamiento_tipo(id):
    """Eliminar tipo de alojamiento
    ---
    tags:
      - Alojamiento Tipos
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
        db.text("DELETE FROM alojamiento_tipos WHERE id = :id"),
        {'id': id}
    )

    if getattr(result, 'rowcount', 0) == 0:
        return jsonify({'error': 'Tipo de alojamiento no encontrado'}), 404

    db.session.commit()
    return jsonify({'mensaje': 'Tipo de alojamiento eliminado correctamente'})
