from flask import request, jsonify
from acta_coe_resolucion_mesas import acta_coe_resolucion_mesas_bp
from models import db
from datetime import datetime, timezone


@acta_coe_resolucion_mesas_bp.route('/api/acta_coe_resolucion_mesas', methods=['GET'])
def get_acta_coe_resolucion_mesas():
    """Listar acta_coe_resolucion_mesas
    ---
    tags:
      - Acta Coe Resolucion Mesas
    responses:
      200:
        description: Lista de acta_coe_resolucion_mesas
        schema:
          type: array
          items:
            type: object
            properties:
              id: {type: integer}
              acta_coe_resolucion_id: {type: integer}
              mesa_id: {type: integer}
              responsable: {type: string}
              acta_coe_resolucion_mesa_estado_id: {type: integer}
              activo: {type: boolean}
              creador: {type: string}
              creacion: {type: string}
              modificador: {type: string}
              modificacion: {type: string}
    """
    result = db.session.execute(db.text("SELECT * FROM acta_coe_resolucion_mesas"))
    items = []
    for row in result:
        items.append({  # type: ignore
            'id': row.id,
            'acta_coe_resolucion_id': row.acta_coe_resolucion_id,
            'mesa_id': row.mesa_id,
            'responsable': row.responsable,
            'acta_coe_resolucion_mesa_estado_id': row.acta_coe_resolucion_mesa_estado_id,
            'activo': row.activo,
            'creador': row.creador,
            'creacion': row.creacion.isoformat() if row.creacion else None,
            'modificador': row.modificador,
            'modificacion': row.modificacion.isoformat() if row.modificacion else None,
        })
    return jsonify(items)


@acta_coe_resolucion_mesas_bp.route('/api/acta_coe_resolucion_mesas/acta_coe_resolucion/<int:acta_coe_resolucion_id>', methods=['GET'])
def get_acta_coe_resolucion_mesas_by_resolucion(acta_coe_resolucion_id):
    """Obtener acta_coe_resolucion_mesas por acta_coe_resolucion
    ---
    tags:
      - Acta Coe Resolucion Mesas
    parameters:
      - name: acta_coe_resolucion_id
        in: path
        type: integer
        required: true
    responses:
      200:
        description: Lista de acta_coe_resolucion_mesas
        schema:
          type: array
          items:
            type: object
            properties:
              id: {type: integer}
              acta_coe_resolucion_id: {type: integer}
              mesa_id: {type: integer}
              responsable: {type: string}
              acta_coe_resolucion_mesa_estado_id: {type: integer}
              activo: {type: boolean}
              creador: {type: string}
              creacion: {type: string}
              modificador: {type: string}
              modificacion: {type: string}
    """
    result = db.session.execute(
        db.text("SELECT * FROM acta_coe_resolucion_mesas WHERE acta_coe_resolucion_id = :acta_coe_resolucion_id"),
        {'acta_coe_resolucion_id': acta_coe_resolucion_id}
    )
    items = []
    for row in result:
        items.append({  # type: ignore
            'id': row.id,
            'acta_coe_resolucion_id': row.acta_coe_resolucion_id,
            'mesa_id': row.mesa_id,
            'responsable': row.responsable,
            'acta_coe_resolucion_mesa_estado_id': row.acta_coe_resolucion_mesa_estado_id,
            'activo': row.activo,
            'creador': row.creador,
            'creacion': row.creacion.isoformat() if row.creacion else None,
            'modificador': row.modificador,
            'modificacion': row.modificacion.isoformat() if row.modificacion else None,
        })
    return jsonify(items)


@acta_coe_resolucion_mesas_bp.route('/api/acta_coe_resolucion_mesas', methods=['POST'])
def create_acta_coe_resolucion_mesa():
    """Crear acta_coe_resolucion_mesa
    ---
    tags:
      - Acta Coe Resolucion Mesas
    consumes:
      - application/json
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          required: [acta_coe_resolucion_id, mesa_id, acta_coe_resolucion_mesa_estado_id]
          properties:
            acta_coe_resolucion_id: {type: integer, description: 'ID de la resolución del acta COE'}
            mesa_id: {type: integer, description: 'ID de la mesa'}
            responsable: {type: string, description: 'Nombre del responsable de la mesa'}
            acta_coe_resolucion_mesa_estado_id: {type: integer, description: 'ID del estado de la resolución de la mesa'}
            activo: {type: boolean, description: 'Indica si el registro está activo'}
            creador: {type: string, description: 'Usuario que creó el registro'}
    responses:
      201:
        description: Acta COE resolucion mesa creada
        schema:
          type: object
          properties:
            id: {type: integer, description: 'ID del registro'}
            acta_coe_resolucion_id: {type: integer, description: 'ID de la resolución del acta COE'}
            mesa_id: {type: integer, description: 'ID de la mesa'}
            responsable: {type: string, description: 'Nombre del responsable de la mesa'}
            acta_coe_resolucion_mesa_estado_id: {type: integer, description: 'ID del estado de la resolución de la mesa'}
            activo: {type: boolean, description: 'Indica si el registro está activo'}
            creador: {type: string, description: 'Usuario que creó el registro'}
            creacion: {type: string, format: date-time, description: 'Fecha de creación del registro'}
            modificador: {type: string, description: 'Usuario que modificó por última vez el registro'}
            modificacion: {type: string, format: date-time, description: 'Fecha de la última modificación'}
    """
    data = request.get_json()
    now = datetime.now(timezone.utc)

    query = db.text("""
        INSERT INTO acta_coe_resolucion_mesas (acta_coe_resolucion_id, mesa_id, responsable, acta_coe_resolucion_mesa_estado_id, activo, creador, creacion, modificador, modificacion)
        VALUES (:acta_coe_resolucion_id, :mesa_id, :responsable, :acta_coe_resolucion_mesa_estado_id, :activo, :creador, :creacion, :modificador, :modificacion)
        RETURNING id
    """)

    result = db.session.execute(query, {
        'acta_coe_resolucion_id': data['acta_coe_resolucion_id'],
        'mesa_id': data['mesa_id'],
        'responsable': data.get('responsable'),
        'acta_coe_resolucion_mesa_estado_id': data['acta_coe_resolucion_mesa_estado_id'],
        'activo': data.get('activo', True),
        'creador': data.get('creador', 'Sistema'),
        'creacion': now,
        'modificador': data.get('creador', 'Sistema'),
        'modificacion': now,
    })

    row = result.fetchone()
    if row is None:
        db.session.rollback()
        return jsonify({'error': 'Failed to create acta_coe_resolucion_mesa'}), 500

    new_id = row[0]
    db.session.commit()

    item = db.session.execute(
        db.text("SELECT * FROM acta_coe_resolucion_mesas WHERE id = :id"),
        {'id': new_id}
    ).fetchone()

    if not item:
        return jsonify({'error': 'acta_coe_resolucion_mesa not found after creation'}), 404

    return jsonify({  # type: ignore
        'id': item.id,
        'acta_coe_resolucion_id': item.acta_coe_resolucion_id,
        'mesa_id': item.mesa_id,
        'responsable': item.responsable,
        'acta_coe_resolucion_mesa_estado_id': item.acta_coe_resolucion_mesa_estado_id,
        'activo': item.activo,
        'creador': item.creador,
        'creacion': item.creacion.isoformat() if item.creacion else None,
        'modificador': item.modificador,
        'modificacion': item.modificacion.isoformat() if item.modificacion else None,
    }), 201


@acta_coe_resolucion_mesas_bp.route('/api/acta_coe_resolucion_mesas/<int:id>', methods=['GET'])
def get_acta_coe_resolucion_mesa(id):
    """Obtener acta_coe_resolucion_mesa por ID
    ---
    tags:
      - Acta Coe Resolucion Mesas
    parameters:
      - name: id
        in: path
        type: integer
        required: true
    responses:
      200:
        description: Acta COE resolucion mesa
        schema:
          type: object
          properties:
            id: {type: integer, description: 'ID del registro'}
            acta_coe_resolucion_id: {type: integer, description: 'ID de la resolución del acta COE'}
            mesa_id: {type: integer, description: 'ID de la mesa'}
            responsable: {type: string, description: 'Nombre del responsable de la mesa'}
            acta_coe_resolucion_mesa_estado_id: {type: integer, description: 'ID del estado de la resolución de la mesa'}
            activo: {type: boolean, description: 'Indica si el registro está activo'}
            creador: {type: string, description: 'Usuario que creó el registro'}
            creacion: {type: string, format: date-time, description: 'Fecha de creación del registro'}
            modificador: {type: string, description: 'Usuario que modificó por última vez el registro'}
            modificacion: {type: string, format: date-time, description: 'Fecha de la última modificación'}
      404:
        description: No encontrada
    """
    result = db.session.execute(
        db.text("SELECT * FROM acta_coe_resolucion_mesas WHERE id = :id"),
        {'id': id}
    )
    item = result.fetchone()

    if not item:
        return jsonify({'error': 'Acta COE resolucion mesa no encontrada'}), 404

    return jsonify({
        'id': item.id,
        'acta_coe_resolucion_id': item.acta_coe_resolucion_id,
        'mesa_id': item.mesa_id,
        'responsable': item.responsable,
        'acta_coe_resolucion_mesa_estado_id': item.acta_coe_resolucion_mesa_estado_id,
        'activo': item.activo,
        'creador': item.creador,
        'creacion': item.creacion.isoformat() if item.creacion else None,
        'modificador': item.modificador,
        'modificacion': item.modificacion.isoformat() if item.modificacion else None,
    })


@acta_coe_resolucion_mesas_bp.route('/api/acta_coe_resolucion_mesas/<int:id>', methods=['PUT'])
def update_acta_coe_resolucion_mesa(id):
    """Actualizar acta_coe_resolucion_mesa
    ---
    tags:
      - Acta Coe Resolucion Mesas
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
            acta_coe_resolucion_id: {type: integer}
            mesa_id: {type: integer}
            fecha_cumplimiento: {type: string}
            responsable: {type: string}
            acta_coe_resolucion_mesa_estado_id: {type: integer}
            activo: {type: boolean}
    responses:
      200:
        description: Acta COE resolucion mesa actualizada
      404:
        description: No encontrada
    """
    data = request.get_json()
    now = datetime.now(timezone.utc)

    query = db.text("""
        UPDATE acta_coe_resolucion_mesas
        SET acta_coe_resolucion_id = :acta_coe_resolucion_id,
            mesa_id = :mesa_id,
            responsable = :responsable,
            acta_coe_resolucion_mesa_estado_id = :acta_coe_resolucion_mesa_estado_id,
            activo = :activo,
            modificador = :modificador,
            modificacion = :modificacion
        WHERE id = :id
    """)

    result = db.session.execute(query, {
        'id': id,
        'acta_coe_resolucion_id': data.get('acta_coe_resolucion_id'),
        'mesa_id': data.get('mesa_id'),
        'responsable': data.get('responsable'),
        'acta_coe_resolucion_mesa_estado_id': data.get('acta_coe_resolucion_mesa_estado_id'),
        'activo': data.get('activo'),
        'modificador': data.get('modificador', 'Sistema'),
        'modificacion': now,
    })

    if getattr(result, 'rowcount', 0) == 0:  # type: ignore
        return jsonify({'error': 'Acta COE resolucion mesa no encontrada'}), 404

    db.session.commit()

    item = db.session.execute(
        db.text("SELECT * FROM acta_coe_resolucion_mesas WHERE id = :id"),
        {'id': id}
    ).fetchone()

    if not item:
        return jsonify({'error': 'acta_coe_resolucion_mesa not found after update'}), 404

    return jsonify({  # type: ignore
        'id': item.id,
        'acta_coe_resolucion_id': item.acta_coe_resolucion_id,
        'mesa_id': item.mesa_id,
        'responsable': item.responsable,
        'acta_coe_resolucion_mesa_estado_id': item.acta_coe_resolucion_mesa_estado_id,
        'activo': item.activo,
        'creador': item.creador,
        'creacion': item.creacion.isoformat() if item.creacion else None,
        'modificador': item.modificador,
        'modificacion': item.modificacion.isoformat() if item.modificacion else None,
    })


@acta_coe_resolucion_mesas_bp.route('/api/acta_coe_resolucion_mesas/<int:id>', methods=['DELETE'])
def delete_acta_coe_resolucion_mesa(id):
    """Eliminar acta_coe_resolucion_mesa
    ---
    tags:
      - Acta Coe Resolucion Mesas
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
        db.text("DELETE FROM acta_coe_resolucion_mesas WHERE id = :id"),
        {'id': id}
    )

    if getattr(result, 'rowcount', 0) == 0:  # type: ignore
        return jsonify({'error': 'Acta COE resolucion mesa no encontrada'}), 404

    db.session.commit()
    return jsonify({'mensaje': 'Acta COE resolucion mesa eliminada correctamente'})
