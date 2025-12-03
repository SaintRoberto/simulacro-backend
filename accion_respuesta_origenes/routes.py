from flask import request, jsonify
from accion_respuesta_origenes import accion_respuesta_origenes_bp
from models import db
from datetime import datetime, timezone


@accion_respuesta_origenes_bp.route('/api/accion_respuesta_origenes', methods=['GET'])
def get_accion_respuesta_origenes():
    """Listar accion_respuesta_origenes
    ---
    tags:
      - Accion Respuesta Origenes
    responses:
      200:
        description: Lista de accion_respuesta_origenes
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
    result = db.session.execute(db.text("SELECT * FROM accion_respuesta_origenes"))
    items = []
    for row in result:
        items.append({  # type: ignore
            'id': row.id,
            'nombre': row.nombre,
            'descripcion': row.descripcion,
            'activo': row.activo,
            'creador': row.creador,
            'creacion': row.creacion.isoformat() if row.creacion else None,
            'modificador': row.modificador,
            'modificacion': row.modificacion.isoformat() if row.modificacion else None,
        })
    return jsonify(items)


@accion_respuesta_origenes_bp.route('/api/accion_respuesta_origenes', methods=['POST'])
def create_accion_respuesta_origen():
    """Crear accion_respuesta_origen
    ---
    tags:
      - Accion Respuesta Origenes
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
        description: Origen creado
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
    data = request.get_json() or {}
    now = datetime.now(timezone.utc)

    query = db.text("""
        INSERT INTO accion_respuesta_origenes (nombre, descripcion, activo, creador, creacion, modificador, modificacion)
        VALUES (:nombre, :descripcion, :activo, :creador, :creacion, :modificador, :modificacion)
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
        db.session.rollback()
        return jsonify({'error': 'Failed to create accion_respuesta_origen'}), 500

    origen_id = row[0]
    db.session.commit()

    origen = db.session.execute(
        db.text("SELECT * FROM accion_respuesta_origenes WHERE id = :id"),
        {'id': origen_id},
    ).fetchone()

    if not origen:
        return jsonify({'error': 'accion_respuesta_origen not found after creation'}), 404

    return jsonify({  # type: ignore
        'id': origen.id,
        'nombre': origen.nombre,
        'descripcion': origen.descripcion,
        'activo': origen.activo,
        'creador': origen.creador,
        'creacion': origen.creacion.isoformat() if origen.creacion else None,
        'modificador': origen.modificador,
        'modificacion': origen.modificacion.isoformat() if origen.modificacion else None,
    }), 201


@accion_respuesta_origenes_bp.route('/api/accion_respuesta_origenes/<int:id>', methods=['GET'])
def get_accion_respuesta_origen(id):
    """Obtener accion_respuesta_origen por ID
    ---
    tags:
      - Accion Respuesta Origenes
    parameters:
      - name: id
        in: path
        type: integer
        required: true
    responses:
      200:
        description: Origen de acción de respuesta
      404:
        description: No encontrado
    """
    result = db.session.execute(
        db.text("SELECT * FROM accion_respuesta_origenes WHERE id = :id"),
        {'id': id},
    )
    origen = result.fetchone()

    if not origen:
        return jsonify({'error': 'accion_respuesta_origen no encontrado'}), 404

    return jsonify({
        'id': origen.id,
        'nombre': origen.nombre,
        'descripcion': origen.descripcion,
        'activo': origen.activo,
        'creador': origen.creador,
        'creacion': origen.creacion.isoformat() if origen.creacion else None,
        'modificador': origen.modificador,
        'modificacion': origen.modificacion.isoformat() if origen.modificacion else None,
    })


@accion_respuesta_origenes_bp.route('/api/accion_respuesta_origenes/<int:id>', methods=['PUT'])
def update_accion_respuesta_origen(id):
    """Actualizar accion_respuesta_origen
    ---
    tags:
      - Accion Respuesta Origenes
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
        description: Origen actualizado
      404:
        description: No encontrado
    """
    data = request.get_json() or {}
    now = datetime.now(timezone.utc)

    query = db.text("""
        UPDATE accion_respuesta_origenes
        SET nombre = :nombre,
            descripcion = :descripcion,
            activo = :activo,
            modificador = :modificador,
            modificacion = :modificacion
        WHERE id = :id
    """)

    result = db.session.execute(query, {
        'id': id,
        'nombre': data.get('nombre'),
        'descripcion': data.get('descripcion'),
        'activo': data.get('activo'),
        'modificador': data.get('modificador', 'Sistema'),
        'modificacion': now,
    })

    if getattr(result, 'rowcount', 0) == 0:  # type: ignore
        return jsonify({'error': 'accion_respuesta_origen no encontrado'}), 404

    db.session.commit()

    origen = db.session.execute(
        db.text("SELECT * FROM accion_respuesta_origenes WHERE id = :id"),
        {'id': id},
    ).fetchone()

    if not origen:
        return jsonify({'error': 'accion_respuesta_origen not found after update'}), 404

    return jsonify({  # type: ignore
        'id': origen.id,
        'nombre': origen.nombre,
        'descripcion': origen.descripcion,
        'activo': origen.activo,
        'creador': origen.creador,
        'creacion': origen.creacion.isoformat() if origen.creacion else None,
        'modificador': origen.modificador,
        'modificacion': origen.modificacion.isoformat() if origen.modificacion else None,
    })


@accion_respuesta_origenes_bp.route('/api/accion_respuesta_origenes/<int:id>', methods=['DELETE'])
def delete_accion_respuesta_origen(id):
    """Eliminar accion_respuesta_origen
    ---
    tags:
      - Accion Respuesta Origenes
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
        db.text("DELETE FROM accion_respuesta_origenes WHERE id = :id"),
        {'id': id},
    )

    if getattr(result, 'rowcount', 0) == 0:  # type: ignore
        return jsonify({'error': 'accion_respuesta_origen no encontrado'}), 404

    db.session.commit()
    return jsonify({'mensaje': 'accion_respuesta_origen eliminado correctamente'})
