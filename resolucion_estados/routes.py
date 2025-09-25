from flask import request, jsonify
from resolucion_estados import resolucion_estados_bp
from models import db
from datetime import datetime, timezone

@resolucion_estados_bp.route('/api/resolucion_estados', methods=['GET'])
def get_resolucion_estados():
    """Listar resolucion_estados
    ---
    tags:
      - Resolucion Estados
    responses:
        200:
          description: Lista de resolucion_estados
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
    result = db.session.execute(db.text("SELECT * FROM resolucion_estados"))
    resolucion_estados = []
    for row in result:
        resolucion_estados.append({  # type: ignore
            'id': row.id,
            'nombre': row.nombre,
            'descripcion': row.descripcion,
            'activo': row.activo,
            'creador': row.creador,
            'creacion': row.creacion.isoformat() if row.creacion else None,
            'modificador': row.modificador,
            'modificacion': row.modificacion.isoformat() if row.modificacion else None
        })
    return jsonify(resolucion_estados)

@resolucion_estados_bp.route('/api/resolucion_estados', methods=['POST'])
def create_resolucion_estado():
    """Crear resolucion_estado
    ---
    tags:
      - Resolucion Estados
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
        description: Resolucion estado creado
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
        INSERT INTO resolucion_estados (nombre, descripcion, activo, creador, creacion, modificador, modificacion)
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
        return jsonify({'error': 'Failed to create resolucion_estado'}), 500
    resolucion_estado_id = row[0]
    db.session.commit()

    resolucion_estado = db.session.execute(
        db.text("SELECT * FROM resolucion_estados WHERE id = :id"),
        {'id': resolucion_estado_id}
    ).fetchone()

    if not resolucion_estado:
        return jsonify({'error': 'Resolucion estado not found after creation'}), 404

    return jsonify({  # type: ignore
        'id': resolucion_estado.id,
        'nombre': resolucion_estado.nombre,
        'descripcion': resolucion_estado.descripcion,
        'activo': resolucion_estado.activo,
        'creador': resolucion_estado.creador,
        'creacion': resolucion_estado.creacion.isoformat() if resolucion_estado.creacion else None,
        'modificador': resolucion_estado.modificador,
        'modificacion': resolucion_estado.modificacion.isoformat() if resolucion_estado.modificacion else None
    }), 201

@resolucion_estados_bp.route('/api/resolucion_estados/<int:id>', methods=['GET'])
def get_resolucion_estado(id):
    """Obtener resolucion_estado por ID
    ---
    tags:
      - Resolucion Estados
    parameters:
      - name: id
        in: path
        type: integer
        required: true
    responses:
      200:
        description: Resolucion estado
      404:
        description: No encontrado
    """
    result = db.session.execute(
        db.text("SELECT * FROM resolucion_estados WHERE id = :id"),
        {'id': id}
    )
    resolucion_estado = result.fetchone()

    if not resolucion_estado:
        return jsonify({'error': 'Resolucion estado no encontrado'}), 404

    return jsonify({
        'id': resolucion_estado.id,
        'nombre': resolucion_estado.nombre,
        'descripcion': resolucion_estado.descripcion,
        'activo': resolucion_estado.activo,
        'creador': resolucion_estado.creador,
        'creacion': resolucion_estado.creacion.isoformat() if resolucion_estado.creacion else None,
        'modificador': resolucion_estado.modificador,
        'modificacion': resolucion_estado.modificacion.isoformat() if resolucion_estado.modificacion else None
    })

@resolucion_estados_bp.route('/api/resolucion_estados/<int:id>', methods=['PUT'])
def update_resolucion_estado(id):
    """Actualizar resolucion_estado
    ---
    tags:
      - Resolucion Estados
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
        description: Resolucion estado actualizado
      404:
        description: No encontrado
    """
    data = request.get_json()
    now = datetime.now(timezone.utc)

    query = db.text("""
        UPDATE resolucion_estados
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

    if result.rowcount == 0:  # type: ignore
        return jsonify({'error': 'Resolucion estado no encontrado'}), 404

    db.session.commit()

    resolucion_estado = db.session.execute(
        db.text("SELECT * FROM resolucion_estados WHERE id = :id"),
        {'id': id}
    ).fetchone()

    if not resolucion_estado:
        return jsonify({'error': 'Resolucion estado not found after update'}), 404

    return jsonify({  # type: ignore
        'id': resolucion_estado.id,
        'nombre': resolucion_estado.nombre,
        'descripcion': resolucion_estado.descripcion,
        'activo': resolucion_estado.activo,
        'creador': resolucion_estado.creador,
        'creacion': resolucion_estado.creacion.isoformat() if resolucion_estado.creacion else None,
        'modificador': resolucion_estado.modificador,
        'modificacion': resolucion_estado.modificacion.isoformat() if resolucion_estado.modificacion else None
    })

@resolucion_estados_bp.route('/api/resolucion_estados/<int:id>', methods=['DELETE'])
def delete_resolucion_estado(id):
    """Eliminar resolucion_estado
    ---
    tags:
      - Resolucion Estados
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
        db.text("DELETE FROM resolucion_estados WHERE id = :id"),
        {'id': id}
    )

    if result.rowcount == 0:  # type: ignore
        return jsonify({'error': 'Resolucion estado no encontrado'}), 404

    db.session.commit()
    return jsonify({'mensaje': 'Resolucion estado eliminado correctamente'})