from flask import request, jsonify
from acta_coe_estados import acta_coe_estados_bp
from models import db
from datetime import datetime, timezone

@acta_coe_estados_bp.route('/api/acta_coe_estados', methods=['GET'])
def get_acta_coe_estados():
    """Listar acta_coe_estados
    ---
    tags:
      - Acta Coe Estados
    responses:
        200:
          description: Lista de acta_coe_estados
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
    result = db.session.execute(db.text("SELECT * FROM acta_coe_estados"))
    acta_coe_estados = []
    for row in result:
        acta_coe_estados.append({  # type: ignore
            'id': row.id,
            'nombre': row.nombre,
            'descripcion': row.descripcion,
            'activo': row.activo,
            'creador': row.creador,
            'creacion': row.creacion.isoformat() if row.creacion else None,
            'modificador': row.modificador,
            'modificacion': row.modificacion.isoformat() if row.modificacion else None
        })
    return jsonify(acta_coe_estados)

@acta_coe_estados_bp.route('/api/acta_coe_estados', methods=['POST'])
def create_acta_coe_estado():
    """Crear acta_coe_estado
    ---
    tags:
      - Acta Coe Estados
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
        description: Acta coe estado creado
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
    now = datetime.now(timezone.utc)

    query = db.text("""
        INSERT INTO acta_coe_estados (nombre, descripcion, activo, creador, creacion, modificador, modificacion)
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
        'modificacion': now
    })

    row = result.fetchone()
    if row is None:
        db.session.rollback()
        return jsonify({'error': 'Failed to create acta_coe_estado'}), 500
    acta_coe_estado_id = row[0]
    db.session.commit()

    acta_coe_estado = db.session.execute(
        db.text("SELECT * FROM acta_coe_estados WHERE id = :id"),
        {'id': acta_coe_estado_id}
    ).fetchone()

    if not acta_coe_estado:
        return jsonify({'error': 'Acta coe estado not found after creation'}), 404

    return jsonify({  # type: ignore
        'id': acta_coe_estado.id,
        'nombre': acta_coe_estado.nombre,
        'descripcion': acta_coe_estado.descripcion,
        'activo': acta_coe_estado.activo,
        'creador': acta_coe_estado.creador,
        'creacion': acta_coe_estado.creacion.isoformat() if acta_coe_estado.creacion else None,
        'modificador': acta_coe_estado.modificador,
        'modificacion': acta_coe_estado.modificacion.isoformat() if acta_coe_estado.modificacion else None
    }), 201

@acta_coe_estados_bp.route('/api/acta_coe_estados/<int:id>', methods=['GET'])
def get_acta_coe_estado(id):
    """Obtener acta_coe_estado por ID
    ---
    tags:
      - Acta Coe Estados
    parameters:
      - name: id
        in: path
        type: integer
        required: true
    responses:
      200:
        description: Acta coe estado
      404:
        description: No encontrado
    """
    result = db.session.execute(
        db.text("SELECT * FROM acta_coe_estados WHERE id = :id"),
        {'id': id}
    )
    acta_coe_estado = result.fetchone()

    if not acta_coe_estado:
        return jsonify({'error': 'Acta coe estado no encontrado'}), 404

    return jsonify({
        'id': acta_coe_estado.id,
        'nombre': acta_coe_estado.nombre,
        'descripcion': acta_coe_estado.descripcion,
        'activo': acta_coe_estado.activo,
        'creador': acta_coe_estado.creador,
        'creacion': acta_coe_estado.creacion.isoformat() if acta_coe_estado.creacion else None,
        'modificador': acta_coe_estado.modificador,
        'modificacion': acta_coe_estado.modificacion.isoformat() if acta_coe_estado.modificacion else None
    })

@acta_coe_estados_bp.route('/api/acta_coe_estados/<int:id>', methods=['PUT'])
def update_acta_coe_estado(id):
    """Actualizar acta_coe_estado
    ---
    tags:
      - Acta Coe Estados
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
    responses:
      200:
        description: Acta coe estado actualizado
      404:
        description: No encontrado
    """
    data = request.get_json()
    now = datetime.now(timezone.utc)

    query = db.text("""
        UPDATE acta_coe_estados
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
        'modificacion': now
    })

    if getattr(result, 'rowcount', 0) == 0:  # type: ignore
        return jsonify({'error': 'Acta coe estado no encontrado'}), 404

    db.session.commit()

    acta_coe_estado = db.session.execute(
        db.text("SELECT * FROM acta_coe_estados WHERE id = :id"),
        {'id': id}
    ).fetchone()

    if not acta_coe_estado:
        return jsonify({'error': 'Acta coe estado not found after update'}), 404

    return jsonify({  # type: ignore
        'id': acta_coe_estado.id,
        'nombre': acta_coe_estado.nombre,
        'descripcion': acta_coe_estado.descripcion,
        'activo': acta_coe_estado.activo,
        'creador': acta_coe_estado.creador,
        'creacion': acta_coe_estado.creacion.isoformat() if acta_coe_estado.creacion else None,
        'modificador': acta_coe_estado.modificador,
        'modificacion': acta_coe_estado.modificacion.isoformat() if acta_coe_estado.modificacion else None
    })

@acta_coe_estados_bp.route('/api/acta_coe_estados/<int:id>', methods=['DELETE'])
def delete_acta_coe_estado(id):
    """Eliminar acta_coe_estado
    ---
    tags:
      - Acta Coe Estados
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
        db.text("DELETE FROM acta_coe_estados WHERE id = :id"),
        {'id': id}
    )

    if getattr(result, 'rowcount', 0) == 0:  # type: ignore
        return jsonify({'error': 'Acta coe estado no encontrado'}), 404

    db.session.commit()
    return jsonify({'mensaje': 'Acta coe estado eliminado correctamente'})
