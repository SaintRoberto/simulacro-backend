from flask import request, jsonify
from alojamiento_situaciones import alojamiento_situaciones_bp
from models import db
from datetime import datetime, timezone


@alojamiento_situaciones_bp.route('/api/alojamiento_situaciones', methods=['GET'])
def get_alojamiento_situaciones():
    """Listar situaciones de alojamiento
    ---
    tags:
      - Alojamiento Situaciones
    responses:
      200:
        description: Lista de situaciones de alojamiento
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
    result = db.session.execute(db.text("SELECT * FROM alojamiento_situaciones"))
    situaciones = []
    for row in result:
        situaciones.append({
            'id': row.id,
            'nombre': row.nombre,
            'descripcion': row.descripcion,
            'activo': row.activo,
            'creador': row.creador,
            'creacion': row.creacion.isoformat() if getattr(row, 'creacion', None) else None,
            'modificador': row.modificador,
            'modificacion': row.modificacion.isoformat() if getattr(row, 'modificacion', None) else None,
        })
    return jsonify(situaciones)


@alojamiento_situaciones_bp.route('/api/alojamiento_situaciones', methods=['POST'])
def create_alojamiento_situacion():
    """Crear situación de alojamiento
    ---
    tags:
      - Alojamiento Situaciones
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
        description: Situación de alojamiento creada
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
        INSERT INTO alojamiento_situaciones (
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
    situacion_id = row[0]
    db.session.commit()

    situacion = db.session.execute(
        db.text("SELECT * FROM alojamiento_situaciones WHERE id = :id"),
        {'id': situacion_id}
    ).fetchone()

    return jsonify({
        'id': situacion.id,
        'nombre': situacion.nombre,
        'descripcion': situacion.descripcion,
        'activo': situacion.activo,
        'creador': situacion.creador,
        'creacion': situacion.creacion.isoformat() if getattr(situacion, 'creacion', None) else None,
        'modificador': situacion.modificador,
        'modificacion': situacion.modificacion.isoformat() if getattr(situacion, 'modificacion', None) else None,
    }), 201


@alojamiento_situaciones_bp.route('/api/alojamiento_situaciones/<int:id>', methods=['GET'])
def get_alojamiento_situacion(id):
    """Obtener situación de alojamiento por ID
    ---
    tags:
      - Alojamiento Situaciones
    parameters:
      - name: id
        in: path
        type: integer
        required: true
    responses:
      200:
        description: Situación de alojamiento
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
        db.text("SELECT * FROM alojamiento_situaciones WHERE id = :id"),
        {'id': id}
    )
    situacion = result.fetchone()

    if not situacion:
        return jsonify({'error': 'Situación de alojamiento no encontrada'}), 404

    return jsonify({
        'id': situacion.id,
        'nombre': situacion.nombre,
        'descripcion': situacion.descripcion,
        'activo': situacion.activo,
        'creador': situacion.creador,
        'creacion': situacion.creacion.isoformat() if getattr(situacion, 'creacion', None) else None,
        'modificador': situacion.modificador,
        'modificacion': situacion.modificacion.isoformat() if getattr(situacion, 'modificacion', None) else None,
    })


@alojamiento_situaciones_bp.route('/api/alojamiento_situaciones/<int:id>', methods=['PUT'])
def update_alojamiento_situacion(id):
    """Actualizar situación de alojamiento
    ---
    tags:
      - Alojamiento Situaciones
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
        description: Situación de alojamiento actualizada
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
        UPDATE alojamiento_situaciones
        SET {', '.join(update_fields)}
        WHERE id = :id
    """)

    result = db.session.execute(query, params)

    if getattr(result, 'rowcount', 0) == 0:
        return jsonify({'error': 'Situación de alojamiento no encontrada'}), 404

    db.session.commit()

    situacion = db.session.execute(
        db.text("SELECT * FROM alojamiento_situaciones WHERE id = :id"),
        {'id': id}
    ).fetchone()

    if not situacion:
        return jsonify({'error': 'Situación de alojamiento no encontrada'}), 404

    return jsonify({
        'id': situacion.id,
        'nombre': situacion.nombre,
        'descripcion': situacion.descripcion,
        'activo': situacion.activo,
        'creador': situacion.creador,
        'creacion': situacion.creacion.isoformat() if getattr(situacion, 'creacion', None) else None,
        'modificador': situacion.modificador,
        'modificacion': situacion.modificacion.isoformat() if getattr(situacion, 'modificacion', None) else None,
    })


@alojamiento_situaciones_bp.route('/api/alojamiento_situaciones/<int:id>', methods=['DELETE'])
def delete_alojamiento_situacion(id):
    """Eliminar situación de alojamiento
    ---
    tags:
      - Alojamiento Situaciones
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
        db.text("DELETE FROM alojamiento_situaciones WHERE id = :id"),
        {'id': id}
    )

    if getattr(result, 'rowcount', 0) == 0:
        return jsonify({'error': 'Situación de alojamiento no encontrada'}), 404

    db.session.commit()
    return jsonify({'mensaje': 'Situación de alojamiento eliminada correctamente'})
