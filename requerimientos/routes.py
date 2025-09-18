from flask import request, jsonify
from requerimientos import requerimientos_bp
from models import db
from datetime import datetime, timezone

@requerimientos_bp.route('/api/requerimientos/<int:usuario_id>', methods=['GET'])
def get_requerimientos(usuario_id):
    """Listar requerimientos
    ---
    tags:
      - Requerimientos
    parameters:
      - name: usuario_id
        in: path
        type: integer
        required: true
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
              usuario_emisor_id: {type: integer}
              usuario_receptor_id: {type: integer}
              fecha_inicio: {type: string}
              fecha_fin: {type: string}
              porcentaje_avance: {type: integer}
              requerimiento_estado_id: {type: integer}
              activo: {type: boolean}
              creador: {type: string}
              creacion: {type: string}
              modificador: {type: string}
              modificacion: {type: string}
    """
    params = {'usuario_id': usuario_id}
    query = db.text("""SELECT r.emergencia_id, r.id requerimiento_id, 
        r.usuario_emisor_id, ue.usuario usuario_emisor,
        r.usuario_receptor_id, ur.usuario usuario_receptor,
        r.fecha_inicio, r.fecha_fin, r.porcentaje_avance, r.requerimiento_estado_id, r.activo
        FROM public.requerimientos r
        INNER JOIN public.usuarios ue ON r.usuario_emisor_id = ue.id
        INNER JOIN public.usuarios ur ON r.usuario_receptor_id = ur.id
        WHERE r.usuario_emisor_id = :usuario_id""")

    result = db.session.execute(query, params)
    requerimientos = []
    if not result:
        return jsonify({'error': 'Requerimientos no encontrados'}), 404
    for row in result:
        requerimientos.append({
            'emergencia_id': row.emergencia_id,
            'requerimiento_id': row.requerimiento_id,
            'usuario_emisor_id': row.usuario_emisor_id,
            'usuario_emisor': row.usuario_emisor,
            'usuario_receptor_id': row.usuario_receptor_id,
            'usuario_receptor': row.usuario_receptor,
            'fecha_inicio': row.fecha_inicio.isoformat() if row.fecha_inicio else None,
            'fecha_fin': row.fecha_fin.isoformat() if row.fecha_fin else None,
            'porcentaje_avance': row.porcentaje_avance,
            'requerimiento_estado_id': row.requerimiento_estado_id,
            'activo': row.activo
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
          required: [emergencia_id, usuario_emisor_id, usuario_receptor_id]
          properties:
            emergencia_id: {type: integer}
            usuario_emisor_id: {type: integer}
            usuario_receptor_id: {type: integer}
            fecha_inicio: {type: string}
            fecha_fin: {type: string}
            porcentaje_avance: {type: integer}
            requerimiento_estado_id: {type: integer}
            activo: {type: boolean}
            creador: {type: string}
    responses:
      201:
        description: Requerimiento creado
        schema:
          type: object
          properties:
            id: {type: integer}
            emergencia_id: {type: integer}
            usuario_emisor_id: {type: integer}
            usuario_receptor_id: {type: integer}
            fecha_inicio: {type: string}
            fecha_fin: {type: string}
            porcentaje_avance: {type: integer}
            requerimiento_estado_id: {type: integer}
            activo: {type: boolean}
            creador: {type: string}
            creacion: {type: string}
            modificador: {type: string}
            modificacion: {type: string}
    """
    data = request.get_json()
    now = datetime.now(timezone.utc)
    
    query = db.text("""
        INSERT INTO requerimientos (
            emergencia_id, usuario_emisor_id, usuario_receptor_id, fecha_inicio,
            fecha_fin, activo, creador, creacion, modificador, modificacion,
            porcentaje_avance, requerimiento_estado_id
        )
        VALUES (
            :emergencia_id, :usuario_emisor_id, :usuario_receptor_id, :fecha_inicio,
            :fecha_fin, :activo, :creador, :creacion, :modificador, :modificacion,
            :porcentaje_avance, :requerimiento_estado_id
        )
        RETURNING id
    """)

    result = db.session.execute(query, {
        'emergencia_id': data['emergencia_id'],
        'usuario_emisor_id': data['usuario_emisor_id'],
        'usuario_receptor_id': data['usuario_receptor_id'],
        'fecha_inicio': data.get('fecha_inicio', now),
        'fecha_fin': data.get('fecha_fin'),
        'activo': data.get('activo', True),
        'creador': data.get('creador', 'Sistema'),
        'creacion': now,
        'modificador': data.get('creador', 'Sistema'),
        'modificacion': now,
        'porcentaje_avance': data.get('porcentaje_avance', 0),
        'requerimiento_estado_id': data.get('requerimiento_estado_id', 1)
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
        'usuario_emisor_id': requerimiento.usuario_emisor_id,
        'usuario_receptor_id': requerimiento.usuario_receptor_id,
        'fecha_inicio': requerimiento.fecha_inicio.isoformat() if requerimiento.fecha_inicio else None,
        'fecha_fin': requerimiento.fecha_fin.isoformat() if requerimiento.fecha_fin else None,
        'porcentaje_avance': requerimiento.porcentaje_avance,
        'requerimiento_estado_id': requerimiento.requerimiento_estado_id,
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
        'usuario_emisor_id': requerimiento.usuario_emisor_id,
        'usuario_receptor_id': requerimiento.usuario_receptor_id,
        'fecha_inicio': requerimiento.fecha_inicio.isoformat() if requerimiento.fecha_inicio else None,
        'fecha_fin': requerimiento.fecha_fin.isoformat() if requerimiento.fecha_fin else None,
        'porcentaje_avance': requerimiento.porcentaje_avance,
        'requerimiento_estado_id': requerimiento.requerimiento_estado_id,
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
            usuario_emisor_id: {type: integer}
            usuario_receptor_id: {type: integer}
            fecha_inicio: {type: string}
            fecha_fin: {type: string}
            porcentaje_avance: {type: integer}
            requerimiento_estado_id: {type: integer}
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
            usuario_emisor_id = :usuario_emisor_id,
            usuario_receptor_id = :usuario_receptor_id,
            fecha_inicio = :fecha_inicio,
            fecha_fin = :fecha_fin,
            porcentaje_avance = :porcentaje_avance,
            requerimiento_estado_id = :requerimiento_estado_id,
            activo = :activo,
            modificador = :modificador,
            modificacion = :modificacion
        WHERE id = :id
    """)

    result = db.session.execute(query, {
        'id': id,
        'emergencia_id': data.get('emergencia_id'),
        'usuario_emisor_id': data.get('usuario_emisor_id'),
        'usuario_receptor_id': data.get('usuario_receptor_id'),
        'fecha_inicio': data.get('fecha_inicio'),
        'fecha_fin': data.get('fecha_fin'),
        'porcentaje_avance': data.get('porcentaje_avance'),
        'requerimiento_estado_id': data.get('requerimiento_estado_id'),
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
        'usuario_emisor_id': requerimiento.usuario_emisor_id,
        'usuario_receptor_id': requerimiento.usuario_receptor_id,
        'fecha_inicio': requerimiento.fecha_inicio.isoformat() if requerimiento.fecha_inicio else None,
        'fecha_fin': requerimiento.fecha_fin.isoformat() if requerimiento.fecha_fin else None,
        'porcentaje_avance': requerimiento.porcentaje_avance,
        'requerimiento_estado_id': requerimiento.requerimiento_estado_id,
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
