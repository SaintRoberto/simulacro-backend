from flask import Blueprint, request, jsonify
from datetime import datetime, timezone
from models import db

evento_atencion_estados_bp = Blueprint('evento_atencion_estados', __name__)

@evento_atencion_estados_bp.route('/api/evento_atencion_estados', methods=['GET'])
def get_evento_atencion_estados():
    """
    Listar todos los estados de atención de eventos registrados.
    
    Devuelve una lista de todos los estados de atención de eventos existentes en la base de datos,
    ordenados por ID. Incluye información de creación y modificación.
    
    ---
    tags:
      - Estados de Atención de Eventos
    responses:
      200:
        description: Lista de estados de atención de eventos
    """
    query = db.text("""
        SELECT id, nombre, descripcion, activo, creador, creacion, modificador, modificacion 
        FROM evento_atencion_estados 
        ORDER BY id
    """)
    result = db.session.execute(query)
    return jsonify([dict(row._mapping) for row in result])

@evento_atencion_estados_bp.route('/api/evento_atencion_estados/<int:id>', methods=['GET'])
def get_evento_atencion_estado(id):
    """
    Obtener un estado de atención de evento específico por ID.

    Parámetros:
      id (int): ID del estado de atención de evento

    ---
    tags:
      - Estados de Atención de Eventos
    parameters:
      - name: id
        in: path
        description: Identificador del estado de atención de evento
        required: true
        type: integer
    responses:
      200:
        description: Estado de atención de evento encontrado
      404:
        description: Estado de atención de evento no encontrado
    """
    query = db.text("""
        SELECT id, nombre, descripcion, activo, creador, creacion, modificador, modificacion
        FROM evento_atencion_estados 
        WHERE id = :id
    """)
    estado = db.session.execute(query, {'id': id}).fetchone()
    if not estado:
        return jsonify({'error': 'Estado de atención de evento no encontrado'}), 404
    return jsonify(dict(estado._mapping))

@evento_atencion_estados_bp.route('/api/evento_atencion_estados', methods=['POST'])
def create_evento_atencion_estado():
    """
    Crear un nuevo estado de atención de evento.
    
    Campos obligatorios:
    - nombre: Nombre del estado (máx. 100 caracteres)
    
    Campos opcionales:
    - descripcion: Descripción detallada del estado (máx. 500 caracteres)
    - activo: Booleano que indica si el estado está activo (por defecto: true)
    - creador: Usuario que crea el registro (por defecto: 'Sistema')
    
    ---
    tags:
      - Estados de Atención de Eventos
    """
    data = request.get_json()
    
    if not data or 'nombre' not in data:
        return jsonify({'error': 'El campo nombre es obligatorio'}), 400
    
    now = datetime.now(timezone.utc)
    query = db.text("""
        INSERT INTO evento_atencion_estados 
        (nombre, descripcion, activo, creador, creacion, modificador, modificacion)
        VALUES (:nombre, :descripcion, :activo, :creador, :creacion, :modificador, :modificacion)
        RETURNING id
    """)
    
    try:
        result = db.session.execute(query, {
            'nombre': data['nombre'],
            'descripcion': data.get('descripcion'),
            'activo': data.get('activo', True),
            'creador': data.get('creador', 'Sistema'),
            'creacion': now,
            'modificador': data.get('creador', 'Sistema'),
            'modificacion': now
        })
        db.session.commit()
        
        estado_id = result.fetchone()[0]
        return jsonify({'id': estado_id}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400

@evento_atencion_estados_bp.route('/api/evento_atencion_estados/<int:id>', methods=['PUT'])
def update_evento_atencion_estado(id):
    """
    Actualizar un estado de atención de evento existente.
    
    Campos actualizables:
    - nombre: Nuevo nombre del estado
    - descripcion: Nueva descripción
    - activo: Nuevo estado activo/inactivo
    - modificador: Usuario que realiza la modificación
    
    ---
    tags:
      - Estados de Atención de Eventos
    parameters:
      - name: id
        in: path
        description: ID del estado de atención de evento a actualizar
        required: true
        type: integer
    """
    data = request.get_json()
    if not data:
        return jsonify({'error': 'No se proporcionaron datos para actualizar'}), 400
    
    # Verificar que el estado existe
    check_query = db.text("SELECT 1 FROM evento_atencion_estados WHERE id = :id")
    if not db.session.execute(check_query, {'id': id}).fetchone():
        return jsonify({'error': 'Estado de atención de evento no encontrado'}), 404
    
    # Construir la consulta de actualización dinámicamente
    update_fields = []
    params = {'id': id}
    
    if 'nombre' in data:
        update_fields.append("nombre = :nombre")
        params['nombre'] = data['nombre']
    
    if 'descripcion' in data:
        update_fields.append("descripcion = :descripcion")
        params['descripcion'] = data['descripcion']
    
    if 'activo' in data:
        update_fields.append("activo = :activo")
        params['activo'] = data['activo']
    
    # Siempre actualizar el modificador y la fecha de modificación
    modificador = data.get('modificador', 'Sistema')
    update_fields.append("modificador = :modificador")
    params['modificador'] = modificador
    
    now = datetime.now(timezone.utc)
    update_fields.append("modificacion = :modificacion")
    params['modificacion'] = now
    
    if not update_fields:
        return jsonify({'error': 'No se proporcionaron campos para actualizar'}), 400
    
    query = db.text(f"""
        UPDATE evento_atencion_estados
        SET {', '.join(update_fields)}
        WHERE id = :id
    """)
    
    try:
        db.session.execute(query, params)
        db.session.commit()
        return jsonify({'message': 'Estado de atención de evento actualizado correctamente'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400

@evento_atencion_estados_bp.route('/api/evento_atencion_estados/<int:id>', methods=['DELETE'])
def delete_evento_atencion_estado(id):
    """
    Eliminar un estado de atención de evento existente.
    
    Marca el registro como inactivo en lugar de eliminarlo físicamente (soft delete).
    
    ---
    tags:
      - Estados de Atención de Eventos
    parameters:
      - name: id
        in: path
        description: ID del estado de atención de evento a eliminar
        required: true
        type: integer
      - name: modificador
        in: query
        description: Usuario que realiza la eliminación
        required: false
        type: string
        default: 'Sistema'
    """
    # Verificar que el estado existe
    check_query = db.text("SELECT 1 FROM evento_atencion_estados WHERE id = :id")
    if not db.session.execute(check_query, {'id': id}).fetchone():
        return jsonify({'error': 'Estado de atención de evento no encontrado'}), 404
    
    # Realizar soft delete (marcar como inactivo)
    modificador = request.args.get('modificador', 'Sistema')
    now = datetime.now(timezone.utc)
    
    query = db.text("""
        UPDATE evento_atencion_estados
        SET activo = false,
            modificador = :modificador,
            modificacion = :modificacion
        WHERE id = :id
    """)
    
    try:
        db.session.execute(query, {
            'id': id,
            'modificador': modificador,
            'modificacion': now
        })
        db.session.commit()
        return jsonify({'message': 'Estado de atención de evento eliminado correctamente'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400
