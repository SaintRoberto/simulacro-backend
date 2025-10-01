from flask import request, jsonify
from coe_actas import coe_actas_bp
from models import db
from datetime import datetime, timezone

@coe_actas_bp.route('/api/coe_actas', methods=['GET'])
def get_coe_actas():
    """Listar coe_actas
    ---
    tags:
      - Coe Actas
    responses:
        200:
          description: Lista de coe_actas
          schema:
            type: array
            items:
              type: object
              properties:
                id: {type: integer}
                usuario_id: {type: integer}
                emergencia_id: {type: integer}
                fecha_sesion: {type: string}
                hora_sesion: {type: string}
                activo: {type: boolean}
                creador: {type: string}
                creacion: {type: string}
                modificador: {type: string}
                modificacion: {type: string}
    """
    result = db.session.execute(db.text("SELECT * FROM coe_actas"))
    coe_actas = []
    for row in result:
        coe_actas.append({  # type: ignore
            'id': row.id,
            'usuario_id': row.usuario_id,
            'emergencia_id': row.emergencia_id,
            'fecha_sesion': row.fecha_sesion.isoformat() if row.fecha_sesion else None,
            'hora_sesion': row.hora_sesion,
            'activo': row.activo,
            'creador': row.creador,
            'creacion': row.creacion.isoformat() if row.creacion else None,
            'modificador': row.modificador,
            'modificacion': row.modificacion.isoformat() if row.modificacion else None
        })
    return jsonify(coe_actas)

@coe_actas_bp.route('/api/coe_actas/usuario/<int:usuario_id>/emergencia/<int:emergencia_id>', methods=['GET'])
def get_coe_actas_by_usuario_by_emergencia(usuario_id, emergencia_id):
    """Obtener coe_actas por usuario y emergencia
    ---
    tags:
      - Coe Actas
    parameters:
      - name: usuario_id
        in: path
        type: integer
        required: true
      - name: emergencia_id
        in: path
        type: integer
        required: true
    responses:
        200:
          description: Lista de coe_actas
          schema:
            type: array
            items:
              type: object
              properties:
                id: {type: integer}
                usuario_id: {type: integer}
                emergencia_id: {type: integer}
                fecha_sesion: {type: string}
                hora_sesion: {type: string}
                activo: {type: boolean}
                creador: {type: string}
                creacion: {type: string}
                modificador: {type: string}
                modificacion: {type: string}
    """
    result = db.session.execute(db.text("SELECT * FROM coe_actas WHERE usuario_id = :usuario_id AND emergencia_id = :emergencia_id"), {'usuario_id': usuario_id, 'emergencia_id': emergencia_id})
    coe_actas = []
    for row in result:
        coe_actas.append({  # type: ignore
            'id': row.id,
            'usuario_id': row.usuario_id,
            'emergencia_id': row.emergencia_id,
            'fecha_sesion': row.fecha_sesion.isoformat() if row.fecha_sesion else None,
            'hora_sesion': row.hora_sesion,
            'activo': row.activo,
            'creador': row.creador,
            'creacion': row.creacion.isoformat() if row.creacion else None,
            'modificador': row.modificador,
            'modificacion': row.modificacion.isoformat() if row.modificacion else None
        })
    return jsonify(coe_actas)

@coe_actas_bp.route('/api/coe_actas', methods=['POST'])
def create_coe_acta():
    """Crear coe_acta
    ---
    tags:
      - Coe Actas
    consumes:
      - application/json
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          required: [usuario_id, emergencia_id]
          properties:
            usuario_id: {type: integer}
            emergencia_id: {type: integer}
            fecha_sesion: {type: string, format: date-time}
            hora_sesion: {type: string}
            activo: {type: boolean}
            creador: {type: string}
    responses:
      201:
        description: Coe acta creada
        schema:
          type: object
          properties:
            id: {type: integer}
            usuario_id: {type: integer}
            emergencia_id: {type: integer}
            fecha_sesion: {type: string}
            hora_sesion: {type: string}
            activo: {type: boolean}
            creador: {type: string}
            creacion: {type: string}
            modificador: {type: string}
            modificacion: {type: string}
    """
    data = request.get_json()
    now = datetime.now(timezone.utc)

    query = db.text("""
        INSERT INTO coe_actas (usuario_id, emergencia_id, fecha_sesion, hora_sesion, activo, creador, creacion, modificador, modificacion)
        VALUES (:usuario_id, :emergencia_id, :fecha_sesion, :hora_sesion, :activo, :creador, :creacion, :modificador, :modificacion)
        RETURNING id
    """)

    result = db.session.execute(query, {
        'usuario_id': data['usuario_id'],
        'emergencia_id': data['emergencia_id'],
        'fecha_sesion': data.get('fecha_sesion'),
        'hora_sesion': data.get('hora_sesion'),
        'activo': data.get('activo', True),
        'creador': data.get('creador', 'Sistema'),
        'creacion': now,
        'modificador': data.get('creador', 'Sistema'),
        'modificacion': now
    })

    row = result.fetchone()
    if row is None:
        db.session.rollback()
        return jsonify({'error': 'Failed to create coe_acta'}), 500
    coe_acta_id = row[0]
    db.session.commit()

    coe_acta = db.session.execute(
        db.text("SELECT * FROM coe_actas WHERE id = :id"),
        {'id': coe_acta_id}
    ).fetchone()

    if not coe_acta:
        return jsonify({'error': 'Coe acta not found after creation'}), 404

    return jsonify({  # type: ignore
        'id': coe_acta.id,
        'usuario_id': coe_acta.usuario_id,
        'emergencia_id': coe_acta.emergencia_id,
        'fecha_sesion': coe_acta.fecha_sesion.isoformat() if coe_acta.fecha_sesion else None,
        'hora_sesion': coe_acta.hora_sesion,
        'activo': coe_acta.activo,
        'creador': coe_acta.creador,
        'creacion': coe_acta.creacion.isoformat() if coe_acta.creacion else None,
        'modificador': coe_acta.modificador,
        'modificacion': coe_acta.modificacion.isoformat() if coe_acta.modificacion else None
    }), 201

@coe_actas_bp.route('/api/coe_actas/<int:id>', methods=['GET'])
def get_coe_acta(id):
    """Obtener coe_acta por ID
    ---
    tags:
      - Coe Actas
    parameters:
      - name: id
        in: path
        type: integer
        required: true
    responses:
      200:
        description: Coe acta
      404:
        description: No encontrada
    """
    result = db.session.execute(
        db.text("SELECT * FROM coe_actas WHERE id = :id"),
        {'id': id}
    )
    coe_acta = result.fetchone()

    if not coe_acta:
        return jsonify({'error': 'Coe acta no encontrada'}), 404

    return jsonify({
        'id': coe_acta.id,
        'usuario_id': coe_acta.usuario_id,
        'emergencia_id': coe_acta.emergencia_id,
        'fecha_sesion': coe_acta.fecha_sesion.isoformat() if coe_acta.fecha_sesion else None,
        'hora_sesion': coe_acta.hora_sesion,
        'activo': coe_acta.activo,
        'creador': coe_acta.creador,
        'creacion': coe_acta.creacion.isoformat() if coe_acta.creacion else None,
        'modificador': coe_acta.modificador,
        'modificacion': coe_acta.modificacion.isoformat() if coe_acta.modificacion else None
    })

@coe_actas_bp.route('/api/coe_actas/<int:id>', methods=['PUT'])
def update_coe_acta(id):
    """Actualizar coe_acta
    ---
    tags:
      - Coe Actas
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
            usuario_id: {type: integer}
            emergencia_id: {type: integer}
            fecha_sesion: {type: string, format: date-time}
            hora_sesion: {type: string}
            activo: {type: boolean}
    responses:
      200:
        description: Coe acta actualizada
      404:
        description: No encontrada
    """
    data = request.get_json()
    now = datetime.now(timezone.utc)

    query = db.text("""
        UPDATE coe_actas
        SET usuario_id = :usuario_id,
            emergencia_id = :emergencia_id,
            fecha_sesion = :fecha_sesion,
            hora_sesion = :hora_sesion,
            activo = :activo,
            modificador = :modificador,
            modificacion = :modificacion
        WHERE id = :id
    """)

    result = db.session.execute(query, {
        'id': id,
        'usuario_id': data.get('usuario_id'),
        'emergencia_id': data.get('emergencia_id'),
        'fecha_sesion': data.get('fecha_sesion'),
        'hora_sesion': data.get('hora_sesion'),
        'activo': data.get('activo'),
        'modificador': data.get('modificador', 'Sistema'),
        'modificacion': now
    })

    if getattr(result, 'rowcount', 0) == 0:  # type: ignore
        return jsonify({'error': 'Coe acta no encontrada'}), 404

    db.session.commit()

    coe_acta = db.session.execute(
        db.text("SELECT * FROM coe_actas WHERE id = :id"),
        {'id': id}
    ).fetchone()

    if not coe_acta:
        return jsonify({'error': 'Coe acta not found after update'}), 404

    return jsonify({  # type: ignore
        'id': coe_acta.id,
        'usuario_id': coe_acta.usuario_id,
        'emergencia_id': coe_acta.emergencia_id,
        'fecha_sesion': coe_acta.fecha_sesion.isoformat() if coe_acta.fecha_sesion else None,
        'hora_sesion': coe_acta.hora_sesion,
        'activo': coe_acta.activo,
        'creador': coe_acta.creador,
        'creacion': coe_acta.creacion.isoformat() if coe_acta.creacion else None,
        'modificador': coe_acta.modificador,
        'modificacion': coe_acta.modificacion.isoformat() if coe_acta.modificacion else None
    })

@coe_actas_bp.route('/api/coe_actas/<int:id>', methods=['DELETE'])
def delete_coe_acta(id):
    """Eliminar coe_acta
    ---
    tags:
      - Coe Actas
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
        db.text("DELETE FROM coe_actas WHERE id = :id"),
        {'id': id}
    )

    if getattr(result, 'rowcount', 0) == 0:  # type: ignore
        return jsonify({'error': 'Coe acta no encontrada'}), 404

    db.session.commit()
    return jsonify({'mensaje': 'Coe acta eliminada correctamente'})