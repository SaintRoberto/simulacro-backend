from flask import request, jsonify
from coe_acta_resoluciones import coe_acta_resoluciones_bp
from models import db
from datetime import datetime, timezone

@coe_acta_resoluciones_bp.route('/api/coe_acta_resoluciones', methods=['GET'])
def get_coe_acta_resoluciones():
    """Listar coe_acta_resoluciones
    ---
    tags:
      - Coe Acta Resoluciones
    responses:
        200:
          description: Lista de coe_acta_resoluciones
          schema:
            type: array
            items:
              type: object
              properties:
                id: {type: integer}
                coe_acta_id: {type: integer}
                mesa_id: {type: integer}
                detalle: {type: string}
                fecha_cumplimiento: {type: string}
                responsable: {type: string}
                resolucion_estado_id: {type: integer}
                activo: {type: boolean}
                creador: {type: string}
                creacion: {type: string}
                modificador: {type: string}
                modificacion: {type: string}
    """
    result = db.session.execute(db.text("SELECT * FROM coe_acta_resoluciones"))
    coe_acta_resoluciones = []
    for row in result:
        coe_acta_resoluciones.append({  # type: ignore
            'id': row.id,
            'coe_acta_id': row.coe_acta_id,
            'mesa_id': row.mesa_id,
            'detalle': row.detalle,
            'fecha_cumplimiento': row.fecha_cumplimiento.isoformat() if row.fecha_cumplimiento else None,
            'responsable': row.responsable,
            'resolucion_estado_id': row.resolucion_estado_id,
            'activo': row.activo,
            'creador': row.creador,
            'creacion': row.creacion.isoformat() if row.creacion else None,
            'modificador': row.modificador,
            'modificacion': row.modificacion.isoformat() if row.modificacion else None
        })
    return jsonify(coe_acta_resoluciones)

@coe_acta_resoluciones_bp.route('/api/coe_acta_resoluciones/coe_acta/<int:coe_acta_id>', methods=['GET'])
def get_coe_acta_resoluciones_by_coe_acta(coe_acta_id):
    """Obtener coe_acta_resoluciones por coe_acta
    ---
    tags:
      - Coe Acta Resoluciones
    parameters:
      - name: coe_acta_id
        in: path
        type: integer
        required: true
    responses:
        200:
          description: Lista de coe_acta_resoluciones
          schema:
            type: array
            items:
              type: object
              properties:
                id: {type: integer}
                coe_acta_id: {type: integer}
                mesa_id: {type: integer}
                detalle: {type: string}
                fecha_cumplimiento: {type: string}
                responsable: {type: string}
                resolucion_estado_id: {type: integer}
                activo: {type: boolean}
                creador: {type: string}
                creacion: {type: string}
                modificador: {type: string}
                modificacion: {type: string}
    """
    result = db.session.execute(db.text("SELECT * FROM coe_acta_resoluciones WHERE coe_acta_id = :coe_acta_id"), {'coe_acta_id': coe_acta_id})
    coe_acta_resoluciones = []
    for row in result:
        coe_acta_resoluciones.append({  # type: ignore
            'id': row.id,
            'coe_acta_id': row.coe_acta_id,
            'mesa_id': row.mesa_id,
            'detalle': row.detalle,
            'fecha_cumplimiento': row.fecha_cumplimiento.isoformat() if row.fecha_cumplimiento else None,
            'responsable': row.responsable,
            'resolucion_estado_id': row.resolucion_estado_id,
            'activo': row.activo,
            'creador': row.creador,
            'creacion': row.creacion.isoformat() if row.creacion else None,
            'modificador': row.modificador,
            'modificacion': row.modificacion.isoformat() if row.modificacion else None
        })
    return jsonify(coe_acta_resoluciones)

@coe_acta_resoluciones_bp.route('/api/coe_acta_resoluciones', methods=['POST'])
def create_coe_acta_resolucion():
    """Crear coe_acta_resolucion
    ---
    tags:
      - Coe Acta Resoluciones
    consumes:
      - application/json
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          required: [coe_acta_id, mesa_id, resolucion_estado_id]
          properties:
            coe_acta_id: {type: integer}
            mesa_id: {type: integer}
            detalle: {type: string}
            fecha_cumplimiento: {type: string, format: date-time}
            responsable: {type: string}
            resolucion_estado_id: {type: integer}
            activo: {type: boolean}
            creador: {type: string}
    responses:
      201:
        description: Coe acta resolucion creada
        schema:
          type: object
          properties:
            id: {type: integer}
            coe_acta_id: {type: integer}
            mesa_id: {type: integer}
            detalle: {type: string}
            fecha_cumplimiento: {type: string}
            responsable: {type: string}
            resolucion_estado_id: {type: integer}
            activo: {type: boolean}
            creador: {type: string}
            creacion: {type: string}
            modificador: {type: string}
            modificacion: {type: string}
    """
    data = request.get_json()
    now = datetime.now(timezone.utc)

    query = db.text("""
        INSERT INTO coe_acta_resoluciones (coe_acta_id, mesa_id, detalle, fecha_cumplimiento, responsable, resolucion_estado_id, activo, creador, creacion, modificador, modificacion)
        VALUES (:coe_acta_id, :mesa_id, :detalle, :fecha_cumplimiento, :responsable, :resolucion_estado_id, :activo, :creador, :creacion, :modificador, :modificacion)
        RETURNING id
    """)

    result = db.session.execute(query, {
        'coe_acta_id': data['coe_acta_id'],
        'mesa_id': data['mesa_id'],
        'detalle': data.get('detalle'),
        'fecha_cumplimiento': data.get('fecha_cumplimiento'),
        'responsable': data.get('responsable'),
        'resolucion_estado_id': data['resolucion_estado_id'],
        'activo': data.get('activo', True),
        'creador': data.get('creador', 'Sistema'),
        'creacion': now,
        'modificador': data.get('creador', 'Sistema'),
        'modificacion': now
    })

    row = result.fetchone()
    if row is None:
        db.session.rollback()
        return jsonify({'error': 'Failed to create coe_acta_resolucion'}), 500
    coe_acta_resolucion_id = row[0]
    db.session.commit()

    coe_acta_resolucion = db.session.execute(
        db.text("SELECT * FROM coe_acta_resoluciones WHERE id = :id"),
        {'id': coe_acta_resolucion_id}
    ).fetchone()

    if not coe_acta_resolucion:
        return jsonify({'error': 'Coe acta resolucion not found after creation'}), 404

    return jsonify({  # type: ignore
        'id': coe_acta_resolucion.id,
        'coe_acta_id': coe_acta_resolucion.coe_acta_id,
        'mesa_id': coe_acta_resolucion.mesa_id,
        'detalle': coe_acta_resolucion.detalle,
        'fecha_cumplimiento': coe_acta_resolucion.fecha_cumplimiento.isoformat() if coe_acta_resolucion.fecha_cumplimiento else None,
        'responsable': coe_acta_resolucion.responsable,
        'resolucion_estado_id': coe_acta_resolucion.resolucion_estado_id,
        'activo': coe_acta_resolucion.activo,
        'creador': coe_acta_resolucion.creador,
        'creacion': coe_acta_resolucion.creacion.isoformat() if coe_acta_resolucion.creacion else None,
        'modificador': coe_acta_resolucion.modificador,
        'modificacion': coe_acta_resolucion.modificacion.isoformat() if coe_acta_resolucion.modificacion else None
    }), 201

@coe_acta_resoluciones_bp.route('/api/coe_acta_resoluciones/<int:id>', methods=['GET'])
def get_coe_acta_resolucion(id):
    """Obtener coe_acta_resolucion por ID
    ---
    tags:
      - Coe Acta Resoluciones
    parameters:
      - name: id
        in: path
        type: integer
        required: true
    responses:
      200:
        description: Coe acta resolucion
      404:
        description: No encontrada
    """
    result = db.session.execute(
        db.text("SELECT * FROM coe_acta_resoluciones WHERE id = :id"),
        {'id': id}
    )
    coe_acta_resolucion = result.fetchone()

    if not coe_acta_resolucion:
        return jsonify({'error': 'Coe acta resolucion no encontrada'}), 404

    return jsonify({
        'id': coe_acta_resolucion.id,
        'coe_acta_id': coe_acta_resolucion.coe_acta_id,
        'mesa_id': coe_acta_resolucion.mesa_id,
        'detalle': coe_acta_resolucion.detalle,
        'fecha_cumplimiento': coe_acta_resolucion.fecha_cumplimiento.isoformat() if coe_acta_resolucion.fecha_cumplimiento else None,
        'responsable': coe_acta_resolucion.responsable,
        'resolucion_estado_id': coe_acta_resolucion.resolucion_estado_id,
        'activo': coe_acta_resolucion.activo,
        'creador': coe_acta_resolucion.creador,
        'creacion': coe_acta_resolucion.creacion.isoformat() if coe_acta_resolucion.creacion else None,
        'modificador': coe_acta_resolucion.modificador,
        'modificacion': coe_acta_resolucion.modificacion.isoformat() if coe_acta_resolucion.modificacion else None
    })

@coe_acta_resoluciones_bp.route('/api/coe_acta_resoluciones/<int:id>', methods=['PUT'])
def update_coe_acta_resolucion(id):
    """Actualizar coe_acta_resolucion
    ---
    tags:
      - Coe Acta Resoluciones
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
            coe_acta_id: {type: integer}
            mesa_id: {type: integer}
            detalle: {type: string}
            fecha_cumplimiento: {type: string, format: date-time}
            responsable: {type: string}
            resolucion_estado_id: {type: integer}
            activo: {type: boolean}
    responses:
      200:
        description: Coe acta resolucion actualizada
      404:
        description: No encontrada
    """
    data = request.get_json()
    now = datetime.now(timezone.utc)

    query = db.text("""
        UPDATE coe_acta_resoluciones
        SET coe_acta_id = :coe_acta_id,
            mesa_id = :mesa_id,
            detalle = :detalle,
            fecha_cumplimiento = :fecha_cumplimiento,
            responsable = :responsable,
            resolucion_estado_id = :resolucion_estado_id,
            activo = :activo,
            modificador = :modificador,
            modificacion = :modificacion
        WHERE id = :id
    """)

    result = db.session.execute(query, {
        'id': id,
        'coe_acta_id': data.get('coe_acta_id'),
        'mesa_id': data.get('mesa_id'),
        'detalle': data.get('detalle'),
        'fecha_cumplimiento': data.get('fecha_cumplimiento'),
        'responsable': data.get('responsable'),
        'resolucion_estado_id': data.get('resolucion_estado_id'),
        'activo': data.get('activo'),
        'modificador': data.get('modificador', 'Sistema'),
        'modificacion': now
    })

    if result.rowcount == 0:  # type: ignore
        return jsonify({'error': 'Coe acta resolucion no encontrada'}), 404

    db.session.commit()

    coe_acta_resolucion = db.session.execute(
        db.text("SELECT * FROM coe_acta_resoluciones WHERE id = :id"),
        {'id': id}
    ).fetchone()

    if not coe_acta_resolucion:
        return jsonify({'error': 'Coe acta resolucion not found after update'}), 404

    return jsonify({  # type: ignore
        'id': coe_acta_resolucion.id,
        'coe_acta_id': coe_acta_resolucion.coe_acta_id,
        'mesa_id': coe_acta_resolucion.mesa_id,
        'detalle': coe_acta_resolucion.detalle,
        'fecha_cumplimiento': coe_acta_resolucion.fecha_cumplimiento.isoformat() if coe_acta_resolucion.fecha_cumplimiento else None,
        'responsable': coe_acta_resolucion.responsable,
        'resolucion_estado_id': coe_acta_resolucion.resolucion_estado_id,
        'activo': coe_acta_resolucion.activo,
        'creador': coe_acta_resolucion.creador,
        'creacion': coe_acta_resolucion.creacion.isoformat() if coe_acta_resolucion.creacion else None,
        'modificador': coe_acta_resolucion.modificador,
        'modificacion': coe_acta_resolucion.modificacion.isoformat() if coe_acta_resolucion.modificacion else None
    })

@coe_acta_resoluciones_bp.route('/api/coe_acta_resoluciones/<int:id>', methods=['DELETE'])
def delete_coe_acta_resolucion(id):
    """Eliminar coe_acta_resolucion
    ---
    tags:
      - Coe Acta Resoluciones
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
        db.text("DELETE FROM coe_acta_resoluciones WHERE id = :id"),
        {'id': id}
    )

    if result.rowcount == 0:  # type: ignore
        return jsonify({'error': 'Coe acta resolucion no encontrada'}), 404

    db.session.commit()
    return jsonify({'mensaje': 'Coe acta resolucion eliminada correctamente'})