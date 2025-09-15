from flask import request, jsonify
from requerimiento_recursos import requerimiento_recursos_bp
from models import db
from datetime import datetime, timezone

@requerimiento_recursos_bp.route('/api/requerimiento-recursos', methods=['GET'])
def get_requerimiento_recursos():
    """Listar requerimiento recursos
    ---
    tags:
      - Requerimiento Recursos
    responses:
      200:
        description: Lista de requerimiento recursos
        schema:
          type: array
          items:
            type: object
            properties:
              id: {type: integer}
              requerimiento_id: {type: integer}
              recurso_humano_id: {type: integer}
              recurso_material_id: {type: integer}
              cantidad_asignada: {type: integer}
              observaciones: {type: string}
              activo: {type: boolean}
              creador: {type: string}
              creacion: {type: string}
              modificador: {type: string}
              modificacion: {type: string}
    """
    result = db.session.execute(db.text("SELECT * FROM requerimiento_recursos"))
    relaciones = []
    for row in result:
        relaciones.append({
            'id': row.id,
            'requerimiento_id': row.requerimiento_id,
            'recurso_humano_id': row.recurso_humano_id,
            'recurso_material_id': row.recurso_material_id,
            'cantidad_asignada': row.cantidad_asignada,
            'observaciones': row.observaciones,
            'activo': row.activo,
            'creador': row.creador,
            'creacion': row.creacion.isoformat() if row.creacion else None,
            'modificador': row.modificador,
            'modificacion': row.modificacion.isoformat() if row.modificacion else None
        })
    return jsonify(relaciones)

@requerimiento_recursos_bp.route('/api/requerimiento-recursos', methods=['POST'])
def create_requerimiento_recurso():
    """Crear requerimiento recurso
    ---
    tags:
      - Requerimiento Recursos
    consumes:
      - application/json
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          required: [requerimiento_id]
          properties:
            requerimiento_id: {type: integer}
            recurso_humano_id: {type: integer}
            recurso_material_id: {type: integer}
            cantidad_asignada: {type: integer}
            observaciones: {type: string}
            activo: {type: boolean}
            creador: {type: string}
    responses:
      201:
        description: Requerimiento recurso creado
    """
    data = request.get_json()
    now = datetime.now(timezone.utc)
    
    query = db.text("""
        INSERT INTO requerimiento_recursos (
            requerimiento_id, recurso_humano_id, recurso_material_id, cantidad_asignada,
            observaciones, activo, creador, creacion, modificador, modificacion
        )
        VALUES (
            :requerimiento_id, :recurso_humano_id, :recurso_material_id, :cantidad_asignada,
            :observaciones, :activo, :creador, :creacion, :modificador, :modificacion
        )
        RETURNING id
    """)
    
    result = db.session.execute(query, {
        'requerimiento_id': data['requerimiento_id'],
        'recurso_humano_id': data.get('recurso_humano_id'),
        'recurso_material_id': data.get('recurso_material_id'),
        'cantidad_asignada': data.get('cantidad_asignada', 0),
        'observaciones': data.get('observaciones'),
        'activo': data.get('activo', True),
        'creador': data.get('creador', 'Sistema'),
        'creacion': now,
        'modificador': data.get('creador', 'Sistema'),
        'modificacion': now
    })
    
    relacion_id = result.fetchone()[0]
    db.session.commit()
    
    relacion = db.session.execute(
        db.text("SELECT * FROM requerimiento_recursos WHERE id = :id"), 
        {'id': relacion_id}
    ).fetchone()
    
    return jsonify({
        'id': relacion.id,
        'requerimiento_id': relacion.requerimiento_id,
        'recurso_humano_id': relacion.recurso_humano_id,
        'recurso_material_id': relacion.recurso_material_id,
        'cantidad_asignada': relacion.cantidad_asignada,
        'observaciones': relacion.observaciones,
        'activo': relacion.activo,
        'creador': relacion.creador,
        'creacion': relacion.creacion.isoformat() if relacion.creacion else None,
        'modificador': relacion.modificador,
        'modificacion': relacion.modificacion.isoformat() if relacion.modificacion else None
    }), 201

@requerimiento_recursos_bp.route('/api/requerimiento-recursos/<int:id>', methods=['GET'])
def get_requerimiento_recurso(id):
    """Obtener requerimiento recurso por ID
    ---
    tags:
      - Requerimiento Recursos
    parameters:
      - name: id
        in: path
        type: integer
        required: true
    responses:
      200:
        description: Requerimiento recurso
      404:
        description: No encontrado
    """
    result = db.session.execute(
        db.text("SELECT * FROM requerimiento_recursos WHERE id = :id"), 
        {'id': id}
    )
    relacion = result.fetchone()
    
    if not relacion:
        return jsonify({'error': 'Relación no encontrada'}), 404
    
    return jsonify({
        'id': relacion.id,
        'requerimiento_id': relacion.requerimiento_id,
        'recurso_humano_id': relacion.recurso_humano_id,
        'recurso_material_id': relacion.recurso_material_id,
        'cantidad_asignada': relacion.cantidad_asignada,
        'observaciones': relacion.observaciones,
        'activo': relacion.activo,
        'creador': relacion.creador,
        'creacion': relacion.creacion.isoformat() if relacion.creacion else None,
        'modificador': relacion.modificador,
        'modificacion': relacion.modificacion.isoformat() if relacion.modificacion else None
    })

@requerimiento_recursos_bp.route('/api/requerimiento-recursos/<int:id>', methods=['PUT'])
def update_requerimiento_recurso(id):
    """Actualizar requerimiento recurso
    ---
    tags:
      - Requerimiento Recursos
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
            requerimiento_id: {type: integer}
            recurso_humano_id: {type: integer}
            recurso_material_id: {type: integer}
            cantidad_asignada: {type: integer}
            observaciones: {type: string}
            activo: {type: boolean}
            modificador: {type: string}
    responses:
      200:
        description: Requerimiento recurso actualizado
      404:
        description: No encontrado
    """
    data = request.get_json()
    now = datetime.now(timezone.utc)
    
    query = db.text("""
        UPDATE requerimiento_recursos 
        SET requerimiento_id = :requerimiento_id, 
            recurso_humano_id = :recurso_humano_id, 
            recurso_material_id = :recurso_material_id, 
            cantidad_asignada = :cantidad_asignada, 
            observaciones = :observaciones, 
            activo = :activo, 
            modificador = :modificador, 
            modificacion = :modificacion
        WHERE id = :id
    """)
    
    result = db.session.execute(query, {
        'id': id,
        'requerimiento_id': data.get('requerimiento_id'),
        'recurso_humano_id': data.get('recurso_humano_id'),
        'recurso_material_id': data.get('recurso_material_id'),
        'cantidad_asignada': data.get('cantidad_asignada'),
        'observaciones': data.get('observaciones'),
        'activo': data.get('activo'),
        'modificador': data.get('modificador', 'Sistema'),
        'modificacion': now
    })
    
    if result.rowcount == 0:
        return jsonify({'error': 'Relación no encontrada'}), 404
    
    db.session.commit()
    
    relacion = db.session.execute(
        db.text("SELECT * FROM requerimiento_recursos WHERE id = :id"), 
        {'id': id}
    ).fetchone()
    
    return jsonify({
        'id': relacion.id,
        'requerimiento_id': relacion.requerimiento_id,
        'recurso_humano_id': relacion.recurso_humano_id,
        'recurso_material_id': relacion.recurso_material_id,
        'cantidad_asignada': relacion.cantidad_asignada,
        'observaciones': relacion.observaciones,
        'activo': relacion.activo,
        'creador': relacion.creador,
        'creacion': relacion.creacion.isoformat() if relacion.creacion else None,
        'modificador': relacion.modificador,
        'modificacion': relacion.modificacion.isoformat() if relacion.modificacion else None
    })

@requerimiento_recursos_bp.route('/api/requerimiento-recursos/<int:id>', methods=['DELETE'])
def delete_requerimiento_recurso(id):
    """Eliminar requerimiento recurso
    ---
    tags:
      - Requerimiento Recursos
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
        db.text("DELETE FROM requerimiento_recursos WHERE id = :id"), 
        {'id': id}
    )
    
    if result.rowcount == 0:
        return jsonify({'error': 'Relación no encontrada'}), 404
    
    db.session.commit()
    return jsonify({'mensaje': 'Relación eliminada correctamente'})
