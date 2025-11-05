from flask import request, jsonify
from eventos import eventos_bp
from models import db
from datetime import datetime, timezone

from utils.db_helpers import check_row_or_abort

@eventos_bp.route('/api/eventos', methods=['GET'])
def get_eventos():
    """Listar eventos.

    Devuelve todos los eventos almacenados en la tabla `eventos`.
    Responde con una lista de objetos JSON que representan cada registro.
    ---
    tags:
      - Eventos
    responses:
      200:
        description: Lista de eventos
    """
    result = db.session.execute(db.text("SELECT * FROM eventos ORDER BY id"))
    eventos = []
    for row in result:
        eventos.append({
            'id': row.id,
            'emergencia_id': row.emergencia_id,
            'provincia_id': row.provincia_id,
            'canton_id': row.canton_id,
            'parroquia_id': row.parroquia_id,
            'sector': row.sector,
            'evento_fecha': row.evento_fecha.isoformat() if row.evento_fecha else None,
            'longitud': float(row.longitud) if row.longitud is not None else None,
            'latitud': float(row.latitud) if row.latitud is not None else None,
            'evento_categoria_id': row.evento_categoria_id,
            'evento_tipo_id': row.evento_tipo_id,
            'evento_causa_id': row.evento_causa_id,
            'evento_origen_id': row.evento_origen_id,
            'alto_impacto': bool(row.alto_impacto),
            'descripcion': row.descripcion,
            'situacion': row.situacion,
            'evento_estado_id': row.evento_estado_id,
            'activo': row.activo,
            'creador': row.creador,
            'creacion': row.creacion.isoformat() if row.creacion else None,
            'modificador': row.modificador,
            'modificacion': row.modificacion.isoformat() if row.modificacion else None
        })
    return jsonify(eventos)

@eventos_bp.route('/api/eventos/emergencia/<int:emergencia_id>', methods=['GET'])
def get_eventos_by_emergencia(emergencia_id):
    """Obtener todos los eventos asociados a una emergencia específica.

    Este endpoint devuelve una lista de eventos registrados en el sistema que
    pertenecen a la emergencia indicada por su identificador (`emergencia_id`).

    Cada elemento incluye información como ubicación, fecha, causa, tipo,
    descripción, estado y otros metadatos del evento.

    ---
    tags:
      - Eventos
    parameters:
      - name: emergencia_id
        in: path
        description: Identificador de la emergencia cuyos eventos se desean listar
        required: true
        type: integer
    responses:
      200:
        description: Lista de eventos relacionados con la emergencia indicada
        examples:
          application/json:
            - id: 1
              emergencia_id: 3
              descripcion: "Deslizamiento de tierra en zona rural"
              evento_estado_id: 2
              activo: true
    """
    result = db.session.execute(
        db.text("SELECT * FROM eventos WHERE emergencia_id = :emergencia_id ORDER BY id"),
        {'emergencia_id': emergencia_id}
    )
    eventos = []
    for row in result:
        eventos.append({
            'id': row.id,
            'emergencia_id': row.emergencia_id,
            'provincia_id': row.provincia_id,
            'canton_id': row.canton_id,
            'parroquia_id': row.parroquia_id,
            'sector': row.sector,
            'evento_fecha': row.evento_fecha.isoformat() if row.evento_fecha else None,
            'longitud': float(row.longitud) if row.longitud is not None else None,
            'latitud': float(row.latitud) if row.latitud is not None else None,
            'evento_categoria_id': row.evento_categoria_id,
            'evento_tipo_id': row.evento_tipo_id,
            'evento_causa_id': row.evento_causa_id,
            'evento_origen_id': row.evento_origen_id,
            'alto_impacto': bool(row.alto_impacto),
            'descripcion': row.descripcion,
            'situacion': row.situacion,
            'evento_estado_id': row.evento_estado_id,
            'activo': row.activo,
            'creador': row.creador,
            'creacion': row.creacion.isoformat() if row.creacion else None,
            'modificador': row.modificador,
            'modificacion': row.modificacion.isoformat() if row.modificacion else None
        })
    return jsonify(eventos)
@eventos_bp.route('/api/eventos', methods=['POST'])
def create_evento():
    """Crear un nuevo evento.

    Espera un payload JSON con los campos necesarios para insertar un registro
    en la tabla `eventos`. Devuelve el registro creado con código 201.
    ---
    tags:
      - Eventos
    consumes:
      - application/json
    responses:
      201:
        description: Evento creado
      400:
        description: Datos inválidos
    """
    data = request.get_json()
    now = datetime.now(timezone.utc)

    query = db.text("""
        INSERT INTO eventos (
            emergencia_id, provincia_id, canton_id, parroquia_id, sector,
            evento_fecha, longitud, latitud, evento_categoria_id, evento_tipo_id,
            evento_causa_id, evento_origen_id, alto_impacto, descripcion, situacion,
            evento_estado_id, activo, creador, creacion, modificador, modificacion
        )
        VALUES (
            :emergencia_id, :provincia_id, :canton_id, :parroquia_id, :sector,
            :evento_fecha, :longitud, :latitud, :evento_categoria_id, :evento_tipo_id,
            :evento_causa_id, :evento_origen_id, :alto_impacto, :descripcion, :situacion,
            :evento_estado_id, :activo, :creador, :creacion, :modificador, :modificacion
        )
        RETURNING id
    """)

    result = db.session.execute(query, {
        'emergencia_id': data['emergencia_id'],
        'provincia_id': data['provincia_id'],
        'canton_id': data['canton_id'],
        'parroquia_id': data['parroquia_id'],
        'sector': data['sector'],
        'evento_fecha': data.get('evento_fecha', now),
        'longitud': data.get('longitud', 0),
        'latitud': data.get('latitud', 0),
        'evento_categoria_id': data['evento_categoria_id'],
        'evento_tipo_id': data['evento_tipo_id'],
        'evento_causa_id': data['evento_causa_id'],
        'evento_origen_id': data['evento_origen_id'],
        'alto_impacto': data.get('alto_impacto', False),
        'descripcion': data.get('descripcion'),
        'situacion': data.get('situacion'),
        'evento_estado_id': data['evento_estado_id'],
        'activo': data.get('activo', True),
        'creador': data.get('creador', 'Sistema'),
        'creacion': now,
        'modificador': data.get('modificador', data.get('creador', 'Sistema')),
        'modificacion': now
    })

    row = result.fetchone()
    if row is None:
        db.session.rollback()
        return jsonify({'error': 'Failed to create evento'}), 500
    evento_id = row[0]
    db.session.commit()

    evento = db.session.execute(
        db.text("SELECT * FROM eventos WHERE id = :id"),
        {'id': evento_id}
    ).fetchone()

    check_row_or_abort(evento, 'Evento no encontrado después de creación', 500)
    assert evento is not None

    return jsonify({
        'id': evento.id,
        'emergencia_id': evento.emergencia_id,
        'provincia_id': evento.provincia_id,
        'canton_id': evento.canton_id,
        'parroquia_id': evento.parroquia_id,
        'sector': evento.sector,
        'evento_fecha': evento.evento_fecha.isoformat() if evento.evento_fecha else None,
        'longitud': float(evento.longitud) if evento.longitud is not None else None,
        'latitud': float(evento.latitud) if evento.latitud is not None else None,
        'evento_categoria_id': evento.evento_categoria_id,
        'evento_tipo_id': evento.evento_tipo_id,
        'evento_causa_id': evento.evento_causa_id,
        'evento_origen_id': evento.evento_origen_id,
        'alto_impacto': bool(evento.alto_impacto),
        'descripcion': evento.descripcion,
        'situacion': evento.situacion,
        'evento_estado_id': evento.evento_estado_id,
        'activo': evento.activo,
        'creador': evento.creador,
        'creacion': evento.creacion.isoformat() if evento.creacion else None,
        'modificador': evento.modificador,
        'modificacion': evento.modificacion.isoformat() if evento.modificacion else None
    }), 201

@eventos_bp.route('/api/eventos/<int:id>', methods=['GET'])
def get_evento(id):
    """Obtener un evento por su ID.

    Parámetros:
      id (int): identificador del evento.

    Devuelve el objeto JSON del evento si existe, o 404 si no se encuentra.
    ---
    tags:
      - Eventos
    parameters:
      - name: id
        in: path
        type: integer
        required: true
    responses:
      200:
        description: Evento encontrado
      404:
        description: Evento no encontrado
    """
    result = db.session.execute(
        db.text("SELECT * FROM eventos WHERE id = :id"),
        {'id': id}
    )
    evento = result.fetchone()
    check_row_or_abort(evento, 'Evento no encontrado', 404)
    assert evento is not None

    return jsonify({
        'id': evento.id,
        'emergencia_id': evento.emergencia_id,
        'provincia_id': evento.provincia_id,
        'canton_id': evento.canton_id,
        'parroquia_id': evento.parroquia_id,
        'sector': evento.sector,
        'evento_fecha': evento.evento_fecha.isoformat() if evento.evento_fecha else None,
        'longitud': float(evento.longitud) if evento.longitud is not None else None,
        'latitud': float(evento.latitud) if evento.latitud is not None else None,
        'evento_categoria_id': evento.evento_categoria_id,
        'evento_tipo_id': evento.evento_tipo_id,
        'evento_causa_id': evento.evento_causa_id,
        'evento_origen_id': evento.evento_origen_id,
        'alto_impacto': bool(evento.alto_impacto),
        'descripcion': evento.descripcion,
        'situacion': evento.situacion,
        'evento_estado_id': evento.evento_estado_id,
        'activo': evento.activo,
        'creador': evento.creador,
        'creacion': evento.creacion.isoformat() if evento.creacion else None,
        'modificador': evento.modificador,
        'modificacion': evento.modificacion.isoformat() if evento.modificacion else None
    })

@eventos_bp.route('/api/eventos/<int:id>', methods=['PUT'])
def update_evento(id):
    """Actualizar un evento existente.

    Parámetros:
      id (int): identificador del evento a actualizar.
      body: JSON con los campos a actualizar.

    Actualiza los campos proporcionados y devuelve el evento actualizado.
    ---
    tags:
      - Eventos
    consumes:
      - application/json
    parameters:
      - name: id
        in: path
        type: integer
        required: true
    responses:
      200:
        description: Evento actualizado
      404:
        description: Evento no encontrado
    """
    data = request.get_json()
    now = datetime.now(timezone.utc)

    update_fields = []
    params = {'id': id, 'modificador': data.get('modificador', 'Sistema'), 'modificacion': now}

    fields = ['emergencia_id','provincia_id','canton_id','parroquia_id','sector','evento_fecha',
              'longitud','latitud','evento_categoria_id','evento_tipo_id','evento_causa_id',
              'evento_origen_id','alto_impacto','descripcion','situacion','evento_estado_id','activo']

    for field in fields:
        if field in data:
            update_fields.append(f"{field} = :{field}")
            params[field] = data[field]

    update_fields.append('modificador = :modificador')
    update_fields.append('modificacion = :modificacion')

    query = db.text(f"""
        UPDATE eventos
        SET {', '.join(update_fields)}
        WHERE id = :id
    """)

    result = db.session.execute(query, params)

    if getattr(result, 'rowcount', 0) == 0:
        return jsonify({'error': 'Evento no encontrado'}), 404

    db.session.commit()

    evento = db.session.execute(
        db.text("SELECT * FROM eventos WHERE id = :id"),
        {'id': id}
    ).fetchone()

    check_row_or_abort(evento, 'Evento no encontrado después de actualizar', 404)
    assert evento is not None

    return jsonify({
        'id': evento.id,
        'emergencia_id': evento.emergencia_id,
        'provincia_id': evento.provincia_id,
        'canton_id': evento.canton_id,
        'parroquia_id': evento.parroquia_id,
        'sector': evento.sector,
        'evento_fecha': evento.evento_fecha.isoformat() if evento.evento_fecha else None,
        'longitud': float(evento.longitud) if evento.longitud is not None else None,
        'latitud': float(evento.latitud) if evento.latitud is not None else None,
        'evento_categoria_id': evento.evento_categoria_id,
        'evento_tipo_id': evento.evento_tipo_id,
        'evento_causa_id': evento.evento_causa_id,
        'evento_origen_id': evento.evento_origen_id,
        'alto_impacto': bool(evento.alto_impacto),
        'descripcion': evento.descripcion,
        'situacion': evento.situacion,
        'evento_estado_id': evento.evento_estado_id,
        'activo': evento.activo,
        'creador': evento.creador,
        'creacion': evento.creacion.isoformat() if evento.creacion else None,
        'modificador': evento.modificador,
        'modificacion': evento.modificacion.isoformat() if evento.modificacion else None
    })

@eventos_bp.route('/api/eventos/<int:id>', methods=['DELETE'])
def delete_evento(id):
    """Eliminar un evento por ID.

    Parámetros:
      id (int): identificador del evento a eliminar.

    Elimina el registro de la tabla `eventos`. Devuelve 404 si no existe.
    ---
    tags:
      - Eventos
    parameters:
      - name: id
        in: path
        type: integer
        required: true
    responses:
      200:
        description: Eliminado correctamente
      404:
        description: Evento no encontrado
    """
    result = db.session.execute(
        db.text("DELETE FROM eventos WHERE id = :id"),
        {'id': id}
    )

    if getattr(result, 'rowcount', 0) == 0:
        return jsonify({'error': 'Evento no encontrado'}), 404

    db.session.commit()
    return jsonify({'mensaje': 'Evento eliminado correctamente'})
