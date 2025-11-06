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
    query = db.text(
        """SELECT
            x.nombre AS emergencia,
            p.nombre AS provincia,
            c.nombre AS canton,
            q.nombre AS parroquia,
            e.sector,
            e.evento_fecha,
            e.longitud,
            e.latitud,
            k.nombre AS categoria,
            t.nombre AS tipo,
            y.nombre AS causa,
            o.nombre AS origen,
            e.alto_impacto,
            z.nombre AS estado,
            e.descripcion,
            e.situacion
            FROM public.eventos e
            INNER JOIN public.emergencias x ON e.emergencia_id = x.id
            INNER JOIN public.provincias p ON e.provincia_id = p.id
            INNER JOIN public.cantones c ON e.canton_id = c.id
            INNER JOIN public.parroquias q ON e.parroquia_id = q.id
            INNER JOIN public.evento_categorias k ON e.evento_categoria_id = k.id
            INNER JOIN public.evento_tipos t ON e.evento_tipo_id = t.id
            INNER JOIN public.evento_causas y ON e.evento_causa_id = y.id
            INNER JOIN public.evento_origenes o ON e.evento_origen_id = o.id
            INNER JOIN public.evento_estados z ON e.evento_estado_id = z.id
            WHERE e.emergencia_id = :emergencia_id
            ORDER BY e.id"""
    )
    result = db.session.execute(query, {'emergencia_id': emergencia_id})
    eventos = []
    for row in result:
        eventos.append({
            'emergencia': row.emergencia,
            'provincia': row.provincia,
            'canton': row.canton,
            'parroquia': row.parroquia,
            'sector': row.sector,
            'evento_fecha': row.evento_fecha.isoformat() if getattr(row, 'evento_fecha', None) else None,
            'longitud': float(row.longitud) if getattr(row, 'longitud', None) is not None else None,
            'latitud': float(row.latitud) if getattr(row, 'latitud', None) is not None else None,
            'categoria': getattr(row, 'categoria', None),
            'tipo': getattr(row, 'tipo', None),
            'causa': getattr(row, 'causa', None),
            'origen': getattr(row, 'origen', None),
            'alto_impacto': bool(getattr(row, 'alto_impacto', False)),
            'estado': getattr(row, 'estado', None),
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
    """
    query = db.text("""
        SELECT
            x.nombre AS emergencia,
            p.nombre AS provincia,
            c.nombre AS canton,
            q.nombre AS parroquia,
            e.sector,
            e.evento_fecha,
            e.longitud,
            e.latitud,
            k.nombre AS categoria,
            t.nombre AS tipo,
            y.nombre AS causa,
            o.nombre AS origen,
            e.alto_impacto,
            z.nombre AS estado,
            e.descripcion,
            e.situacion
        FROM public.eventos e
        INNER JOIN public.emergencias x ON e.emergencia_id = x.id
        INNER JOIN public.provincias p ON e.provincia_id = p.id
        INNER JOIN public.cantones c ON e.canton_id = c.id
        INNER JOIN public.parroquias q ON e.parroquia_id = q.id
        INNER JOIN public.evento_categorias k ON e.evento_categoria_id = k.id
        INNER JOIN public.evento_tipos t ON e.evento_tipo_id = t.id
        INNER JOIN public.evento_causas y ON e.evento_causa_id = y.id
        INNER JOIN public.evento_origenes o ON e.evento_origen_id = o.id
        INNER JOIN public.evento_estados z ON e.evento_estado_id = z.id
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
            'emergencia': row.emergencia,
            'provincia': row.provincia,
            'canton': row.canton,
            'parroquia': row.parroquia,
            'sector': row.sector,
            'evento_fecha': row.evento_fecha.isoformat() if row.evento_fecha else None,
            'longitud': float(row.longitud) if row.longitud is not None else None,
            'latitud': float(row.latitud) if row.latitud is not None else None,
            'categoria': row.categoria,
            'tipo': row.tipo,
            'causa': row.causa,
            'origen': row.origen,
            'alto_impacto': bool(row.alto_impacto),
            'estado': row.estado,
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
    responses:
      201:
        description: Evento creado correctamente
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


    if getattr(result, 'rowcount', 0) == 0:
        return jsonify({'error': 'Evento no encontrado'}), 404

    db.session.commit()
    return jsonify({'mensaje': 'Evento eliminado correctamente'})

# (Removed duplicated endpoint groups for evento_tipos, evento_origenes, evento_estados, evento_causas, evento_categorias)
# All now live in their respective independent modules under /evento_* directories.

@eventos_bp.route('/api/evento_tipos', methods=['GET'])
def get_evento_tipos():
    """
    Listar todos los tipos de eventos registrados.

    ---
    tags:
      - Tipos de Evento
    responses:
      200:
        description: Lista de tipos de eventos obtenida correctamente
    """
    query = db.text("SELECT * FROM evento_tipos ORDER BY id")
    result = db.session.execute(query)
    tipos = []
    for row in result:
        tipos.append({
            'id': row.id,
            'nombre': row.nombre,
            'descripcion': row.descripcion,
            'activo': row.activo,
            'creador': row.creador,
            'creacion': row.creacion.isoformat() if row.creacion else None,
            'modificador': row.modificador,
            'modificacion': row.modificacion.isoformat() if row.modificacion else None,
            'identificador': row.identificador
        })
    return jsonify(tipos)


@eventos_bp.route('/api/evento_tipos/<int:id>', methods=['GET'])
def get_evento_tipo(id):
    """
    Obtener información detallada de un tipo de evento específico.

    ---
    tags:
      - Tipos de Evento
    parameters:
      - name: id
        in: path
        description: ID del tipo de evento
        required: true
        type: integer
    responses:
      200:
        description: Tipo de evento encontrado y devuelto correctamente
      404:
        description: No se encontró el tipo de evento solicitado
    """
    query = db.text("SELECT * FROM evento_tipos WHERE id = :id")
    result = db.session.execute(query, {'id': id}).fetchone()
    if result is None:
        return jsonify({'error': 'Tipo de evento no encontrado'}), 404
    return jsonify({
        'id': result.id,
        'nombre': result.nombre,
        'descripcion': result.descripcion,
        'activo': result.activo,
        'creador': result.creador,
        'creacion': result.creacion.isoformat() if getattr(result, 'creacion', None) else None,
        'modificador': result.modificador,
        'modificacion': result.modificacion.isoformat() if getattr(result, 'modificacion', None) else None,
        'identificador': getattr(result, 'identificador', None)
    })


@eventos_bp.route('/api/evento_tipos', methods=['POST'])
def create_evento_tipo():
    """Crear un nuevo tipo de evento."""
    data = request.get_json()
    now = datetime.now(timezone.utc)
    query = db.text("""
        INSERT INTO evento_tipos (nombre, descripcion, activo, creador, creacion, modificador, modificacion, identificador)
        VALUES (:nombre, :descripcion, :activo, :creador, :creacion, :modificador, :modificacion, :identificador)
        RETURNING id
    """)
    result = db.session.execute(query, {
        'nombre': data['nombre'],
        'descripcion': data.get('descripcion'),
        'activo': data.get('activo', True),
        'creador': data.get('creador', 'Sistema'),
        'creacion': now,
        'modificador': data.get('modificador', data.get('creador', 'Sistema')),
        'modificacion': now,
        'identificador': data.get('identificador')
    })
    row = result.fetchone()
    if row is None:
        db.session.rollback()
        return jsonify({'error': 'Fallo la creación del tipo de evento'}), 500
    tipo_id = row[0]
    db.session.commit()
    tipo = db.session.execute(db.text("SELECT * FROM evento_tipos WHERE id = :id"), {'id': tipo_id}).fetchone()
    return jsonify({
        'id': getattr(tipo, 'id', None),
        'nombre': getattr(tipo, 'nombre', None),
        'descripcion': getattr(tipo, 'descripcion', None),
        'activo': getattr(tipo, 'activo', None),
        'creador': getattr(tipo, 'creador', None),
        'creacion': tipo.creacion.isoformat() if (tipo is not None and getattr(tipo, 'creacion', None)) else None,
        'modificador': getattr(tipo, 'modificador', None),
        'modificacion': tipo.modificacion.isoformat() if (tipo is not None and getattr(tipo, 'modificacion', None) is not None) else None,
        'identificador': getattr(tipo, 'identificador', None)
    }), 201


@eventos_bp.route('/api/evento_tipos/<int:id>', methods=['PUT'])
def update_evento_tipo(id):
    """Actualizar un tipo de evento."""
    data = request.get_json()
    now = datetime.now(timezone.utc)
    update_fields = []
    params = {'id': id, 'modificador': data.get('modificador', 'Sistema'), 'modificacion': now}
    fields = ['nombre', 'descripcion', 'activo', 'identificador']
    for field in fields:
        if field in data:
            update_fields.append(f"{field} = :{field}")
            params[field] = data[field]
    update_fields.append('modificador = :modificador')
    update_fields.append('modificacion = :modificacion')
    query = db.text(f"""
        UPDATE evento_tipos
        SET {', '.join(update_fields)}
        WHERE id = :id
    """)
    result = db.session.execute(query, params)
    if getattr(result, 'rowcount', 0) == 0:
        return jsonify({'error': 'Tipo de evento no encontrado'}), 404
    db.session.commit()
    tipo = db.session.execute(db.text("SELECT * FROM evento_tipos WHERE id = :id"), {'id': id}).fetchone()
    if tipo is None:
        return jsonify({'error': 'Tipo de evento no encontrado después de actualizar'}), 404
    return jsonify({
        'id': getattr(tipo, 'id', None),
        'nombre': getattr(tipo, 'nombre', None),
        'descripcion': getattr(tipo, 'descripcion', None),
        'activo': getattr(tipo, 'activo', None),
        'creador': getattr(tipo, 'creador', None),
        'creacion': tipo.creacion.isoformat() if getattr(tipo, 'creacion', None) else None,
        'modificador': getattr(tipo, 'modificador', None),
        'modificacion': tipo.modificacion.isoformat() if getattr(tipo, 'modificacion', None) else None,
        'identificador': getattr(tipo, 'identificador', None)
    })


@eventos_bp.route('/api/evento_tipos/<int:id>', methods=['DELETE'])
def delete_evento_tipo(id):
    """Eliminar un tipo de evento."""
    result = db.session.execute(db.text("DELETE FROM evento_tipos WHERE id = :id"), {'id': id})
    if getattr(result, 'rowcount', 0) == 0:
        return jsonify({'error': 'Tipo de evento no encontrado'}), 404
    db.session.commit()
    return jsonify({'mensaje': 'Tipo de evento eliminado correctamente'})


# ==================== EVENTO ORIGENES ====================

@eventos_bp.route('/api/evento_origenes', methods=['GET'])
def get_evento_origenes():
    """
    Listar todos los orígenes de eventos registrados.

    ---
    tags:
      - Orígenes de Evento
    responses:
      200:
        description: Lista de orígenes de eventos obtenida correctamente
    """
    query = db.text("SELECT * FROM evento_origenes ORDER BY id")
    result = db.session.execute(query)
    origenes = []
    for row in result:
        origenes.append({
            'id': row.id,
            'nombre': row.nombre,
            'descripcion': row.descripcion,
            'activo': row.activo,
            'creador': row.creador,
            'creacion': row.creacion.isoformat() if row.creacion else None,
            'modificador': row.modificador,
            'modificacion': row.modificacion.isoformat() if row.modificacion else None
        })
    return jsonify(origenes)


@eventos_bp.route('/api/evento_origenes/<int:id>', methods=['GET'])
def get_evento_origen(id):
    """
    Obtener información detallada de un origen de evento específico.

    ---
    tags:
      - Orígenes de Evento
    parameters:
      - name: id
        in: path
        description: ID del origen de evento
        required: true
        type: integer
    responses:
      200:
        description: Origen de evento encontrado
      404:
        description: No se encontró el origen de evento solicitado
    """
    query = db.text("SELECT * FROM evento_origenes WHERE id = :id")
    result = db.session.execute(query, {'id': id}).fetchone()
    if result is None:
        return jsonify({'error': 'Origen de evento no encontrado'}), 404
    return jsonify({
        'id': result.id,
        'nombre': result.nombre,
        'descripcion': result.descripcion,
        'activo': result.activo,
        'creador': result.creador,
        'creacion': result.creacion.isoformat() if result.creacion else None,
        'modificador': result.modificador,
        'modificacion': result.modificacion.isoformat() if result.modificacion else None
    })


@eventos_bp.route('/api/evento_origenes', methods=['POST'])
def create_evento_origen():
    """
    Crear un nuevo origen de evento.

    ---
    tags:
      - Orígenes de Evento
    consumes:
      - application/json
    responses:
      201:
        description: Origen de evento creado correctamente
      400:
        description: Datos inválidos
    """
    data = request.get_json()
    now = datetime.now(timezone.utc)
    query = db.text("""
        INSERT INTO evento_origenes (nombre, descripcion, activo, creador, creacion, modificador, modificacion)
        VALUES (:nombre, :descripcion, :activo, :creador, :creacion, :modificador, :modificacion)
        RETURNING id
    """)
    result = db.session.execute(query, {
        'nombre': data['nombre'],
        'descripcion': data.get('descripcion'),
        'activo': data.get('activo', True),
        'creador': data.get('creador', 'Sistema'),
        'creacion': now,
        'modificador': data.get('modificador', data.get('creador', 'Sistema')),
        'modificacion': now
    })
    row = result.fetchone()
    if row is None:
        db.session.rollback()
        return jsonify({'error': 'Fallo la creación del origen de evento'}), 500
    origen_id = row[0]
    db.session.commit()
    origen = db.session.execute(db.text("SELECT * FROM evento_origenes WHERE id = :id"), {'id': origen_id}).fetchone()
    if origen is None:
        return jsonify({'error': 'Origen de evento no encontrado después de la creación'}), 404
    return jsonify({
        'id': getattr(origen, 'id', None),
        'nombre': getattr(origen, 'nombre', None),
        'descripcion': getattr(origen, 'descripcion', None),
        'activo': getattr(origen, 'activo', None),
        'creador': getattr(origen, 'creador', None),
        'creacion': origen.creacion.isoformat() if getattr(origen, 'creacion', None) else None,
        'modificador': getattr(origen, 'modificador', None),
        'modificacion': origen.modificacion.isoformat() if getattr(origen, 'modificacion', None) else None
    }), 201


@eventos_bp.route('/api/evento_origenes/<int:id>', methods=['PUT'])
def update_evento_origen(id):
    """
    Actualizar un origen de evento existente.

    ---
    tags:
      - Orígenes de Evento
    consumes:
      - application/json
    parameters:
      - name: id
        in: path
        description: ID del origen de evento a actualizar
        required: true
        type: integer
    responses:
      200:
        description: Origen de evento actualizado correctamente
      404:
        description: Origen de evento no encontrado
    """
    data = request.get_json()
    now = datetime.now(timezone.utc)
    update_fields = []
    params = {'id': id, 'modificador': data.get('modificador', 'Sistema'), 'modificacion': now}
    fields = ['nombre', 'descripcion', 'activo']
    for field in fields:
        if field in data:
            update_fields.append(f"{field} = :{field}")
            params[field] = data[field]
    update_fields.append('modificador = :modificador')
    update_fields.append('modificacion = :modificacion')
    query = db.text(f"""
        UPDATE evento_origenes
        SET {', '.join(update_fields)}
        WHERE id = :id
    """)
    result = db.session.execute(query, params)
    if getattr(result, 'rowcount', 0) == 0:
        return jsonify({'error': 'Origen de evento no encontrado'}), 404
    db.session.commit()
    origen = db.session.execute(db.text("SELECT * FROM evento_origenes WHERE id = :id"), {'id': id}).fetchone()
    if origen is None:
        return jsonify({'error': 'Origen de evento no encontrado después de actualizar'}), 404
    return jsonify({
        'id': getattr(origen, 'id', None),
        'nombre': getattr(origen, 'nombre', None),
        'descripcion': getattr(origen, 'descripcion', None),
        'activo': getattr(origen, 'activo', None),
        'creador': getattr(origen, 'creador', None),
        'creacion': origen.creacion.isoformat() if getattr(origen, 'creacion', None) else None,
        'modificador': getattr(origen, 'modificador', None),
        'modificacion': origen.modificacion.isoformat() if getattr(origen, 'modificacion', None) else None
    })


@eventos_bp.route('/api/evento_origenes/<int:id>', methods=['DELETE'])
def delete_evento_origen(id):
    """
    Eliminar un origen de evento del sistema.

    ---
    tags:
      - Orígenes de Evento
    parameters:
      - name: id
        in: path
        description: ID del origen de evento a eliminar
        required: true
        type: integer
    responses:
      200:
        description: Origen de evento eliminado correctamente
      404:
        description: Origen de evento no encontrado
    """
    result = db.session.execute(db.text("DELETE FROM evento_origenes WHERE id = :id"), {'id': id})
    if getattr(result, 'rowcount', 0) == 0:
        return jsonify({'error': 'Origen de evento no encontrado'}), 404
    db.session.commit()
    return jsonify({'mensaje': 'Origen de evento eliminado correctamente'})

# ==================== EVENTO ESTADOS ====================

@eventos_bp.route('/api/evento_estados', methods=['GET'])
def get_evento_estados():
    """Listar todos los estados de eventos registrados."""
    query = db.text("SELECT * FROM evento_estados ORDER BY id")
    result = db.session.execute(query)
    estados = []
    for row in result:
        estados.append({
            'id': row.id,
            'nombre': row.nombre,
            'descripcion': row.descripcion,
            'activo': row.activo,
            'creador': row.creador,
            'creacion': row.creacion.isoformat() if getattr(row, 'creacion', None) else None,
            'modificador': row.modificador,
            'modificacion': row.modificacion.isoformat() if getattr(row, 'modificacion', None) else None
        })
    return jsonify(estados)


@eventos_bp.route('/api/evento_estados/<int:id>', methods=['GET'])
def get_evento_estado(id):
    """
    Obtener un estado de evento específico por ID.

    Parámetros:
      id (int): Identificador del estado de evento.

    ---
    tags:
      - Estados de Evento
    responses:
      200:
        description: Estado de evento encontrado
      404:
        description: Estado de evento no encontrado
    """
    estado = db.session.execute(db.text("SELECT * FROM evento_estados WHERE id = :id"), {'id': id}).fetchone()
    if estado is None:
        return jsonify({'error': 'Estado de evento no encontrado'}), 404
    return jsonify({
        'id': getattr(estado, 'id', None),
        'nombre': getattr(estado, 'nombre', None),
        'descripcion': getattr(estado, 'descripcion', None),
        'activo': getattr(estado, 'activo', None),
        'creador': getattr(estado, 'creador', None),
        'creacion': estado.creacion.isoformat() if getattr(estado, 'creacion', None) else None,
        'modificador': getattr(estado, 'modificador', None),
        'modificacion': estado.modificacion.isoformat() if getattr(estado, 'modificacion', None) else None
    })


@eventos_bp.route('/api/evento_estados', methods=['POST'])
def create_evento_estado():
    """
    Crear un nuevo estado de evento.

    Recibe JSON con los siguientes campos:
    - nombre (texto, obligatorio)
    - descripcion (texto, opcional)
    - activo (booleano, por defecto True)
    - creador y modificador (opcional, texto)

    ---
    tags:
      - Estados de Evento
    consumes:
      - application/json
    responses:
      201:
        description: Estado de evento creado correctamente
      400:
        description: Datos inválidos
    """
    data = request.get_json()
    now = datetime.now(timezone.utc)
    query = db.text("""
        INSERT INTO evento_estados (nombre, descripcion, activo, creador, creacion, modificador, modificacion)
        VALUES (:nombre, :descripcion, :activo, :creador, :creacion, :modificador, :modificacion)
        RETURNING id
    """)
    result = db.session.execute(query, {
        'nombre': data['nombre'],
        'descripcion': data.get('descripcion'),
        'activo': data.get('activo', True),
        'creador': data.get('creador', 'Sistema'),
        'creacion': now,
        'modificador': data.get('modificador', data.get('creador', 'Sistema')),
        'modificacion': now
    })
    row = result.fetchone()
    if row is None:
        db.session.rollback()
        return jsonify({'error': 'Fallo la creación del estado de evento'}), 500
    estado_id = row[0]
    db.session.commit()
    estado = db.session.execute(db.text("SELECT * FROM evento_estados WHERE id = :id"), {'id': estado_id}).fetchone()
    return jsonify({
        'id': getattr(estado, 'id', None),
        'nombre': getattr(estado, 'nombre', None),
        'descripcion': getattr(estado, 'descripcion', None),
        'activo': getattr(estado, 'activo', None),
        'creador': getattr(estado, 'creador', None),
        'creacion': estado.creacion.isoformat() if (estado is not None and getattr(estado, 'creacion', None) is not None) else None,
        'modificador': getattr(estado, 'modificador', None),
        'modificacion': estado.modificacion.isoformat() if (estado is not None and getattr(estado, 'modificacion', None) is not None) else None
    }), 201


@eventos_bp.route('/api/evento_estados/<int:id>', methods=['PUT'])
def update_evento_estado(id):
    """
    Actualizar un estado de evento existente.

    Permite modificar uno o más campos del registro especificado.
    Los campos aceptados son: nombre, descripcion, activo.

    ---
    tags:
      - Estados de Evento
    consumes:
      - application/json
    responses:
      200:
        description: Estado de evento actualizado correctamente
      404:
        description: Estado de evento no encontrado
    """
    data = request.get_json()
    now = datetime.now(timezone.utc)
    update_fields = []
    params = {'id': id, 'modificador': data.get('modificador', 'Sistema'), 'modificacion': now}
    fields = ['nombre', 'descripcion', 'activo']
    for field in fields:
        if field in data:
            update_fields.append(f"{field} = :{field}")
            params[field] = data[field]
    update_fields.append('modificador = :modificador')
    update_fields.append('modificacion = :modificacion')
    query = db.text(f"""
        UPDATE evento_estados
        SET {', '.join(update_fields)}
        WHERE id = :id
    """)
    result = db.session.execute(query, params)
    if getattr(result, 'rowcount', 0) == 0:
        return jsonify({'error': 'Estado de evento no encontrado'}), 404
    db.session.commit()
    estado = db.session.execute(db.text("SELECT * FROM evento_estados WHERE id = :id"), {'id': id}).fetchone()
    if estado is None:
        return jsonify({'error': 'Estado de evento no encontrado después de actualizar'}), 404
    return jsonify({
        'id': getattr(estado, 'id', None),
        'nombre': getattr(estado, 'nombre', None),
        'descripcion': getattr(estado, 'descripcion', None),
        'activo': getattr(estado, 'activo', None),
        'creador': getattr(estado, 'creador', None),
        'creacion': estado.creacion.isoformat() if getattr(estado, 'creacion', None) else None,
        'modificador': getattr(estado, 'modificador', None),
        'modificacion': estado.modificacion.isoformat() if getattr(estado, 'modificacion', None) else None
    })


@eventos_bp.route('/api/evento_estados/<int:id>', methods=['DELETE'])
def delete_evento_estado(id):
    """
    Eliminar un estado de evento existente.

    Parámetros:
      id (int): Identificador del estado de evento a eliminar.

    ---
    tags:
      - Estados de Evento
    responses:
      200:
        description: Estado de evento eliminado correctamente
      404:
        description: Estado de evento no encontrado
    """
    result = db.session.execute(db.text("DELETE FROM evento_estados WHERE id = :id"), {'id': id})
    if getattr(result, 'rowcount', 0) == 0:
        return jsonify({'error': 'Estado de evento no encontrado'}), 404
    db.session.commit()
    return jsonify({'mensaje': 'Estado de evento eliminado correctamente'})


# ==================== EVENTO CAUSAS ====================

@eventos_bp.route('/api/evento_causas', methods=['GET'])
def get_evento_causas():
    """
    Listar todas las causas de eventos registradas.

    Devuelve una lista completa de las causas almacenadas en la tabla `evento_causas`.

    ---
    tags:
      - Causas de Evento
    responses:
      200:
        description: Lista de causas de eventos obtenida correctamente
    """
    query = db.text("SELECT * FROM evento_causas ORDER BY id")
    result = db.session.execute(query)
    causas = []
    for row in result:
        causas.append({
            'id': row.id,
            'nombre': row.nombre,
            'descripcion': row.descripcion,
            'activo': row.activo,
            'creador': row.creador,
            'creacion': row.creacion.isoformat() if getattr(row, 'creacion', None) else None,
            'modificador': row.modificador,
            'modificacion': row.modificacion.isoformat() if getattr(row, 'modificacion', None) else None
        })
    return jsonify(causas)


@eventos_bp.route('/api/evento_causas/<int:id>', methods=['GET'])
def get_evento_causa(id):
    """
    Obtener una causa de evento específica por ID.

    Parámetros:
      id (int): Identificador de la causa de evento.

    ---
    tags:
      - Causas de Evento
    responses:
      200:
        description: Causa de evento encontrada
      404:
        description: Causa de evento no encontrada
    """
    causa = db.session.execute(db.text("SELECT * FROM evento_causas WHERE id = :id"), {'id': id}).fetchone()
    if causa is None:
        return jsonify({'error': 'Causa de evento no encontrada'}), 404
    return jsonify({
        'id': getattr(causa, 'id', None),
        'nombre': getattr(causa, 'nombre', None),
        'descripcion': getattr(causa, 'descripcion', None),
        'activo': getattr(causa, 'activo', None),
        'creador': getattr(causa, 'creador', None),
        'creacion': causa.creacion.isoformat() if getattr(causa, 'creacion', None) else None,
        'modificador': getattr(causa, 'modificador', None),
        'modificacion': causa.modificacion.isoformat() if getattr(causa, 'modificacion', None) else None
    })


@eventos_bp.route('/api/evento_causas', methods=['POST'])
def create_evento_causa():
    """
    Crear una nueva causa de evento.

    Recibe un cuerpo JSON con los campos requeridos para insertar un nuevo registro
    en la tabla `evento_causas`.

    ---
    tags:
      - Causas de Evento
    consumes:
      - application/json
    responses:
      201:
        description: Causa de evento creada correctamente
      400:
        description: Datos inválidos
    """
    data = request.get_json()
    now = datetime.now(timezone.utc)
    query = db.text("""
        INSERT INTO evento_causas (nombre, descripcion, activo, creador, creacion, modificador, modificacion)
        VALUES (:nombre, :descripcion, :activo, :creador, :creacion, :modificador, :modificacion)
        RETURNING id
    """)
    result = db.session.execute(query, {
        'nombre': data['nombre'],
        'descripcion': data.get('descripcion'),
        'activo': data.get('activo', True),
        'creador': data.get('creador', 'Sistema'),
        'creacion': now,
        'modificador': data.get('modificador', data.get('creador', 'Sistema')),
        'modificacion': now
    })
    row = result.fetchone()
    if row is None:
        db.session.rollback()
        return jsonify({'error': 'Fallo la creación de la causa de evento'}), 500
    causa_id = row[0]
    db.session.commit()
    causa = db.session.execute(db.text("SELECT * FROM evento_causas WHERE id = :id"), {'id': causa_id}).fetchone()
    return jsonify({
        'id': getattr(causa, 'id', None),
        'nombre': getattr(causa, 'nombre', None),
        'descripcion': getattr(causa, 'descripcion', None),
        'activo': getattr(causa, 'activo', None),
        'creador': getattr(causa, 'creador', None),
        'creacion': causa.creacion.isoformat() if (causa is not None and getattr(causa, 'creacion', None) is not None) else None,
        'modificador': getattr(causa, 'modificador', None),
        'modificacion': causa.modificacion.isoformat() if (causa is not None and getattr(causa, 'modificacion', None) is not None) else None
    }), 201


@eventos_bp.route('/api/evento_causas/<int:id>', methods=['PUT'])
def update_evento_causa(id):
    """
    Actualizar una causa de evento existente.

    Permite modificar uno o más campos de una causa de evento existente.

    ---
    tags:
      - Causas de Evento
    consumes:
      - application/json
    responses:
      200:
        description: Causa de evento actualizada correctamente
      404:
        description: Causa de evento no encontrada
    """
    data = request.get_json()
    now = datetime.now(timezone.utc)
    update_fields = []
    params = {'id': id, 'modificador': data.get('modificador', 'Sistema'), 'modificacion': now}
    fields = ['nombre', 'descripcion', 'activo']
    for field in fields:
        if field in data:
            update_fields.append(f"{field} = :{field}")
            params[field] = data[field]
    update_fields.append('modificador = :modificador')
    update_fields.append('modificacion = :modificacion')
    query = db.text(f"""
        UPDATE evento_causas
        SET {', '.join(update_fields)}
        WHERE id = :id
    """)
    result = db.session.execute(query, params)
    if getattr(result, 'rowcount', 0) == 0:
        return jsonify({'error': 'Causa de evento no encontrada'}), 404
    db.session.commit()
    causa = db.session.execute(db.text("SELECT * FROM evento_causas WHERE id = :id"), {'id': id}).fetchone()
    if causa is None:
        return jsonify({'error': 'Causa de evento no encontrada después de actualizar'}), 404
    return jsonify({
        'id': getattr(causa, 'id', None),
        'nombre': getattr(causa, 'nombre', None),
        'descripcion': getattr(causa, 'descripcion', None),
        'activo': getattr(causa, 'activo', None),
        'creador': getattr(causa, 'creador', None),
        'creacion': causa.creacion.isoformat() if getattr(causa, 'creacion', None) else None,
        'modificador': getattr(causa, 'modificador', None),
        'modificacion': causa.modificacion.isoformat() if getattr(causa, 'modificacion', None) else None
    })


@eventos_bp.route('/api/evento_causas/<int:id>', methods=['DELETE'])
def delete_evento_causa(id):
    """
    Eliminar una causa de evento existente.

    Parámetros:
      id (int): Identificador de la causa de evento a eliminar.

    ---
    tags:
      - Causas de Evento
    responses:
      200:
        description: Causa de evento eliminada correctamente
      404:
        description: Causa de evento no encontrada
    """
    result = db.session.execute(db.text("DELETE FROM evento_causas WHERE id = :id"), {'id': id})
    if getattr(result, 'rowcount', 0) == 0:
        return jsonify({'error': 'Causa de evento no encontrada'}), 404
    db.session.commit()
    return jsonify({'mensaje': 'Causa de evento eliminada correctamente'})


# ==================== EVENTO CATEGORIAS ====================

@eventos_bp.route('/api/evento_categorias', methods=['GET'])
def get_evento_categorias():
    """
    Listar todas las categorías de eventos registradas.

    Devuelve una lista completa de categorías almacenadas en la tabla `evento_categorias`.

    ---
    tags:
      - Categorías de Evento
    responses:
      200:
        description: Lista de categorías de eventos obtenida correctamente
    """
    query = db.text("SELECT * FROM evento_categorias ORDER BY id")
    result = db.session.execute(query)
    categorias = []
    for row in result:
        categorias.append({
            'id': row.id,
            'nombre': row.nombre,
            'descripcion': row.descripcion,
            'activo': row.activo,
            'creador': row.creador,
            'creacion': row.creacion.isoformat() if getattr(row, 'creacion', None) else None,
            'modificador': row.modificador,
            'modificacion': row.modificacion.isoformat() if getattr(row, 'modificacion', None) else None
        })
    return jsonify(categorias)


@eventos_bp.route('/api/evento_categorias/<int:id>', methods=['GET'])
def get_evento_categoria(id):
    """
    Obtener una categoría de evento específica por ID.

    Parámetros:
      id (int): Identificador de la categoría de evento.

    ---
    tags:
      - Categorías de Evento
    responses:
      200:
        description: Categoría de evento encontrada
      404:
        description: Categoría de evento no encontrada
    """
    categoria = db.session.execute(db.text("SELECT * FROM evento_categorias WHERE id = :id"), {'id': id}).fetchone()
    if categoria is None:
        return jsonify({'error': 'Categoría de evento no encontrada'}), 404
    return jsonify({
        'id': getattr(categoria, 'id', None),
        'nombre': getattr(categoria, 'nombre', None),
        'descripcion': getattr(categoria, 'descripcion', None),
        'activo': getattr(categoria, 'activo', None),
        'creador': getattr(categoria, 'creador', None),
        'creacion': categoria.creacion.isoformat() if getattr(categoria, 'creacion', None) else None,
        'modificador': getattr(categoria, 'modificador', None),
        'modificacion': categoria.modificacion.isoformat() if getattr(categoria, 'modificacion', None) else None
    })


@eventos_bp.route('/api/evento_categorias', methods=['POST'])
def create_evento_categoria():
    """
    Crear una nueva categoría de evento.

    Recibe un cuerpo JSON con los campos requeridos para insertar un nuevo registro
    en la tabla `evento_categorias`.

    ---
    tags:
      - Categorías de Evento
    consumes:
      - application/json
    responses:
      201:
        description: Categoría de evento creada correctamente
      400:
        description: Datos inválidos
    """
    data = request.get_json()
    now = datetime.now(timezone.utc)
    query = db.text("""
        INSERT INTO evento_categorias (nombre, descripcion, activo, creador, creacion, modificador, modificacion)
        VALUES (:nombre, :descripcion, :activo, :creador, :creacion, :modificador, :modificacion)
        RETURNING id
    """)
    result = db.session.execute(query, {
        'nombre': data['nombre'],
        'descripcion': data.get('descripcion'),
        'activo': data.get('activo', True),
        'creador': data.get('creador', 'Sistema'),
        'creacion': now,
        'modificador': data.get('modificador', data.get('creador', 'Sistema')),
        'modificacion': now
    })
    row = result.fetchone()
    if row is None:
        db.session.rollback()
        return jsonify({'error': 'Fallo la creación de la categoría de evento'}), 500
    categoria_id = row[0]
    db.session.commit()
    categoria = db.session.execute(db.text("SELECT * FROM evento_categorias WHERE id = :id"), {'id': categoria_id}).fetchone()
    return jsonify({
        'id': getattr(categoria, 'id', None),
        'nombre': getattr(categoria, 'nombre', None),
        'descripcion': getattr(categoria, 'descripcion', None),
        'activo': getattr(categoria, 'activo', None),
        'creador': getattr(categoria, 'creador', None),
        'creacion': categoria.creacion.isoformat() if (categoria is not None and getattr(categoria, 'creacion', None) is not None) else None,
        'modificador': getattr(categoria, 'modificador', None),
        'modificacion': categoria.modificacion.isoformat() if (categoria is not None and getattr(categoria, 'modificacion', None) is not None) else None
    }), 201


@eventos_bp.route('/api/evento_categorias/<int:id>', methods=['PUT'])
def update_evento_categoria(id):
    """
    Actualizar una categoría de evento existente.

    Permite modificar uno o más campos de la categoría de evento.

    ---
    tags:
      - Categorías de Evento
    consumes:
      - application/json
    responses:
      200:
        description: Categoría de evento actualizada correctamente
      404:
        description: Categoría de evento no encontrada
    """
    data = request.get_json()
    now = datetime.now(timezone.utc)
    update_fields = []
    params = {'id': id, 'modificador': data.get('modificador', 'Sistema'), 'modificacion': now}
    fields = ['nombre', 'descripcion', 'activo']
    for field in fields:
        if field in data:
            update_fields.append(f"{field} = :{field}")
            params[field] = data[field]
    update_fields.append('modificador = :modificador')
    update_fields.append('modificacion = :modificacion')
    query = db.text(f"""
        UPDATE evento_categorias
        SET {', '.join(update_fields)}
        WHERE id = :id
    """)
    result = db.session.execute(query, params)
    if getattr(result, 'rowcount', 0) == 0:
        return jsonify({'error': 'Categoría de evento no encontrada'}), 404
    db.session.commit()
    categoria = db.session.execute(db.text("SELECT * FROM evento_categorias WHERE id = :id"), {'id': id}).fetchone()
    if categoria is None:
        return jsonify({'error': 'Categoría de evento no encontrada después de actualizar'}), 404
    return jsonify({
        'id': getattr(categoria, 'id', None),
        'nombre': getattr(categoria, 'nombre', None),
        'descripcion': getattr(categoria, 'descripcion', None),
        'activo': getattr(categoria, 'activo', None),
        'creador': getattr(categoria, 'creador', None),
        'creacion': categoria.creacion.isoformat() if getattr(categoria, 'creacion', None) else None,
        'modificador': getattr(categoria, 'modificador', None),
        'modificacion': categoria.modificacion.isoformat() if getattr(categoria, 'modificacion', None) else None
    })


@eventos_bp.route('/api/evento_categorias/<int:id>', methods=['DELETE'])
def delete_evento_categoria(id):
    """
    Eliminar una categoría de evento existente.

    Parámetros:
      id (int): Identificador de la categoría de evento a eliminar.

    ---
    tags:
      - Categorías de Evento
    responses:
      200:
        description: Categoría de evento eliminada correctamente
      404:
        description: Categoría de evento no encontrada
    """
    result = db.session.execute(db.text("DELETE FROM evento_categorias WHERE id = :id"), {'id': id})
    if getattr(result, 'rowcount', 0) == 0:
        return jsonify({'error': 'Categoría de evento no encontrada'}), 404
    db.session.commit()
    return jsonify({'mensaje': 'Categoría de evento eliminada correctamente'})
