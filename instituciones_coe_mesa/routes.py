from flask import request, jsonify
from instituciones_coe_mesa import instituciones_coe_mesa_bp
from models import db
from datetime import datetime, timezone


@instituciones_coe_mesa_bp.route('/api/instituciones_coe_mesa', methods=['GET'])
def get_instituciones_coe_mesa():
    """Listar instituciones_coe_mesa
    ---
    tags:
      - Instituciones Coe Mesa
    responses:
      200:
        description: Lista de relaciones instituciones_coe_mesa
        schema:
          type: array
          items:
            type: object
            properties:
              id: {type: integer}
              coe_id: {type: integer}
              mesa_id: {type: integer}
              institucion_id: {type: integer}
              activo: {type: boolean}
              creador: {type: string}
              creacion: {type: string}
              modificador: {type: string}
              modificacion: {type: string}
    """
    result = db.session.execute(db.text("SELECT * FROM instituciones_coe_mesa"))
    items = []
    for row in result:
        items.append({
            'id': row.id,
            'coe_id': row.coe_id,
            'mesa_id': row.mesa_id,
            'institucion_id': row.institucion_id,
            'activo': row.activo,
            'creador': row.creador,
            'creacion': row.creacion.isoformat() if row.creacion else None,
            'modificador': row.modificador,
            'modificacion': row.modificacion.isoformat() if row.modificacion else None
        })
    return jsonify(items)


@instituciones_coe_mesa_bp.route('/api/instituciones_coe_mesa/coe/<int:coe_id>/mesa/<int:mesa_id>', methods=['GET'])
def get_instituciones_by_coe_by_mesa(coe_id, mesa_id):
    """Obtener instituciones por COE y mesa
    ---
    tags:
      - Instituciones Coe Mesa
    parameters:
      - name: coe_id
        in: path
        type: integer
        required: true
      - name: mesa_id
        in: path
        type: integer
        required: true
    responses:
      200:
        description: Lista de instituciones asociadas al COE y mesa
        schema:
          type: array
          items:
            type: object
            properties:
              id: {type: integer}
              coe_id: {type: integer}
              mesa_id: {type: integer}
              institucion_id: {type: integer}
              institucion_categoria_id: {type: integer}
              nombre: {type: string}
              siglas: {type: string}
              observaciones: {type: string}
              activo: {type: boolean}
    """
    query = db.text("""
        SELECT
            icm.id,
            icm.coe_id,
            icm.mesa_id,
            icm.institucion_id,
            i.institucion_categoria_id,
            i.nombre,
            i.siglas,
            i.observaciones,
            icm.activo
        FROM instituciones_coe_mesa icm
        INNER JOIN instituciones i ON icm.institucion_id = i.id
        WHERE icm.coe_id = :coe_id
          AND icm.mesa_id = :mesa_id
          AND icm.activo = true
          AND i.activo = true
        ORDER BY i.nombre
    """)
    result = db.session.execute(query, {
        'coe_id': coe_id,
        'mesa_id': mesa_id,
    })
    items = []
    for row in result:
        items.append({
            'id': row.id,
            'coe_id': row.coe_id,
            'mesa_id': row.mesa_id,
            'institucion_id': row.institucion_id,
            'institucion_categoria_id': row.institucion_categoria_id,
            'nombre': row.nombre,
            'siglas': row.siglas,
            'observaciones': row.observaciones,
            'activo': row.activo,
        })
    return jsonify(items)


@instituciones_coe_mesa_bp.route('/api/instituciones_coe_mesa', methods=['POST'])
def create_institucion_coe_mesa():
    """Crear relacion instituciones_coe_mesa
    ---
    tags:
      - Instituciones Coe Mesa
    consumes:
      - application/json
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          required: [coe_id, mesa_id, institucion_id]
          properties:
            coe_id: {type: integer}
            mesa_id: {type: integer}
            institucion_id: {type: integer}
            activo: {type: boolean}
            creador: {type: string}
            modificador: {type: string}
    responses:
      201:
        description: Relacion creada
        schema:
          type: object
          properties:
            id: {type: integer}
            coe_id: {type: integer}
            mesa_id: {type: integer}
            institucion_id: {type: integer}
            activo: {type: boolean}
            creador: {type: string}
            creacion: {type: string}
            modificador: {type: string}
            modificacion: {type: string}
    """
    data = request.get_json() or {}
    required_fields = ['coe_id', 'mesa_id', 'institucion_id']
    missing_fields = [field for field in required_fields if field not in data]
    if missing_fields:
        return jsonify({'error': f"Campos requeridos faltantes: {', '.join(missing_fields)}"}), 400

    now = datetime.now(timezone.utc)

    query = db.text("""
        INSERT INTO instituciones_coe_mesa (
            coe_id, mesa_id, institucion_id, activo,
            creador, creacion, modificador, modificacion
        )
        VALUES (
            :coe_id, :mesa_id, :institucion_id, :activo,
            :creador, :creacion, :modificador, :modificacion
        )
        RETURNING id
    """)

    result = db.session.execute(query, {
        'coe_id': data['coe_id'],
        'mesa_id': data['mesa_id'],
        'institucion_id': data['institucion_id'],
        'activo': data.get('activo', True),
        'creador': data.get('creador', 'Sistema'),
        'creacion': now,
        'modificador': data.get('modificador', data.get('creador', 'Sistema')),
        'modificacion': now
    })

    row = result.fetchone()
    if row is None:
        db.session.rollback()
        return jsonify({'error': 'Failed to create relacion instituciones_coe_mesa'}), 500

    item_id = row[0]
    db.session.commit()

    item = db.session.execute(
        db.text("SELECT * FROM instituciones_coe_mesa WHERE id = :id"),
        {'id': item_id}
    ).fetchone()

    if item is None:
        return jsonify({'error': 'Relacion creada pero no encontrada'}), 500

    return jsonify({
        'id': item.id,
        'coe_id': item.coe_id,
        'mesa_id': item.mesa_id,
        'institucion_id': item.institucion_id,
        'activo': item.activo,
        'creador': item.creador,
        'creacion': item.creacion.isoformat() if item.creacion else None,
        'modificador': item.modificador,
        'modificacion': item.modificacion.isoformat() if item.modificacion else None
    }), 201


@instituciones_coe_mesa_bp.route('/api/instituciones_coe_mesa/<int:id>', methods=['GET'])
def get_institucion_coe_mesa(id):
    """Obtener relacion instituciones_coe_mesa por ID
    ---
    tags:
      - Instituciones Coe Mesa
    parameters:
      - name: id
        in: path
        type: integer
        required: true
    responses:
      200:
        description: Relacion encontrada
      404:
        description: No encontrada
    """
    result = db.session.execute(
        db.text("SELECT * FROM instituciones_coe_mesa WHERE id = :id"),
        {'id': id}
    )
    item = result.fetchone()

    if not item:
        return jsonify({'error': 'Relacion instituciones_coe_mesa no encontrada'}), 404

    return jsonify({
        'id': item.id,
        'coe_id': item.coe_id,
        'mesa_id': item.mesa_id,
        'institucion_id': item.institucion_id,
        'activo': item.activo,
        'creador': item.creador,
        'creacion': item.creacion.isoformat() if item.creacion else None,
        'modificador': item.modificador,
        'modificacion': item.modificacion.isoformat() if item.modificacion else None
    })


@instituciones_coe_mesa_bp.route('/api/instituciones_coe_mesa/<int:id>', methods=['PUT'])
def update_institucion_coe_mesa(id):
    """Actualizar relacion instituciones_coe_mesa
    ---
    tags:
      - Instituciones Coe Mesa
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
            coe_id: {type: integer}
            mesa_id: {type: integer}
            institucion_id: {type: integer}
            activo: {type: boolean}
            modificador: {type: string}
    responses:
      200:
        description: Relacion actualizada
      404:
        description: No encontrada
    """
    data = request.get_json() or {}
    now = datetime.now(timezone.utc)

    update_fields = []
    params = {
        'id': id,
        'modificador': data.get('modificador', 'Sistema'),
        'modificacion': now
    }

    for field in ['coe_id', 'mesa_id', 'institucion_id', 'activo']:
        if field in data:
            update_fields.append(f"{field} = :{field}")
            params[field] = data[field]

    update_fields.append('modificador = :modificador')
    update_fields.append('modificacion = :modificacion')

    query = db.text(f"""
        UPDATE instituciones_coe_mesa
        SET {', '.join(update_fields)}
        WHERE id = :id
    """)

    result = db.session.execute(query, params)

    if getattr(result, 'rowcount', 0) == 0:
        return jsonify({'error': 'Relacion instituciones_coe_mesa no encontrada'}), 404

    db.session.commit()

    item = db.session.execute(
        db.text("SELECT * FROM instituciones_coe_mesa WHERE id = :id"),
        {'id': id}
    ).fetchone()

    if item is None:
        return jsonify({'error': 'Relacion instituciones_coe_mesa no encontrada despues de actualizar'}), 404

    return jsonify({
        'id': item.id,
        'coe_id': item.coe_id,
        'mesa_id': item.mesa_id,
        'institucion_id': item.institucion_id,
        'activo': item.activo,
        'creador': item.creador,
        'creacion': item.creacion.isoformat() if item.creacion else None,
        'modificador': item.modificador,
        'modificacion': item.modificacion.isoformat() if item.modificacion else None
    })


@instituciones_coe_mesa_bp.route('/api/instituciones_coe_mesa/<int:id>', methods=['DELETE'])
def delete_institucion_coe_mesa(id):
    """Eliminar relacion instituciones_coe_mesa
    ---
    tags:
      - Instituciones Coe Mesa
    parameters:
      - name: id
        in: path
        type: integer
        required: true
    responses:
      200:
        description: Eliminada
      404:
        description: No encontrada
    """
    result = db.session.execute(
        db.text("DELETE FROM instituciones_coe_mesa WHERE id = :id"),
        {'id': id}
    )

    if getattr(result, 'rowcount', 0) == 0:
        return jsonify({'error': 'Relacion instituciones_coe_mesa no encontrada'}), 404

    db.session.commit()
    return jsonify({'mensaje': 'Relacion instituciones_coe_mesa eliminada correctamente'})
