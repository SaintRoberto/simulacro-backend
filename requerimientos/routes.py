from flask import request, jsonify
from requerimientos import requerimientos_bp
from models import db
from datetime import datetime, timezone

@requerimientos_bp.route('/api/requerimientos', methods=['GET'])
def get_requerimientos():
    """Listar requerimientos
    ---
    tags:
      - Requerimientos
    responses:
      200:
        description: Lista de requerimientos
        schema:
          type: array
          items:
            type: object
            properties:
              id: {type: integer}
              emergencia_id: {type: integer}
              mesa_id: {type: integer}
              institucion_id: {type: integer}
              descripcion: {type: string}
              cantidad_solicitada: {type: integer}
              cantidad_aprobada: {type: integer}
              cantidad_entregada: {type: integer}
              observaciones: {type: string}
              activo: {type: boolean}
              creador: {type: string}
              creacion: {type: string}
              modificador: {type: string}
              modificacion: {type: string}
    """
    result = db.session.execute(db.text("SELECT * FROM requerimientos"))
    requerimientos = []
    for row in result:
        requerimientos.append({
            'id': row.id,
            'emergencia_id': row.emergencia_id,
            'mesa_id': row.mesa_id,
            'institucion_id': row.institucion_id,
            'descripcion': row.descripcion,
            'cantidad_solicitada': row.cantidad_solicitada,
            'cantidad_aprobada': row.cantidad_aprobada,
            'cantidad_entregada': row.cantidad_entregada,
            'observaciones': row.observaciones,
            'activo': row.activo,
            'creador': row.creador,
            'creacion': row.creacion.isoformat() if row.creacion else None,
            'modificador': row.modificador,
            'modificacion': row.modificacion.isoformat() if row.modificacion else None
        })
    return jsonify(requerimientos)

@requerimientos_bp.route('/api/requerimientos', methods=['POST'])
def create_requerimiento():
    """Crear requerimiento
    ---
    tags:
      - Requerimientos
    consumes:
      - application/json
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          required: [emergencia_id, mesa_id, institucion_id, descripcion]
          properties:
            emergencia_id: {type: integer}
            mesa_id: {type: integer}
            institucion_id: {type: integer}
            descripcion: {type: string}
            cantidad_solicitada: {type: integer}
            cantidad_aprobada: {type: integer}
            cantidad_entregada: {type: integer}
            observaciones: {type: string}
            activo: {type: boolean}
            creador: {type: string}
    responses:
      201:
        description: Requerimiento creado
    """
    data = request.get_json()
    now = datetime.now(timezone.utc)
    
    query = db.text("""
        INSERT INTO requerimientos (
            emergencia_id, mesa_id, institucion_id, descripcion, cantidad_solicitada,
            cantidad_aprobada, cantidad_entregada, observaciones, activo,
            creador, creacion, modificador, modificacion
        )
        VALUES (
            :emergencia_id, :mesa_id, :institucion_id, :descripcion, :cantidad_solicitada,
            :cantidad_aprobada, :cantidad_entregada, :observaciones, :activo,
            :creador, :creacion, :modificador, :modificacion
        )
        RETURNING id
    """)
    
    result = db.session.execute(query, {
        'emergencia_id': data['emergencia_id'],
        'mesa_id': data['mesa_id'],
        'institucion_id': data['institucion_id'],
        'descripcion': data['descripcion'],
        'cantidad_solicitada': data.get('cantidad_solicitada', 0),
        'cantidad_aprobada': data.get('cantidad_aprobada', 0),
        'cantidad_entregada': data.get('cantidad_entregada', 0),
        'observaciones': data.get('observaciones'),
        'activo': data.get('activo', True),
        'creador': data.get('creador', 'Sistema'),
        'creacion': now,
        'modificador': data.get('creador', 'Sistema'),
        'modificacion': now
    })
    
    requerimiento_id = result.fetchone()[0]
    db.session.commit()
    
    requerimiento = db.session.execute(
        db.text("SELECT * FROM requerimientos WHERE id = :id"), 
        {'id': requerimiento_id}
    ).fetchone()
    
    return jsonify({
        'id': requerimiento.id,
        'emergencia_id': requerimiento.emergencia_id,
        'mesa_id': requerimiento.mesa_id,
        'institucion_id': requerimiento.institucion_id,
        'descripcion': requerimiento.descripcion,
        'cantidad_solicitada': requerimiento.cantidad_solicitada,
        'cantidad_aprobada': requerimiento.cantidad_aprobada,
        'cantidad_entregada': requerimiento.cantidad_entregada,
        'observaciones': requerimiento.observaciones,
        'activo': requerimiento.activo,
        'creador': requerimiento.creador,
        'creacion': requerimiento.creacion.isoformat() if requerimiento.creacion else None,
        'modificador': requerimiento.modificador,
        'modificacion': requerimiento.modificacion.isoformat() if requerimiento.modificacion else None
    }), 201

@requerimientos_bp.route('/api/requerimientos/<int:id>', methods=['GET'])
def get_requerimiento(id):
    """Obtener requerimiento por ID
    ---
    tags:
      - Requerimientos
    parameters:
      - name: id
        in: path
        type: integer
        required: true
    responses:
      200:
        description: Requerimiento
      404:
        description: No encontrado
    """
    result = db.session.execute(
        db.text("SELECT * FROM requerimientos WHERE id = :id"), 
        {'id': id}
    )
    requerimiento = result.fetchone()
    
    if not requerimiento:
        return jsonify({'error': 'Requerimiento no encontrado'}), 404
    
    return jsonify({
        'id': requerimiento.id,
        'emergencia_id': requerimiento.emergencia_id,
        'mesa_id': requerimiento.mesa_id,
        'institucion_id': requerimiento.institucion_id,
        'descripcion': requerimiento.descripcion,
        'cantidad_solicitada': requerimiento.cantidad_solicitada,
        'cantidad_aprobada': requerimiento.cantidad_aprobada,
        'cantidad_entregada': requerimiento.cantidad_entregada,
        'observaciones': requerimiento.observaciones,
        'activo': requerimiento.activo,
        'creador': requerimiento.creador,
        'creacion': requerimiento.creacion.isoformat() if requerimiento.creacion else None,
        'modificador': requerimiento.modificador,
        'modificacion': requerimiento.modificacion.isoformat() if requerimiento.modificacion else None
    })

@requerimientos_bp.route('/api/requerimientos/<int:id>', methods=['PUT'])
def update_requerimiento(id):
    """Actualizar requerimiento
    ---
    tags:
      - Requerimientos
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
            emergencia_id: {type: integer}
            mesa_id: {type: integer}
            institucion_id: {type: integer}
            descripcion: {type: string}
            cantidad_solicitada: {type: integer}
            cantidad_aprobada: {type: integer}
            cantidad_entregada: {type: integer}
            observaciones: {type: string}
            activo: {type: boolean}
            modificador: {type: string}
    responses:
      200:
        description: Requerimiento actualizado
      404:
        description: No encontrado
    """
    data = request.get_json()
    now = datetime.now(timezone.utc)
    
    query = db.text("""
        UPDATE requerimientos 
        SET emergencia_id = :emergencia_id, 
            mesa_id = :mesa_id, 
            institucion_id = :institucion_id, 
            descripcion = :descripcion, 
            cantidad_solicitada = :cantidad_solicitada, 
            cantidad_aprobada = :cantidad_aprobada, 
            cantidad_entregada = :cantidad_entregada, 
            observaciones = :observaciones, 
            activo = :activo, 
            modificador = :modificador, 
            modificacion = :modificacion
        WHERE id = :id
    """)
    
    result = db.session.execute(query, {
        'id': id,
        'emergencia_id': data.get('emergencia_id'),
        'mesa_id': data.get('mesa_id'),
        'institucion_id': data.get('institucion_id'),
        'descripcion': data.get('descripcion'),
        'cantidad_solicitada': data.get('cantidad_solicitada'),
        'cantidad_aprobada': data.get('cantidad_aprobada'),
        'cantidad_entregada': data.get('cantidad_entregada'),
        'observaciones': data.get('observaciones'),
        'activo': data.get('activo'),
        'modificador': data.get('modificador', 'Sistema'),
        'modificacion': now
    })
    
    if result.rowcount == 0:
        return jsonify({'error': 'Requerimiento no encontrado'}), 404
    
    db.session.commit()
    
    requerimiento = db.session.execute(
        db.text("SELECT * FROM requerimientos WHERE id = :id"), 
        {'id': id}
    ).fetchone()
    
    return jsonify({
        'id': requerimiento.id,
        'emergencia_id': requerimiento.emergencia_id,
        'mesa_id': requerimiento.mesa_id,
        'institucion_id': requerimiento.institucion_id,
        'descripcion': requerimiento.descripcion,
        'cantidad_solicitada': requerimiento.cantidad_solicitada,
        'cantidad_aprobada': requerimiento.cantidad_aprobada,
        'cantidad_entregada': requerimiento.cantidad_entregada,
        'observaciones': requerimiento.observaciones,
        'activo': requerimiento.activo,
        'creador': requerimiento.creador,
        'creacion': requerimiento.creacion.isoformat() if requerimiento.creacion else None,
        'modificador': requerimiento.modificador,
        'modificacion': requerimiento.modificacion.isoformat() if requerimiento.modificacion else None
    })

@requerimientos_bp.route('/api/requerimientos/<int:id>', methods=['DELETE'])
def delete_requerimiento(id):
    """Eliminar requerimiento
    ---
    tags:
      - Requerimientos
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
        db.text("DELETE FROM requerimientos WHERE id = :id"), 
        {'id': id}
    )
    
    if result.rowcount == 0:
        return jsonify({'error': 'Requerimiento no encontrado'}), 404
    
    db.session.commit()
    return jsonify({'mensaje': 'Requerimiento eliminado correctamente'})
