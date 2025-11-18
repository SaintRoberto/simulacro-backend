from flask import Blueprint, request, jsonify
from models import db
from datetime import datetime, timezone


evento_subtipos_bp = Blueprint('evento_subtipos', __name__)


@evento_subtipos_bp.route('/api/evento_subtipos', methods=['GET'])
def get_evento_subtipos():
    """
    Listar todos los subtipos de eventos registrados.

    ---
    tags:
      - Subtipos de Evento
    parameters:
      - name: evento_tipo_id
        in: query
        description: Filtrar por ID de tipo de evento
        required: false
        type: integer
    responses:
      200:
        description: Lista de subtipos de eventos obtenida correctamente
        schema:
          type: array
          items:
            type: object
            properties:
              id: {type: integer}
              evento_tipo_id: {type: integer}
              evento_tipo_nombre: {type: string}
              nombre: {type: string}
              descripcion: {type: string}
              abreviatura: {type: string}
              activo: {type: boolean}
              creador: {type: string}
              creacion: {type: string, format: date-time}
              modificador: {type: string}
              modificacion: {type: string, format: date-time}
              identificador: {type: string}
    """
    evento_tipo_id = request.args.get('evento_tipo_id', type=int)

    query = db.text("""
        SELECT es.*, 
               et.nombre as evento_tipo_nombre
        FROM evento_subtipos es
        LEFT JOIN evento_tipos et ON es.evento_tipo_id = et.id
        WHERE (:evento_tipo_id IS NULL OR es.evento_tipo_id = :evento_tipo_id)
        ORDER BY es.id
    """)

    result = db.session.execute(query, {'evento_tipo_id': evento_tipo_id})
    subtipos = []
    for row in result:
        subtipos.append({
            'id': row.id,
            'evento_tipo_id': row.evento_tipo_id,
            'evento_tipo_nombre': getattr(row, 'evento_tipo_nombre', None),
            'nombre': row.nombre,
            'descripcion': row.descripcion,
            'abreviatura': row.abreviatura,
            'activo': row.activo,
            'creador': row.creador,
            'creacion': row.creacion.isoformat() if row.creacion else None,
            'modificador': row.modificador,
            'modificacion': row.modificacion.isoformat() if row.modificacion else None,
            'identificador': row.identificador
        })
    return jsonify(subtipos)


@evento_subtipos_bp.route('/api/evento_subtipos/tipo/<int:evento_tipo_id>', methods=['GET'])
def get_evento_subtipos_by_tipo(evento_tipo_id):
    """
    Listar subtipos de eventos filtrados por un tipo de evento específico.

    ---
    tags:
      - Subtipos de Evento
    parameters:
      - name: evento_tipo_id
        in: path
        description: ID del tipo de evento por el que se filtrarán los subtipos
        required: true
        type: integer
    responses:
      200:
        description: Lista de subtipos de eventos filtrada correctamente
        schema:
          type: array
          items:
            type: object
            properties:
              id: {type: integer}
              evento_tipo_id: {type: integer}
              evento_tipo_nombre: {type: string}
              nombre: {type: string}
              descripcion: {type: string}
              abreviatura: {type: string}
              activo: {type: boolean}
              creador: {type: string}
              creacion: {type: string, format: date-time}
              modificador: {type: string}
              modificacion: {type: string, format: date-time}
              identificador: {type: string}
    """
    query = db.text("""
        SELECT es.*, 
               et.nombre as evento_tipo_nombre
        FROM evento_subtipos es
        LEFT JOIN evento_tipos et ON es.evento_tipo_id = et.id
        WHERE es.evento_tipo_id = :evento_tipo_id
        ORDER BY es.id
    """)

    result = db.session.execute(query, {'evento_tipo_id': evento_tipo_id})
    subtipos = []
    for row in result:
        subtipos.append({
            'id': row.id,
            'evento_tipo_id': row.evento_tipo_id,
            'evento_tipo_nombre': getattr(row, 'evento_tipo_nombre', None),
            'nombre': row.nombre,
            'descripcion': row.descripcion,
            'abreviatura': row.abreviatura,
            'activo': row.activo,
            'creador': row.creador,
            'creacion': row.creacion.isoformat() if row.creacion else None,
            'modificador': row.modificador,
            'modificacion': row.modificacion.isoformat() if row.modificacion else None,
            'identificador': row.identificador
        })

    return jsonify(subtipos)


@evento_subtipos_bp.route('/api/evento_subtipos/<int:id>', methods=['GET'])
def get_evento_subtipo(id):
    """
    Obtener información detallada de un subtipo de evento específico.

    ---
    tags:
      - Subtipos de Evento
    parameters:
      - name: id
        in: path
        description: ID del subtipo de evento
        required: true
        type: integer
    responses:
      200:
        description: Subtipo de evento encontrado y devuelto correctamente
        schema:
          type: object
          properties:
            id: {type: integer}
            evento_tipo_id: {type: integer}
            evento_tipo_nombre: {type: string}
            nombre: {type: string}
            descripcion: {type: string}
            abreviatura: {type: string}
            activo: {type: boolean}
            creador: {type: string}
            creacion: {type: string, format: date-time}
            modificador: {type: string}
            modificacion: {type: string, format: date-time}
            identificador: {type: string}
      404:
        description: No se encontró el subtipo de evento solicitado
    """
    query = db.text("""
        SELECT es.*, 
               et.nombre as evento_tipo_nombre
        FROM evento_subtipos es
        LEFT JOIN evento_tipos et ON es.evento_tipo_id = et.id
        WHERE es.id = :id
    """)

    result = db.session.execute(query, {'id': id}).fetchone()
    if result is None:
        return jsonify({'error': 'Subtipo de evento no encontrado'}), 404

    return jsonify({
        'id': result.id,
        'evento_tipo_id': result.evento_tipo_id,
        'evento_tipo_nombre': getattr(result, 'evento_tipo_nombre', None),
        'nombre': result.nombre,
        'descripcion': result.descripcion,
        'abreviatura': result.abreviatura,
        'activo': result.activo,
        'creador': result.creador,
        'creacion': result.creacion.isoformat() if result.creacion else None,
        'modificador': result.modificador,
        'modificacion': result.modificacion.isoformat() if result.modificacion else None,
        'identificador': result.identificador
    })


@evento_subtipos_bp.route('/api/evento_subtipos', methods=['POST'])
def create_evento_subtipo():
    """
    Crear un nuevo subtipo de evento.

    Inserta un nuevo registro en la tabla `evento_subtipos`.

    ---
    tags:
      - Subtipos de Evento
    consumes:
      - application/json
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          required: [evento_tipo_id, nombre]
          properties:
            evento_tipo_id: {type: integer}
            nombre: {type: string}
            descripcion: {type: string}
            abreviatura: {type: string}
            activo: {type: boolean}
            creador: {type: string}
            modificador: {type: string}
            identificador: {type: string}
    responses:
      201:
        description: Subtipo de evento creado correctamente
        schema:
          $ref: '#/definitions/EventoSubtipo'
      400:
        description: Error en los datos enviados
      500:
        description: Error al crear el subtipo de evento
    """
    data = request.get_json()

    # Validar campos requeridos
    required_fields = ['evento_tipo_id', 'nombre']
    missing_fields = [field for field in required_fields if field not in data]
    if missing_fields:
        return jsonify({
            'error': 'Faltan campos requeridos',
            'campos_faltantes': missing_fields
        }), 400

    now = datetime.now(timezone.utc)
    query = db.text("""
        INSERT INTO evento_subtipos (
            evento_tipo_id, nombre, descripcion, abreviatura,
            activo, creador, creacion, modificador, modificacion, identificador
        )
        VALUES (
            :evento_tipo_id, :nombre, :descripcion, :abreviatura,
            :activo, :creador, :creacion, :modificador, :modificacion, :identificador
        )
        RETURNING id
    """)

    try:
        result = db.session.execute(query, {
            'evento_tipo_id': data['evento_tipo_id'],
            'nombre': data['nombre'],
            'descripcion': data.get('descripcion'),
            'abreviatura': data.get('abreviatura'),
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
            return jsonify({'error': 'Fallo la creación del subtipo de evento'}), 500

        subtipo_id = row[0]
        db.session.commit()

        # Obtener el subtipo de evento recién creado con el nombre del tipo
        subtipo = db.session.execute(db.text("""
            SELECT es.*, 
                   et.nombre as evento_tipo_nombre
            FROM evento_subtipos es
            LEFT JOIN evento_tipos et ON es.evento_tipo_id = et.id
            WHERE es.id = :id
        """), {'id': subtipo_id}).fetchone()

        if subtipo is None:
            return jsonify({'error': 'No se pudo recuperar el subtipo de evento recién creado'}), 500

        return jsonify({
            'id': subtipo.id,
            'evento_tipo_id': subtipo.evento_tipo_id,
            'evento_tipo_nombre': getattr(subtipo, 'evento_tipo_nombre', None),
            'nombre': subtipo.nombre,
            'descripcion': subtipo.descripcion,
            'abreviatura': subtipo.abreviatura,
            'activo': subtipo.activo,
            'creador': subtipo.creador,
            'creacion': subtipo.creacion.isoformat() if subtipo.creacion else None,
            'modificador': subtipo.modificador,
            'modificacion': subtipo.modificacion.isoformat() if subtipo.modificacion else None,
            'identificador': subtipo.identificador
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({
            'error': 'Error al crear el subtipo de evento',
            'detalle': str(e)
        }), 500


@evento_subtipos_bp.route('/api/evento_subtipos/<int:id>', methods=['PUT'])
def update_evento_subtipo(id):
    """
    Actualizar un subtipo de evento existente.

    ---
    tags:
      - Subtipos de Evento
    parameters:
      - name: id
        in: path
        description: ID del subtipo de evento a actualizar
        required: true
        type: integer
      - in: body
        name: body
        required: true
        schema:
          type: object
          properties:
            evento_tipo_id: {type: integer}
            nombre: {type: string}
            descripcion: {type: string}
            abreviatura: {type: string}
            activo: {type: boolean}
            modificador: {type: string}
            identificador: {type: string}
    responses:
      200:
        description: Subtipo de evento actualizado correctamente
        schema:
          $ref: '#/definitions/EventoSubtipo'
      400:
        description: Error en los datos enviados
      404:
        description: Subtipo de evento no encontrado
      500:
        description: Error al actualizar el subtipo de evento
    """
    data = request.get_json()
    if not data:
        return jsonify({'error': 'No se proporcionaron datos para actualizar'}), 400

    now = datetime.now(timezone.utc)
    update_fields = []
    params = {
        'id': id,
        'modificador': data.get('modificador', 'Sistema'),
        'modificacion': now
    }

    # Campos actualizables
    fields = ['evento_tipo_id', 'nombre', 'descripcion', 'abreviatura', 'activo', 'identificador']

    for field in fields:
        if field in data:
            update_fields.append(f"{field} = :{field}")
            params[field] = data[field]

    if not update_fields:
        return jsonify({'error': 'No se proporcionaron campos válidos para actualizar'}), 400

    update_fields.append('modificador = :modificador')
    update_fields.append('modificacion = :modificacion')

    try:
        query = db.text(f"""
            UPDATE evento_subtipos
            SET {', '.join(update_fields)}
            WHERE id = :id
            RETURNING id
        """)

        result = db.session.execute(query, params)
        if getattr(result, 'rowcount', 0) == 0:
            return jsonify({'error': 'Subtipo de evento no encontrado'}), 404

        db.session.commit()

        # Obtener el subtipo de evento actualizado con el nombre del tipo
        subtipo = db.session.execute(db.text("""
            SELECT es.*, 
                   et.nombre as evento_tipo_nombre
            FROM evento_subtipos es
            LEFT JOIN evento_tipos et ON es.evento_tipo_id = et.id
            WHERE es.id = :id
        """), {'id': id}).fetchone()

        if subtipo is None:
            return jsonify({'error': 'No se pudo recuperar el subtipo de evento actualizado'}), 500

        return jsonify({
            'id': subtipo.id,
            'evento_tipo_id': subtipo.evento_tipo_id,
            'evento_tipo_nombre': getattr(subtipo, 'evento_tipo_nombre', None),
            'nombre': subtipo.nombre,
            'descripcion': subtipo.descripcion,
            'abreviatura': subtipo.abreviatura,
            'activo': subtipo.activo,
            'creador': subtipo.creador,
            'creacion': subtipo.creacion.isoformat() if subtipo.creacion else None,
            'modificador': subtipo.modificador,
            'modificacion': subtipo.modificacion.isoformat() if subtipo.modificacion else None,
            'identificador': subtipo.identificador
        })

    except Exception as e:
        db.session.rollback()
        return jsonify({
            'error': 'Error al actualizar el subtipo de evento',
            'detalle': str(e)
        }), 500


@evento_subtipos_bp.route('/api/evento_subtipos/<int:id>', methods=['DELETE'])
def delete_evento_subtipo(id):
    """
    Eliminar un subtipo de evento.

    ---
    tags:
      - Subtipos de Evento
    parameters:
      - name: id
        in: path
        description: ID del subtipo de evento a eliminar
        required: true
        type: integer
    responses:
      200:
        description: Subtipo de evento eliminado correctamente
        schema:
          type: object
          properties:
            mensaje: {type: string}
            id: {type: integer}
      404:
        description: Subtipo de evento no encontrado
      500:
        description: Error al eliminar el subtipo de evento
    """
    try:
        # Primero verificamos si existe
        subtipo = db.session.execute(
            db.text("SELECT id FROM evento_subtipos WHERE id = :id"),
            {'id': id}
        ).fetchone()

        if not subtipo:
            return jsonify({'error': 'Subtipo de evento no encontrado'}), 404

        # Verificar si hay eventos que dependen de este subtipo
        eventos_count = db.session.execute(
            db.text("SELECT COUNT(*) FROM eventos WHERE evento_subtipo_id = :id"),
            {'id': id}
        ).scalar()

        if eventos_count > 0:
            return jsonify({
                'error': 'No se puede eliminar el subtipo de evento porque tiene eventos asociados',
                'eventos_asociados': eventos_count
            }), 400

        # Si no hay dependencias, procedemos a eliminar
        result = db.session.execute(
            db.text("DELETE FROM evento_subtipos WHERE id = :id"),
            {'id': id}
        )

        if getattr(result, 'rowcount', 0) == 0:
            return jsonify({'error': 'No se pudo eliminar el subtipo de evento'}), 500

        db.session.commit()
        return jsonify({
            'mensaje': 'Subtipo de evento eliminado correctamente',
            'id': id
        })

    except Exception as e:
        db.session.rollback()
        return jsonify({
            'error': 'Error al eliminar el subtipo de evento',
            'detalle': str(e)
        }), 500
