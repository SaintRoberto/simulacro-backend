from flask import request, jsonify
from actas_coe import actas_coe_bp
from models import db
from datetime import datetime, timezone

@actas_coe_bp.route('/api/actas_coe', methods=['GET'])
def get_actas_coe():
    """Listar actas_coe
    ---
    tags:
      - Actas Coe
    responses:
        200:
          description: Lista de actas COE
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
                detalle: {type: string}
                fecha_finalizado: {type: string}
                acta_coe_estado_id: {type: integer}
                activo: {type: boolean}
                creador: {type: string}
                creacion: {type: string}
                modificador: {type: string}
                modificacion: {type: string}
    """
    result = db.session.execute(db.text("SELECT * FROM actas_coe"))
    coe_actas = []
    for row in result:
        coe_actas.append({  # type: ignore
            'id': row.id,
            'usuario_id': row.usuario_id,
            'emergencia_id': row.emergencia_id,
            'fecha_sesion': row.fecha_sesion.isoformat() if row.fecha_sesion else None,
            'hora_sesion': row.hora_sesion,
            'detalle': row.detalle,
            'fecha_finalizado': row.fecha_finalizado.isoformat() if getattr(row, 'fecha_finalizado', None) else None,
            'acta_coe_estado_id': getattr(row, 'acta_coe_estado_id', None),
            'activo': row.activo,
            'creador': row.creador,
            'creacion': row.creacion.isoformat() if row.creacion else None,
            'modificador': row.modificador,
            'modificacion': row.modificacion.isoformat() if row.modificacion else None
        })
    return jsonify(coe_actas)

@actas_coe_bp.route('/api/actas_coe/usuario/<int:usuario_id>/emergencia/<int:emergencia_id>', methods=['GET'])
def get_actas_coe_by_usuario_by_emergencia(usuario_id, emergencia_id):
    """Obtener actas_coe por usuario y emergencia
    ---
    tags:
      - Actas Coe
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
          description: Lista de actas COE
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
                detalle: {type: string}
                fecha_finalizado: {type: string}
                acta_coe_estado_id: {type: integer}
                activo: {type: boolean}
                creador: {type: string}
                creacion: {type: string}
                modificador: {type: string}
                modificacion: {type: string}
    """
    result = db.session.execute(db.text("SELECT * FROM actas_coe WHERE usuario_id = :usuario_id AND emergencia_id = :emergencia_id"), {'usuario_id': usuario_id, 'emergencia_id': emergencia_id})
    coe_actas = []
    for row in result:
        coe_actas.append({  # type: ignore
            'id': row.id,
            'usuario_id': row.usuario_id,
            'emergencia_id': row.emergencia_id,
            'fecha_sesion': row.fecha_sesion.isoformat() if row.fecha_sesion else None,
            'hora_sesion': row.hora_sesion,
            'detalle': row.detalle,
            'fecha_finalizado': row.fecha_finalizado.isoformat() if getattr(row, 'fecha_finalizado', None) else None,
            'acta_coe_estado_id': getattr(row, 'acta_coe_estado_id', None),
            'activo': row.activo,
            'creador': row.creador,
            'creacion': row.creacion.isoformat() if row.creacion else None,
            'modificador': row.modificador,
            'modificacion': row.modificacion.isoformat() if row.modificacion else None
        })
    return jsonify(coe_actas)

@actas_coe_bp.route('/api/actas_coe', methods=['POST'])
def create_acta_coe():
    """Crear acta COE
    ---
    tags:
      - Actas Coe
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
            detalle: {type: string}
            acta_coe_estado_id: {type: integer}
            activo: {type: boolean}
            creador: {type: string}
    responses:
      201:
        description: Acta COE creada
        schema:
          type: object
          properties:
            id: {type: integer}
            usuario_id: {type: integer}
            emergencia_id: {type: integer}
            fecha_sesion: {type: string}
            hora_sesion: {type: string}
            detalle: {type: string}
            fecha_finalizado: {type: string}
            acta_coe_estado_id: {type: integer}
            activo: {type: boolean}
            creador: {type: string}
            creacion: {type: string}
            modificador: {type: string}
            modificacion: {type: string}
    """
    data = request.get_json()
    now = datetime.now(timezone.utc)

    acta_coe_estado_id = data.get('acta_coe_estado_id')
    fecha_finalizado = None

    # Estado "Finalizada" = 3
    if acta_coe_estado_id == 3:
        fecha_finalizado = now

    query = db.text("""
        INSERT INTO actas_coe (usuario_id, emergencia_id, fecha_sesion, hora_sesion, detalle, fecha_finalizado, acta_coe_estado_id, activo, creador, creacion, modificador, modificacion)
        VALUES (:usuario_id, :emergencia_id, :fecha_sesion, :hora_sesion, :detalle, :fecha_finalizado, :acta_coe_estado_id, :activo, :creador, :creacion, :modificador, :modificacion)
        RETURNING id
    """)

    result = db.session.execute(query, {
        'usuario_id': data['usuario_id'],
        'emergencia_id': data['emergencia_id'],
        'fecha_sesion': data.get('fecha_sesion'),
        'hora_sesion': data.get('hora_sesion'),
        'detalle': data.get('detalle'),
        'fecha_finalizado': fecha_finalizado,
        'acta_coe_estado_id': acta_coe_estado_id,
        'activo': data.get('activo', True),
        'creador': data.get('creador', 'Sistema'),
        'creacion': now,
        'modificador': data.get('creador', 'Sistema'),
        'modificacion': now
    })

    row = result.fetchone()
    if row is None:
        db.session.rollback()
        return jsonify({'error': 'Failed to create acta COE'}), 500
    coe_acta_id = row[0]

    db.session.commit()

    coe_acta = db.session.execute(
        db.text("SELECT * FROM actas_coe WHERE id = :id"),
        {'id': coe_acta_id}
    ).fetchone()

    if not coe_acta:
        return jsonify({'error': 'Acta COE not found after creation'}), 404

    return jsonify({  # type: ignore
        'id': coe_acta.id,
        'usuario_id': coe_acta.usuario_id,
        'emergencia_id': coe_acta.emergencia_id,
        'fecha_sesion': coe_acta.fecha_sesion.isoformat() if coe_acta.fecha_sesion else None,
        'hora_sesion': coe_acta.hora_sesion,
        'detalle': coe_acta.detalle,
        'fecha_finalizado': coe_acta.fecha_finalizado.isoformat() if getattr(coe_acta, 'fecha_finalizado', None) else None,
        'acta_coe_estado_id': getattr(coe_acta, 'acta_coe_estado_id', None),
        'activo': coe_acta.activo,
        'creador': coe_acta.creador,
        'creacion': coe_acta.creacion.isoformat() if coe_acta.creacion else None,
        'modificador': coe_acta.modificador,
        'modificacion': coe_acta.modificacion.isoformat() if coe_acta.modificacion else None
    }), 201

@actas_coe_bp.route('/api/actas_coe/<int:id>', methods=['GET'])
def get_acta_coe(id):
    """Obtener acta COE por ID
    ---
    tags:
      - Actas Coe
    parameters:
      - name: id
        in: path
        type: integer
        required: true
    responses:
        200:
          description: Acta COE
        404:
          description: No encontrada
    """
    result = db.session.execute(
        db.text("SELECT * FROM actas_coe WHERE id = :id"),
        {'id': id}
    )
    coe_acta = result.fetchone()

    if not coe_acta:
        return jsonify({'error': 'Acta COE no encontrada'}), 404

    return jsonify({
        'id': coe_acta.id,
        'usuario_id': coe_acta.usuario_id,
        'emergencia_id': coe_acta.emergencia_id,
        'fecha_sesion': coe_acta.fecha_sesion.isoformat() if coe_acta.fecha_sesion else None,
        'hora_sesion': coe_acta.hora_sesion,
        'detalle': coe_acta.detalle,
        'fecha_finalizado': coe_acta.fecha_finalizado.isoformat() if getattr(coe_acta, 'fecha_finalizado', None) else None,
        'acta_coe_estado_id': getattr(coe_acta, 'acta_coe_estado_id', None),
        'activo': coe_acta.activo,
        'creador': coe_acta.creador,
        'creacion': coe_acta.creacion.isoformat() if coe_acta.creacion else None,
        'modificador': coe_acta.modificador,
        'modificacion': coe_acta.modificacion.isoformat() if coe_acta.modificacion else None
    })

@actas_coe_bp.route('/api/actas_coe/<int:id>', methods=['PUT'])
def update_acta_coe(id):
    """Actualizar acta COE
    ---
    tags:
      - Actas Coe
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
            detalle: {type: string}
            acta_coe_estado_id: {type: integer}
            activo: {type: boolean}
    responses:
      200:
        description: Acta COE actualizada
      404:
        description: No encontrada
    """
    data = request.get_json()
    now = datetime.now(timezone.utc)

    acta_coe_estado_id = data.get('acta_coe_estado_id')
    fecha_finalizado = None

    # Estado "Finalizada" = 3
    if acta_coe_estado_id == 3:
        fecha_finalizado = now

    query = db.text("""
        UPDATE actas_coe
        SET usuario_id = :usuario_id,
            emergencia_id = :emergencia_id,
            fecha_sesion = :fecha_sesion,
            hora_sesion = :hora_sesion,
            detalle = :detalle,
            fecha_finalizado = :fecha_finalizado,
            acta_coe_estado_id = :acta_coe_estado_id,
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
        'detalle': data.get('detalle'),
        'fecha_finalizado': fecha_finalizado,
        'acta_coe_estado_id': acta_coe_estado_id,
        'activo': data.get('activo'),
        'modificador': data.get('modificador', 'Sistema'),
        'modificacion': now
    })

    if getattr(result, 'rowcount', 0) == 0:  # type: ignore
        return jsonify({'error': 'Acta COE no encontrada'}), 404

    db.session.commit()

    coe_acta = db.session.execute(
        db.text("SELECT * FROM actas_coe WHERE id = :id"),
        {'id': id}
    ).fetchone()

    if not coe_acta:
        return jsonify({'error': 'Acta COE not found after update'}), 404

    return jsonify({  # type: ignore
        'id': coe_acta.id,
        'usuario_id': coe_acta.usuario_id,
        'emergencia_id': coe_acta.emergencia_id,
        'fecha_sesion': coe_acta.fecha_sesion.isoformat() if coe_acta.fecha_sesion else None,
        'hora_sesion': coe_acta.hora_sesion,
        'detalle': coe_acta.detalle,
        'fecha_finalizado': coe_acta.fecha_finalizado.isoformat() if getattr(coe_acta, 'fecha_finalizado', None) else None,
        'acta_coe_estado_id': getattr(coe_acta, 'acta_coe_estado_id', None),
        'activo': coe_acta.activo,
        'creador': coe_acta.creador,
        'creacion': coe_acta.creacion.isoformat() if coe_acta.creacion else None,
        'modificador': coe_acta.modificador,
        'modificacion': coe_acta.modificacion.isoformat() if coe_acta.modificacion else None
    })

@actas_coe_bp.route('/api/actas_coe/<int:id>', methods=['DELETE'])
def delete_acta_coe(id):
    """Eliminar acta COE
    ---
    tags:
      - Actas Coe
    parameters:
      - name: id
        in: path
        type: integer
        required: true
    responses:
      200:
        description: Acta COE eliminada
      404:
        description: No encontrada
    """
    result = db.session.execute(
        db.text("DELETE FROM actas_coe WHERE id = :id"),
        {'id': id}
    )

    if getattr(result, 'rowcount', 0) == 0:  # type: ignore
        return jsonify({'error': 'Acta COE no encontrada'}), 404

    db.session.commit()
    return jsonify({'mensaje': 'Acta COE eliminada correctamente'})