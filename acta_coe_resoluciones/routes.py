from flask import request, jsonify
from acta_coe_resoluciones import acta_coe_resoluciones_bp
from models import db
from datetime import datetime, timezone

@acta_coe_resoluciones_bp.route('/api/acta_coe_resoluciones', methods=['GET'])
def get_acta_coe_resoluciones():
    """Listar acta_coe_resoluciones
    ---
    tags:
      - Acta Coe Resoluciones
    responses:
        200:
          description: Lista de acta_coe_resoluciones
          schema:
            type: array
            items:
              type: object
              properties:
                id: {type: integer}
                acta_coe_id: {type: integer}
                detalle: {type: string}
                acta_coe_resolucion_estado_id: {type: integer}
                activo: {type: boolean}
                creador: {type: string}
                creacion: {type: string}
                modificador: {type: string}
                modificacion: {type: string}
    """
    result = db.session.execute(db.text("SELECT * FROM acta_coe_resoluciones"))
    acta_coe_resoluciones = []
    for row in result:
        acta_coe_resoluciones.append({  # type: ignore
            'id': row.id,
            'acta_coe_id': row.acta_coe_id,
            'detalle': row.detalle,
            'acta_coe_resolucion_estado_id': row.acta_coe_resolucion_estado_id,
            'activo': row.activo,
            'creador': row.creador,
            'creacion': row.creacion.isoformat() if row.creacion else None,
            'modificador': row.modificador,
            'modificacion': row.modificacion.isoformat() if row.modificacion else None
        })
    return jsonify(acta_coe_resoluciones)

@acta_coe_resoluciones_bp.route('/api/acta_coe_resoluciones/acta_coe/<int:acta_coe_id>', methods=['GET'])
def get_acta_coe_resoluciones_by_acta_coe(acta_coe_id):
    """Obtener acta_coe_resoluciones por acta_coe
    ---
    tags:
      - Acta Coe Resoluciones
    parameters:
      - name: acta_coe_id
        in: path
        type: integer
        required: true
    responses:
        200:
          description: Lista de acta_coe_resoluciones
          schema:
            type: array
            items:
              type: object
              properties:
                id: {type: integer}
                acta_coe_id: {type: integer}
                detalle: {type: string}
                acta_coe_resolucion_estado_id: {type: integer}
                activo: {type: boolean}
                creador: {type: string}
                creacion: {type: string}
                modificador: {type: string}
                modificacion: {type: string}
    """
    result = db.session.execute(db.text("SELECT * FROM acta_coe_resoluciones WHERE acta_coe_id = :acta_coe_id"), {'acta_coe_id': acta_coe_id})
    acta_coe_resoluciones = []
    for row in result:
        acta_coe_resoluciones.append({  # type: ignore
            'id': row.id,
            'acta_coe_id': row.acta_coe_id,
            'detalle': row.detalle,
            'acta_coe_resolucion_estado_id': row.acta_coe_resolucion_estado_id,
            'activo': row.activo,
            'creador': row.creador,
            'creacion': row.creacion.isoformat() if row.creacion else None,
            'modificador': row.modificador,
            'modificacion': row.modificacion.isoformat() if row.modificacion else None
        })
    return jsonify(acta_coe_resoluciones)

@acta_coe_resoluciones_bp.route('/api/acta_coe_resoluciones', methods=['POST'])
def create_acta_coe_resolucion():
    """Crear acta_coe_resolucion
    ---
    tags:
      - Acta Coe Resoluciones
    consumes:
      - application/json
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          required: [acta_coe_id, acta_coe_resolucion_estado_id]
          properties:
            acta_coe_id: {type: integer}
            detalle: {type: string}
            acta_coe_resolucion_estado_id: {type: integer}
            activo: {type: boolean}
            creador: {type: string}
    responses:
      201:
        description: Acta COE resolucion creada
        schema:
          type: object
          properties:
            id: {type: integer}
            acta_coe_id: {type: integer}
            detalle: {type: string}
            acta_coe_resolucion_estado_id: {type: integer}
            activo: {type: boolean}
            creador: {type: string}
            creacion: {type: string}
            modificador: {type: string}
            modificacion: {type: string}
    """
    data = request.get_json()
    now = datetime.now(timezone.utc)

    query = db.text("""
        INSERT INTO acta_coe_resoluciones (acta_coe_id, detalle, acta_coe_resolucion_estado_id, activo, creador, creacion, modificador, modificacion)
        VALUES (:acta_coe_id, :detalle, :acta_coe_resolucion_estado_id, :activo, :creador, :creacion, :modificador, :modificacion)
        RETURNING id
    """)
    
    result = db.session.execute(query, {
        'acta_coe_id': data['acta_coe_id'],
        'detalle': data.get('detalle'),
        'acta_coe_resolucion_estado_id': data['acta_coe_resolucion_estado_id'],
        'activo': data.get('activo', True),
        'creador': data.get('creador', 'Sistema'),
        'creacion': now,
        'modificador': data.get('creador', 'Sistema'),
        'modificacion': now
    })

    row = result.fetchone()
    if row is None:
        db.session.rollback()
        return jsonify({'error': 'Failed to create acta_coe_resolucion'}), 500
    coe_acta_resolucion_id = row[0]
    db.session.commit()

    coe_acta_resolucion = db.session.execute(
        db.text("SELECT * FROM acta_coe_resoluciones WHERE id = :id"),
        {'id': coe_acta_resolucion_id}
    ).fetchone()

    if not coe_acta_resolucion:
        return jsonify({'error': 'Acta COE resolucion not found after creation'}), 404

    return jsonify({  # type: ignore
        'id': coe_acta_resolucion.id,
        'acta_coe_id': coe_acta_resolucion.acta_coe_id,
        'detalle': coe_acta_resolucion.detalle,
        'acta_coe_resolucion_estado_id': coe_acta_resolucion.acta_coe_resolucion_estado_id,
        'activo': coe_acta_resolucion.activo,
        'creador': coe_acta_resolucion.creador,
        'creacion': coe_acta_resolucion.creacion.isoformat() if coe_acta_resolucion.creacion else None,
        'modificador': coe_acta_resolucion.modificador,
        'modificacion': coe_acta_resolucion.modificacion.isoformat() if coe_acta_resolucion.modificacion else None
    }), 201

@acta_coe_resoluciones_bp.route('/api/acta_coe_resoluciones/<int:id>', methods=['GET'])
def get_acta_coe_resolucion(id):
    """Obtener acta_coe_resolucion por ID
    ---
    tags:
      - Acta Coe Resoluciones
    parameters:
      - name: id
        in: path
        type: integer
        required: true
    responses:
      200:
        description: Acta COE resolucion
        schema:
          type: object
          properties:
            id: {type: integer}
            acta_coe_id: {type: integer}
            detalle: {type: string}
            acta_coe_resolucion_estado_id: {type: integer}
            activo: {type: boolean}
            creador: {type: string}
            creacion: {type: string}
            modificador: {type: string}
            modificacion: {type: string}
      404:
        description: No encontrada
    """
    result = db.session.execute(
        db.text("SELECT * FROM acta_coe_resoluciones WHERE id = :id"),
        {'id': id}
    )
    coe_acta_resolucion = result.fetchone()

    if not coe_acta_resolucion:
        return jsonify({'error': 'Acta COE resolucion no encontrada'}), 404

    return jsonify({
        'id': coe_acta_resolucion.id,
        'acta_coe_id': coe_acta_resolucion.acta_coe_id,
        'detalle': coe_acta_resolucion.detalle,
        'acta_coe_resolucion_estado_id': coe_acta_resolucion.acta_coe_resolucion_estado_id,
        'activo': coe_acta_resolucion.activo,
        'creador': coe_acta_resolucion.creador,
        'creacion': coe_acta_resolucion.creacion.isoformat() if coe_acta_resolucion.creacion else None,
        'modificador': coe_acta_resolucion.modificador,
        'modificacion': coe_acta_resolucion.modificacion.isoformat() if coe_acta_resolucion.modificacion else None
    })

@acta_coe_resoluciones_bp.route('/api/acta_coe_resoluciones/<int:id>', methods=['PUT'])
def update_acta_coe_resolucion(id):
    """Actualizar acta_coe_resolucion
    ---
    tags:
      - Acta Coe Resoluciones
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
            acta_coe_id: {type: integer}
            detalle: {type: string}
            acta_coe_resolucion_estado_id: {type: integer}
            activo: {type: boolean}
    responses:
      200:
        description: Acta COE resolucion actualizada
      404:
        description: No encontrada
    """
    data = request.get_json()
    now = datetime.now(timezone.utc)

    query = db.text("""
        UPDATE acta_coe_resoluciones
        SET acta_coe_id = :acta_coe_id,
            detalle = :detalle,
            acta_coe_resolucion_estado_id = :acta_coe_resolucion_estado_id,
            activo = :activo,
            modificador = :modificador,
            modificacion = :modificacion
        WHERE id = :id
    """)

    result = db.session.execute(query, {
        'id': id,
        'acta_coe_id': data.get('acta_coe_id'),
        'detalle': data.get('detalle'),
        'acta_coe_resolucion_estado_id': data.get('acta_coe_resolucion_estado_id'),
        'activo': data.get('activo'),
        'modificador': data.get('modificador', 'Sistema'),
        'modificacion': now
    })

    if getattr(result, 'rowcount', 0) == 0:  # type: ignore
        return jsonify({'error': 'Acta COE resolucion no encontrada'}), 404

    db.session.commit()

    coe_acta_resolucion = db.session.execute(
        db.text("SELECT * FROM acta_coe_resoluciones WHERE id = :id"),
        {'id': id}
    ).fetchone()

    if not coe_acta_resolucion:
        return jsonify({'error': 'Acta COE resolucion not found after update'}), 404

    return jsonify({  # type: ignore
        'id': coe_acta_resolucion.id,
        'acta_coe_id': coe_acta_resolucion.acta_coe_id,
        'detalle': coe_acta_resolucion.detalle,
        'acta_coe_resolucion_estado_id': coe_acta_resolucion.acta_coe_resolucion_estado_id,
        'activo': coe_acta_resolucion.activo,
        'creador': coe_acta_resolucion.creador,
        'creacion': coe_acta_resolucion.creacion.isoformat() if coe_acta_resolucion.creacion else None,
        'modificador': coe_acta_resolucion.modificador,
        'modificacion': coe_acta_resolucion.modificacion.isoformat() if coe_acta_resolucion.modificacion else None
    })

@acta_coe_resoluciones_bp.route('/api/acta_coe_resoluciones/<int:id>', methods=['DELETE'])
def delete_acta_coe_resolucion(id):
    """Eliminar acta_coe_resolucion
    ---
    tags:
      - Acta Coe Resoluciones
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
        db.text("DELETE FROM acta_coe_resoluciones WHERE id = :id"),
        {'id': id}
    )

    if getattr(result, 'rowcount', 0) == 0:  # type: ignore
        return jsonify({'error': 'Acta COE resolucion no encontrada'}), 404

    db.session.commit()
    return jsonify({'mensaje': 'Acta COE resolucion eliminada correctamente'})