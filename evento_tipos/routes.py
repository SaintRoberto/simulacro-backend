from flask import Blueprint, request, jsonify
from models import db
from datetime import datetime, timezone

evento_tipos_bp = Blueprint('evento_tipos', __name__)

@evento_tipos_bp.route('/api/evento_tipos', methods=['GET'])
def get_evento_tipos():
    """
    Listar todos los tipos de eventos registrados.

    ---
    tags:
      - Tipos de Evento
    responses:
      200:
        description: Lista de tipos de eventos obtenida correctamente
        schema:
          type: array
          items:
            type: object
            properties:
              id: {type: integer}
              evento_fenomeno_id: {type: integer}
              evento_clase_id: {type: integer}
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
        SELECT et.*, 
               ef.nombre as evento_fenomeno_nombre,
               ec.nombre as evento_clase_nombre
        FROM evento_tipos et
        LEFT JOIN evento_fenomenos ef ON et.evento_fenomeno_id = ef.id
        LEFT JOIN evento_clases ec ON et.evento_clase_id = ec.id
        ORDER BY et.id
    """)
    result = db.session.execute(query)
    tipos = []
    for row in result:
        tipos.append({
            'id': row.id,
            'evento_fenomeno_id': row.evento_fenomeno_id,
            'evento_fenomeno_nombre': getattr(row, 'evento_fenomeno_nombre', None),
            'evento_clase_id': row.evento_clase_id,
            'evento_clase_nombre': getattr(row, 'evento_clase_nombre', None),
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
    return jsonify(tipos)


@evento_tipos_bp.route('/api/evento_tipos/<int:id>', methods=['GET'])
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
        schema:
          type: object
          properties:
            id: {type: integer}
            evento_fenomeno_id: {type: integer}
            evento_fenomeno_nombre: {type: string}
            evento_clase_id: {type: integer}
            evento_clase_nombre: {type: string}
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
        description: No se encontró el tipo de evento solicitado
    """
    query = db.text("""
        SELECT et.*, 
               ef.nombre as evento_fenomeno_nombre,
               ec.nombre as evento_clase_nombre
        FROM evento_tipos et
        LEFT JOIN evento_fenomenos ef ON et.evento_fenomeno_id = ef.id
        LEFT JOIN evento_clases ec ON et.evento_clase_id = ec.id
        WHERE et.id = :id
    """)
    result = db.session.execute(query, {'id': id}).fetchone()
    if result is None:
        return jsonify({'error': 'Tipo de evento no encontrado'}), 404
    return jsonify({
        'id': result.id,
        'evento_fenomeno_id': result.evento_fenomeno_id,
        'evento_fenomeno_nombre': getattr(result, 'evento_fenomeno_nombre', None),
        'evento_clase_id': result.evento_clase_id,
        'evento_clase_nombre': getattr(result, 'evento_clase_nombre', None),
        'nombre': result.nombre,
        'descripcion': result.descripcion,
        'abreviatura': result.abreviatura,
        'activo': result.activo,
        'creador': result.creador,
        'creacion': result.creacion.isoformat() if getattr(result, 'creacion', None) else None,
        'modificador': result.modificador,
        'modificacion': result.modificacion.isoformat() if getattr(result, 'modificacion', None) else None,
        'identificador': getattr(result, 'identificador', None)
    })


@evento_tipos_bp.route('/api/evento_tipos', methods=['POST'])
def create_evento_tipo():
    """
    Crear un nuevo tipo de evento.

    Inserta un nuevo registro en la tabla `evento_tipos`.
    
    ---
    tags:
      - Tipos de Evento
    consumes:
      - application/json
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          required: [evento_fenomeno_id, evento_clase_id, nombre]
          properties:
            evento_fenomeno_id: {type: integer}
            evento_clase_id: {type: integer}
            nombre: {type: string}
            descripcion: {type: string}
            abreviatura: {type: string}
            activo: {type: boolean}
            creador: {type: string}
            modificador: {type: string}
            identificador: {type: string}
    responses:
      201:
        description: Tipo de evento creado correctamente
        schema:
          $ref: '#/definitions/EventoTipo'
      400:
        description: Error en los datos enviados
      500:
        description: Error al crear el tipo de evento
    """
    data = request.get_json()
    
    # Validar campos requeridos
    required_fields = ['evento_fenomeno_id', 'evento_clase_id', 'nombre']
    missing_fields = [field for field in required_fields if field not in data]
    if missing_fields:
        return jsonify({
            'error': 'Faltan campos requeridos',
            'campos_faltantes': missing_fields
        }), 400
    
    now = datetime.now(timezone.utc)
    query = db.text("""
        INSERT INTO evento_tipos (
            evento_fenomeno_id, evento_clase_id, nombre, descripcion, abreviatura,
            activo, creador, creacion, modificador, modificacion, identificador
        )
        VALUES (
            :evento_fenomeno_id, :evento_clase_id, :nombre, :descripcion, :abreviatura,
            :activo, :creador, :creacion, :modificador, :modificacion, :identificador
        )
        RETURNING id
    """)
    
    try:
        result = db.session.execute(query, {
            'evento_fenomeno_id': data['evento_fenomeno_id'],
            'evento_clase_id': data['evento_clase_id'],
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
            return jsonify({'error': 'Fallo la creación del tipo de evento'}), 500
            
        tipo_id = row[0]
        db.session.commit()
        
        # Obtener el tipo de evento recién creado con los nombres de las relaciones
        tipo = db.session.execute(db.text("""
            SELECT et.*, 
                   ef.nombre as evento_fenomeno_nombre,
                   ec.nombre as evento_clase_nombre
            FROM evento_tipos et
            LEFT JOIN evento_fenomenos ef ON et.evento_fenomeno_id = ef.id
            LEFT JOIN evento_clases ec ON et.evento_clase_id = ec.id
            WHERE et.id = :id
        """), {'id': tipo_id}).fetchone()
        
        if tipo is None:
            return jsonify({'error': 'No se pudo recuperar el tipo de evento recién creado'}), 500
            
        return jsonify({
            'id': tipo.id,
            'evento_fenomeno_id': tipo.evento_fenomeno_id,
            'evento_fenomeno_nombre': getattr(tipo, 'evento_fenomeno_nombre', None),
            'evento_clase_id': tipo.evento_clase_id,
            'evento_clase_nombre': getattr(tipo, 'evento_clase_nombre', None),
            'nombre': tipo.nombre,
            'descripcion': tipo.descripcion,
            'abreviatura': tipo.abreviatura,
            'activo': tipo.activo,
            'creador': tipo.creador,
            'creacion': tipo.creacion.isoformat() if tipo.creacion else None,
            'modificador': tipo.modificador,
            'modificacion': tipo.modificacion.isoformat() if tipo.modificacion else None,
            'identificador': tipo.identificador
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'error': 'Error al crear el tipo de evento',
            'detalle': str(e)
        }), 500


@evento_tipos_bp.route('/api/evento_tipos/<int:id>', methods=['PUT'])
def update_evento_tipo(id):
    """
    Actualizar un tipo de evento existente.
    
    ---
    tags:
      - Tipos de Evento
    parameters:
      - name: id
        in: path
        description: ID del tipo de evento a actualizar
        required: true
        type: integer
      - in: body
        name: body
        required: true
        schema:
          type: object
          properties:
            evento_fenomeno_id: {type: integer}
            evento_clase_id: {type: integer}
            nombre: {type: string}
            descripcion: {type: string}
            abreviatura: {type: string}
            activo: {type: boolean}
            modificador: {type: string}
            identificador: {type: string}
    responses:
      200:
        description: Tipo de evento actualizado correctamente
        schema:
          $ref: '#/definitions/EventoTipo'
      400:
        description: Error en los datos enviados
      404:
        description: Tipo de evento no encontrado
      500:
        description: Error al actualizar el tipo de evento
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
    fields = [
        'evento_fenomeno_id', 'evento_clase_id', 'nombre', 'descripcion',
        'abreviatura', 'activo', 'identificador'
    ]
    
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
            UPDATE evento_tipos
            SET {', '.join(update_fields)}
            WHERE id = :id
            RETURNING id
        """)
        
        result = db.session.execute(query, params)
        if getattr(result, 'rowcount', 0) == 0:
            return jsonify({'error': 'Tipo de evento no encontrado'}), 404
            
        db.session.commit()
        
        # Obtener el tipo de evento actualizado con los nombres de las relaciones
        tipo = db.session.execute(db.text("""
            SELECT et.*, 
                   ef.nombre as evento_fenomeno_nombre,
                   ec.nombre as evento_clase_nombre
            FROM evento_tipos et
            LEFT JOIN evento_fenomenos ef ON et.evento_fenomeno_id = ef.id
            LEFT JOIN evento_clases ec ON et.evento_clase_id = ec.id
            WHERE et.id = :id
        """), {'id': id}).fetchone()
        
        if tipo is None:
            return jsonify({'error': 'No se pudo recuperar el tipo de evento actualizado'}), 500
            
        return jsonify({
            'id': tipo.id,
            'evento_fenomeno_id': tipo.evento_fenomeno_id,
            'evento_fenomeno_nombre': getattr(tipo, 'evento_fenomeno_nombre', None),
            'evento_clase_id': tipo.evento_clase_id,
            'evento_clase_nombre': getattr(tipo, 'evento_clase_nombre', None),
            'nombre': tipo.nombre,
            'descripcion': tipo.descripcion,
            'abreviatura': tipo.abreviatura,
            'activo': tipo.activo,
            'creador': tipo.creador,
            'creacion': tipo.creacion.isoformat() if tipo.creacion else None,
            'modificador': tipo.modificador,
            'modificacion': tipo.modificacion.isoformat() if tipo.modificacion else None,
            'identificador': tipo.identificador
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'error': 'Error al actualizar el tipo de evento',
            'detalle': str(e)
        }), 500


@evento_tipos_bp.route('/api/evento_tipos/<int:id>', methods=['DELETE'])
def delete_evento_tipo(id):
    """
    Eliminar un tipo de evento.
    
    ---
    tags:
      - Tipos de Evento
    parameters:
      - name: id
        in: path
        description: ID del tipo de evento a eliminar
        required: true
        type: integer
    responses:
      200:
        description: Tipo de evento eliminado correctamente
        schema:
          type: object
          properties:
            mensaje: {type: string}
            id: {type: integer}
      404:
        description: Tipo de evento no encontrado
      500:
        description: Error al eliminar el tipo de evento
    """
    try:
        # Primero verificamos si existe
        tipo = db.session.execute(
            db.text("SELECT id FROM evento_tipos WHERE id = :id"),
            {'id': id}
        ).fetchone()
        
        if not tipo:
            return jsonify({'error': 'Tipo de evento no encontrado'}), 404
        
        # Verificar si hay eventos que dependen de este tipo
        eventos_count = db.session.execute(
            db.text("SELECT COUNT(*) FROM eventos WHERE evento_tipo_id = :id"),
            {'id': id}
        ).scalar()
        
        if eventos_count > 0:
            return jsonify({
                'error': 'No se puede eliminar el tipo de evento porque tiene eventos asociados',
                'eventos_asociados': eventos_count
            }), 400
        
        # Si no hay dependencias, procedemos a eliminar
        result = db.session.execute(
            db.text("DELETE FROM evento_tipos WHERE id = :id"),
            {'id': id}
        )
        
        if getattr(result, 'rowcount', 0) == 0:
            return jsonify({'error': 'No se pudo eliminar el tipo de evento'}), 500
            
        db.session.commit()
        return jsonify({
            'mensaje': 'Tipo de evento eliminado correctamente',
            'id': id
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'error': 'Error al eliminar el tipo de evento',
            'detalle': str(e)
        }), 500
