from flask import request, jsonify
from eventos import eventos_bp
from models import db
from datetime import datetime, timezone

from utils.db_helpers import check_row_or_abort

# ==================== EVENTOS ====================

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
        schema:
          type: array
          items:
            type: object
            properties:
              id: {type: integer}
              emergencia_id: {type: integer}
              provincia_id: {type: integer}
              canton_id: {type: integer}
              parroquia_id: {type: integer}
              sector: {type: string}
              evento_fecha: {type: string, format: date-time}
              longitud: {type: number}
              latitud: {type: number}
              evento_tipo_id: {type: integer}
              evento_causa_id: {type: integer}
              evento_origen_id: {type: integer}
              alto_impacto: {type: boolean}
              descripcion: {type: string}
              situacion: {type: string}
              evento_atencion_estado_id: {type: integer}
              activo: {type: boolean}
              creador: {type: string}
              creacion: {type: string, format: date-time}
              modificador: {type: string}
              modificacion: {type: string, format: date-time}
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
            'evento_tipo_id': row.evento_tipo_id,
            'evento_causa_id': row.evento_causa_id,
            'evento_origen_id': row.evento_origen_id,
            'alto_impacto': bool(row.alto_impacto),
            'descripcion': row.descripcion,
            'situacion': row.situacion,
            'evento_atencion_estado_id': row.evento_atencion_estado_id,
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
        schema:
          type: array
          items:
            type: object
            properties:
              emergencia: {type: string}
              provincia: {type: string}
              canton: {type: string}
              parroquia: {type: string}
              sector: {type: string}
              evento_fecha: {type: string, format: date-time}
              longitud: {type: number}
              latitud: {type: number}
              evento_tipo: {type: string}
              evento_causa: {type: string}
              evento_origen: {type: string}
              alto_impacto: {type: boolean}
              evento_atencion_estado: {type: string}
              descripcion: {type: string}
              situacion: {type: string}
      404:
        description: Emergencia no encontrada
    """
    query = db.text(
        """SELECT
            e.id,
            x.nombre AS emergencia,
            p.nombre AS provincia,
            c.nombre AS canton,
            q.nombre AS parroquia,
            e.sector,
            e.evento_fecha,
            e.longitud,
            e.latitud,
            t.nombre AS evento_tipo,
            y.nombre AS evento_causa,
            o.nombre AS evento_origen,
            e.alto_impacto,
            z.nombre AS evento_atencion_estado,
            e.descripcion,
            e.situacion
            FROM public.eventos e
            INNER JOIN public.emergencias x ON e.emergencia_id = x.id
            INNER JOIN public.provincias p ON e.provincia_id = p.id
            INNER JOIN public.cantones c ON e.canton_id = c.id
            INNER JOIN public.parroquias q ON e.parroquia_id = q.id
            INNER JOIN public.evento_tipos t ON e.evento_tipo_id = t.id
            INNER JOIN public.evento_causas y ON e.evento_causa_id = y.id
            INNER JOIN public.evento_origenes o ON e.evento_origen_id = o.id
            INNER JOIN public.evento_atencion_estados z ON e.evento_atencion_estado_id = z.id
            WHERE e.emergencia_id = :emergencia_id
            ORDER BY e.id"""
    )
    result = db.session.execute(query, {'emergencia_id': emergencia_id})
    eventos = []
    for row in result:
        eventos.append({
            'id': row.id,
            'emergencia': row.emergencia,
            'provincia': row.provincia,
            'canton': row.canton,
            'parroquia': row.parroquia,
            'sector': row.sector,
            'evento_fecha': row.evento_fecha.isoformat() if getattr(row, 'evento_fecha', None) else None,
            'longitud': float(row.longitud) if getattr(row, 'longitud', None) is not None else None,
            'latitud': float(row.latitud) if getattr(row, 'latitud', None) is not None else None,
            'evento_tipo': getattr(row, 'evento_tipo', None),
            'evento_causa': getattr(row, 'evento_causa', None),
            'evento_origen': getattr(row, 'evento_origen', None),
            'alto_impacto': bool(getattr(row, 'alto_impacto', False)),
            'evento_atencion_estado': getattr(row, 'evento_atencion_estado', None),
            'descripcion': getattr(row, 'descripcion', None),
            'situacion': getattr(row, 'situacion', None)
        })
    return jsonify(eventos)
   
   
@eventos_bp.route('/api/eventos/emergencia/<int:emergencia_id>/provincia/<int:provincia_id>/canton/<int:canton_id>', methods=['GET'])
def get_eventos_by_emergencia_by_provincia_by_canton(emergencia_id, provincia_id, canton_id):
    """Obtener eventos filtrados por emergencia, provincia y cantón.

    Este endpoint devuelve los eventos correspondientes a una emergencia 
    específica, además de filtrar por provincia y cantón. 
    Cada registro incluye detalles del evento, ubicación, tipo, causa, 
    estado, descripción y situación.

    ---
    tags:
      - Eventos
    parameters:
      - name: emergencia_id
        in: path
        description: Identificador de la emergencia relacionada con los eventos
        required: true
        type: integer
      - name: provincia_id
        in: path
        description: Identificador de la provincia
        required: true
        type: integer
      - name: canton_id
        in: path
        description: Identificador del cantón
        required: true
        type: integer
    responses:
      200:
        description: Lista de eventos correspondientes a los filtros aplicados
        schema:
          type: array
          items:
            type: object
            properties:
              emergencia: {type: string}
              provincia: {type: string}
              canton: {type: string}
              parroquia: {type: string}
              sector: {type: string}
              evento_fecha: {type: string, format: date-time}
              longitud: {type: number}
              latitud: {type: number}
              evento_tipo: {type: string}
              evento_causa: {type: string}
              evento_origen: {type: string}
              alto_impacto: {type: boolean}
              evento_atencion_estado: {type: string}
              descripcion: {type: string}
              situacion: {type: string}
    """
    query = db.text("""
        SELECT
            e.id,
            x.nombre AS emergencia,
            p.nombre AS provincia,
            c.nombre AS canton,
            q.nombre AS parroquia,
            e.sector,
            e.evento_fecha,
            e.longitud,
            e.latitud,
            e.evento_tipo_id,
            e.evento_causa_id,
            e.evento_origen_id,
            e.evento_atencion_estado_id,
            t.nombre AS evento_tipo,
            y.nombre AS evento_causa,
            o.nombre AS evento_origen,
            e.alto_impacto,
            z.nombre AS evento_atencion_estado,
            e.descripcion,
            e.situacion
        FROM public.eventos e
        INNER JOIN public.emergencias x ON e.emergencia_id = x.id
        INNER JOIN public.provincias p ON e.provincia_id = p.id
        INNER JOIN public.cantones c ON e.canton_id = c.id
        INNER JOIN public.parroquias q ON e.parroquia_id = q.id
        INNER JOIN public.evento_tipos t ON e.evento_tipo_id = t.id
        INNER JOIN public.evento_causas y ON e.evento_causa_id = y.id
        INNER JOIN public.evento_origenes o ON e.evento_origen_id = o.id
        INNER JOIN public.evento_atencion_estados z ON e.evento_atencion_estado_id = z.id
        WHERE e.emergencia_id = :emergencia_id AND e.provincia_id = :provincia_id AND e.canton_id = :canton_id
        ORDER BY e.id
    """)
    result = db.session.execute(query, {
        'emergencia_id': emergencia_id,
        'provincia_id': provincia_id,
        'canton_id': canton_id
    })
    eventos = []
    for row in result:
        eventos.append({
            'id': row.id,
            'emergencia': row.emergencia,
            'provincia': row.provincia,
            'canton': row.canton,
            'parroquia': row.parroquia,
            'sector': row.sector,
            'evento_fecha': row.evento_fecha.isoformat() if row.evento_fecha else None,
            'longitud': float(row.longitud) if row.longitud is not None else None,
            'latitud': float(row.latitud) if row.latitud is not None else None,
            'evento_tipo': row.evento_tipo,
            'evento_causa': row.evento_causa,
            'evento_origen': row.evento_origen,
            'alto_impacto': bool(row.alto_impacto),
            'evento_atencion_estado': row.evento_atencion_estado,
            'descripcion': row.descripcion,
            'situacion': row.situacion
        })
    return jsonify(eventos)

@eventos_bp.route('/api/eventos', methods=['POST'])
def create_evento():
    """Crear un nuevo evento.

    Este endpoint recibe un JSON con los datos necesarios para registrar un nuevo evento
    en la tabla eventos. Devuelve el registro creado junto con un código 201 en caso de éxito.

    ---
    tags:
      - Eventos
    consumes:
      - application/json
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          required: [emergencia_id, provincia_id, canton_id, parroquia_id, evento_tipo_id, evento_causa_id, evento_origen_id, evento_atencion_estado_id]
          properties:
            emergencia_id: {type: integer}
            provincia_id: {type: integer}
            canton_id: {type: integer}
            parroquia_id: {type: integer}
            sector: {type: string}
            evento_fecha: {type: string, format: date-time}
            longitud: {type: number}
            latitud: {type: number}
            evento_tipo_id: {type: integer}
            evento_causa_id: {type: integer}
            evento_origen_id: {type: integer}
            alto_impacto: {type: boolean}
            descripcion: {type: string}
            situacion: {type: string}
            evento_atencion_estado_id: {type: integer}
            activo: {type: boolean}
            creador: {type: string}
            modificador: {type: string}
    responses:
      201:
        description: Evento creado correctamente
        schema:
          type: object
          properties:
            id: {type: integer}
            emergencia_id: {type: integer}
            provincia_id: {type: integer}
            canton_id: {type: integer}
            parroquia_id: {type: integer}
            sector: {type: string}
            evento_fecha: {type: string, format: date-time}
            longitud: {type: number}
            latitud: {type: number}
            evento_tipo_id: {type: integer}
            evento_causa_id: {type: integer}
            evento_origen_id: {type: integer}
            alto_impacto: {type: boolean}
            descripcion: {type: string}
            situacion: {type: string}
            evento_atencion_estado_id: {type: integer}
            activo: {type: boolean}
            creador: {type: string}
            creacion: {type: string, format: date-time}
            modificador: {type: string}
            modificacion: {type: string, format: date-time}
      400:
        description: Datos inválidos
    """
    data = request.get_json()
    now = datetime.now(timezone.utc)

    query = db.text("""
        INSERT INTO eventos (
            emergencia_id, provincia_id, canton_id, parroquia_id, sector,
            evento_fecha, longitud, latitud, evento_tipo_id,
            evento_causa_id, evento_origen_id, alto_impacto, descripcion, situacion,
            evento_atencion_estado_id, activo, creador, creacion, modificador, modificacion
        )
        VALUES (
            :emergencia_id, :provincia_id, :canton_id, :parroquia_id, :sector,
            :evento_fecha, :longitud, :latitud, :evento_tipo_id,
            :evento_causa_id, :evento_origen_id, :alto_impacto, :descripcion, :situacion,
            :evento_atencion_estado_id, :activo, :creador, :creacion, :modificador, :modificacion
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
        'evento_tipo_id': data['evento_tipo_id'],
        'evento_causa_id': data['evento_causa_id'],
        'evento_origen_id': data['evento_origen_id'],
        'alto_impacto': data.get('alto_impacto', False),
        'descripcion': data.get('descripcion'),
        'situacion': data.get('situacion'),
        'evento_atencion_estado_id': data['evento_atencion_estado_id'],
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
        'evento_tipo_id': evento.evento_tipo_id,
        'evento_causa_id': evento.evento_causa_id,
        'evento_origen_id': evento.evento_origen_id,
        'alto_impacto': bool(evento.alto_impacto),
        'descripcion': evento.descripcion,
        'situacion': evento.situacion,
        'evento_atencion_estado_id': evento.evento_atencion_estado_id,
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
        schema:
          type: object
          properties:
            id: {type: integer}
            emergencia_id: {type: integer}
            provincia_id: {type: integer}
            canton_id: {type: integer}
            parroquia_id: {type: integer}
            sector: {type: string}
            evento_fecha: {type: string, format: date-time}
            longitud: {type: number}
            latitud: {type: number}
            evento_tipo_id: {type: integer}
            evento_causa_id: {type: integer}
            evento_origen_id: {type: integer}
            alto_impacto: {type: boolean}
            descripcion: {type: string}
            situacion: {type: string}
            evento_atencion_estado_id: {type: integer}
            activo: {type: boolean}
            creador: {type: string}
            creacion: {type: string, format: date-time}
            modificador: {type: string}
            modificacion: {type: string, format: date-time}
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
        'evento_tipo_id': evento.evento_tipo_id,
        'evento_causa_id': evento.evento_causa_id,
        'evento_origen_id': evento.evento_origen_id,
        'alto_impacto': bool(evento.alto_impacto),
        'descripcion': evento.descripcion,
        'situacion': evento.situacion,
        'evento_atencion_estado_id': evento.evento_atencion_estado_id,
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
      - in: body
        name: body
        required: true
        schema:
          type: object
          properties:
            emergencia_id: {type: integer}
            provincia_id: {type: integer}
            canton_id: {type: integer}
            parroquia_id: {type: integer}
            sector: {type: string}
            evento_fecha: {type: string, format: date-time}
            longitud: {type: number}
            latitud: {type: number}
            evento_tipo_id: {type: integer}
            evento_causa_id: {type: integer}
            evento_origen_id: {type: integer}
            alto_impacto: {type: boolean}
            descripcion: {type: string}
            situacion: {type: string}
            evento_atencion_estado_id: {type: integer}
            activo: {type: boolean}
            modificador: {type: string}
    responses:
      200:
        description: Evento actualizado
        schema:
          type: object
          properties:
            id: {type: integer}
            emergencia_id: {type: integer}
            provincia_id: {type: integer}
            canton_id: {type: integer}
            parroquia_id: {type: integer}
            sector: {type: string}
            evento_fecha: {type: string, format: date-time}
            longitud: {type: number}
            latitud: {type: number}
            evento_tipo_id: {type: integer}
            evento_causa_id: {type: integer}
            evento_origen_id: {type: integer}
            alto_impacto: {type: boolean}
            descripcion: {type: string}
            situacion: {type: string}
            evento_atencion_estado_id: {type: integer}
            activo: {type: boolean}
            creador: {type: string}
            creacion: {type: string, format: date-time}
            modificador: {type: string}
            modificacion: {type: string, format: date-time}
      404:
        description: Evento no encontrado
    """
    data = request.get_json()
    now = datetime.now(timezone.utc)

    update_fields = []
    params = {'id': id, 'modificador': data.get('modificador', 'Sistema'), 'modificacion': now}

    fields = ['emergencia_id','provincia_id','canton_id','parroquia_id','sector','evento_fecha',
              'longitud','latitud','evento_tipo_id','evento_causa_id',
              'evento_origen_id','alto_impacto','descripcion','situacion','evento_atencion_estado_id','activo']

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
        'evento_tipo_id': evento.evento_tipo_id,
        'evento_causa_id': evento.evento_causa_id,
        'evento_origen_id': evento.evento_origen_id,
        'alto_impacto': bool(evento.alto_impacto),
        'descripcion': evento.descripcion,
        'situacion': evento.situacion,
        'evento_atencion_estado_id': evento.evento_atencion_estado_id,
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
