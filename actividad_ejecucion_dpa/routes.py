from flask import request, jsonify
from models import db
from datetime import datetime, timezone
from . import actividad_ejecucion_dpa_bp

@actividad_ejecucion_dpa_bp.route('/api/actividad_ejecucion_dpa', methods=['GET'])
def get_actividades_ejecucion_dpa():
    """Listar todas las actividades de ejecución DPA
    ---
    tags:
      - Actividad Ejecución DPA
    responses:
      200:
        description: Lista de actividades de ejecución DPA
        schema:
          type: array
          items:
            type: object
            properties:
              id: {type: integer}
              actividad_ejecucion_id: {type: integer}
              provincia_id: {type: integer}
              canton_id: {type: integer}
              parroquia_id: {type: integer}
              activo: {type: boolean}
              creador: {type: string}
              creacion: {type: string}
              modificador: {type: string}
              modificacion: {type: string}
    """
    result = db.session.execute(db.text("SELECT * FROM actividad_ejecucion_dpa WHERE activo = true"))
    items = [dict(row._mapping) for row in result]
    for item in items:
        for k, v in item.items():
            if isinstance(v, datetime):
                item[k] = v.isoformat()
    return jsonify(items)

@actividad_ejecucion_dpa_bp.route('/api/actividad_ejecucion_dpa/actividad_ejecucion/<int:actividad_ejecucion_id>', methods=['GET'])
def get_actividades_ejecucion_dpa_by_actividad_ejecucion(actividad_ejecucion_id):
    """Obtener actividades DPA por ID de actividad de ejecución
    ---
    tags:
      - Actividad Ejecución DPA
    parameters:
      - name: actividad_ejecucion_id
        in: path
        type: integer
        required: true
    responses:
      200:
        description: Lista de actividades DPA para la actividad de ejecución
        schema:
          type: array
          items:
            type: object
            properties:
              id: {type: integer}
              actividad_ejecucion_id: {type: integer}
              provincia_id: {type: integer}
              provincia_nombre: {type: string}
              canton_id: {type: integer}
              canton_nombre: {type: string}
              parroquia_id: {type: integer}
              parroquia_nombre: {type: string}
    """
    query = db.text("""
        SELECT aed.*, 
               p.nombre as provincia_nombre,
               c.nombre as canton_nombre,
               pa.nombre as parroquia_nombre
        FROM actividad_ejecucion_dpa aed
        LEFT JOIN provincias p ON aed.provincia_id = p.id
        LEFT JOIN cantones c ON aed.canton_id = c.id
        LEFT JOIN parroquias pa ON aed.parroquia_id = pa.id
        WHERE aed.actividad_ejecucion_id = :actividad_ejecucion_id
        AND aed.activo = true
    """)
    result = db.session.execute(query, {'actividad_ejecucion_id': actividad_ejecucion_id})
    items = [dict(row._mapping) for row in result]
    for item in items:
        for k, v in item.items():
            if isinstance(v, datetime):
                item[k] = v.isoformat()
    return jsonify(items)

@actividad_ejecucion_dpa_bp.route('/api/actividad_ejecucion_dpa/<int:id>', methods=['GET'])
def get_actividades_ejecucion_dpa_by_id(id):
    """Obtener una actividad de ejecución DPA por su ID
    ---
    tags:
      - Actividad Ejecución DPA
    parameters:
      - name: id
        in: path
        type: integer
        required: true
        description: ID de la actividad de ejecución DPA
    responses:
      200:
        description: Detalle de la actividad de ejecución DPA
        schema:
          type: object
          properties:
            id: {type: integer}
            actividad_ejecucion_id: {type: integer}
            provincia_id: {type: integer}
            provincia_nombre: {type: string}
            canton_id: {type: integer}
            canton_nombre: {type: string}
            parroquia_id: {type: integer}
            parroquia_nombre: {type: string}
            activo: {type: boolean}
            creador: {type: string}
            creacion: {type: string}
            modificador: {type: string}
            modificacion: {type: string}
      404:
        description: No se encontró la actividad de ejecución DPA
    """
    query = db.text("""
        SELECT aed.*, 
               p.nombre as provincia_nombre,
               c.nombre as canton_nombre,
               pa.nombre as parroquia_nombre
        FROM actividad_ejecucion_dpa aed
        LEFT JOIN provincias p ON aed.provincia_id = p.id
        LEFT JOIN cantones c ON aed.canton_id = c.id
        LEFT JOIN parroquias pa ON aed.parroquia_id = pa.id
        WHERE aed.id = :id
    """)
    
    result = db.session.execute(query, {'id': id}).fetchone()
    
    if not result:
        return jsonify({'error': 'Actividad de ejecución DPA no encontrada'}), 404
    
    # Convertir el resultado a diccionario
    item = dict(result._mapping)
    
    # Formatear fechas
    for k, v in item.items():
        if isinstance(v, datetime):
            item[k] = v.isoformat()
    
    return jsonify(item)

@actividad_ejecucion_dpa_bp.route('/api/actividad_ejecucion_dpa', methods=['POST'])
def create_actividad_ejecucion_dpa():
    """Crear una nueva actividad de ejecución DPA
    ---
    tags:
      - Actividad Ejecución DPA
    consumes:
      - application/json
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          required: [actividad_ejecucion_id, provincia_id, canton_id, parroquia_id]
          properties:
            actividad_ejecucion_id: {type: integer}
            provincia_id: {type: integer}
            canton_id: {type: integer}
            parroquia_id: {type: integer}
            creador: {type: string}
    responses:
      201:
        description: Actividad de ejecución DPA creada
      400:
        description: Datos de entrada inválidos
    """
    data = request.get_json() or {}
    if not data:
        return jsonify({'error': 'No se proporcionaron datos'}), 400

    required = ['actividad_ejecucion_id', 'provincia_id', 'canton_id', 'parroquia_id']
    missing = [field for field in required if field not in data]
    if missing:
        return jsonify({'error': 'Faltan campos requeridos', 'campos_faltantes': missing}), 400

    now = datetime.now(timezone.utc)
    
    query = db.text("""
        INSERT INTO actividad_ejecucion_dpa (
            actividad_ejecucion_id, provincia_id, canton_id, parroquia_id,
            activo, creador, creacion, modificador, modificacion
        ) VALUES (
            :actividad_ejecucion_id, :provincia_id, :canton_id, :parroquia_id,
            true, :creador, :creacion, :modificador, :modificacion
        ) RETURNING id
    """)
    
    params = {
        'actividad_ejecucion_id': data['actividad_ejecucion_id'],
        'provincia_id': data['provincia_id'],
        'canton_id': data['canton_id'],
        'parroquia_id': data['parroquia_id'],
        'creador': data.get('creador', 'sistema'),
        'creacion': now,
        'modificador': data.get('modificador', data.get('creador', 'sistema')),
        'modificacion': now
    }

    try:
        result = db.session.execute(query, params)
        db.session.commit()
        new_id = result.fetchone()[0]
        
        # Obtener el registro creado
        new_record = db.session.execute(
            db.text("SELECT * FROM actividad_ejecucion_dpa WHERE id = :id"),
            {'id': new_id}
        ).fetchone()
        
        if not new_record:
            return jsonify({'error': 'Error al recuperar el registro creado'}), 500
            
        return jsonify(dict(new_record._mapping)), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@actividad_ejecucion_dpa_bp.route('/api/actividad_ejecucion_dpa/<int:id>', methods=['PUT'])
def update_actividad_ejecucion_dpa(id):
    """Actualizar una actividad de ejecución DPA
    ---
    tags:
      - Actividad Ejecución DPA
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
            provincia_id: {type: integer}
            canton_id: {type: integer}
            parroquia_id: {type: integer}
            activo: {type: boolean}
            modificador: {type: string}
    responses:
      200:
        description: Actividad de ejecución DPA actualizada
      404:
        description: No encontrado
    """
    data = request.get_json() or {}
    if not data:
        return jsonify({'error': 'No se proporcionaron datos para actualizar'}), 400

    # Verificar que el registro existe
    existing = db.session.execute(
        db.text("SELECT * FROM actividad_ejecucion_dpa WHERE id = :id"),
        {'id': id}
    ).fetchone()
    
    if not existing:
        return jsonify({'error': 'Registro no encontrado'}), 404

    # Construir la consulta de actualización
    updates = []
    params = {'id': id}
    
    if 'provincia_id' in data:
        updates.append("provincia_id = :provincia_id")
        params['provincia_id'] = data['provincia_id']
    
    if 'canton_id' in data:
        updates.append("canton_id = :canton_id")
        params['canton_id'] = data['canton_id']
    
    if 'parroquia_id' in data:
        updates.append("parroquia_id = :parroquia_id")
        params['parroquia_id'] = data['parroquia_id']
    
    if 'activo' in data:
        updates.append("activo = :activo")
        params['activo'] = data['activo']
    
    # Siempre actualizar modificador y fecha de modificación
    updates.append("modificador = :modificador")
    params['modificador'] = data.get('modificador', 'sistema')
    
    updates.append("modificacion = :modificacion")
    params['modificacion'] = datetime.now(timezone.utc)

    if not updates:
        return jsonify({'error': 'No hay campos para actualizar'}), 400

    query = db.text(f"""
        UPDATE actividad_ejecucion_dpa 
        SET {', '.join(updates)}
        WHERE id = :id
        RETURNING *
    """)

    try:
        result = db.session.execute(query, params)
        db.session.commit()
        updated = result.fetchone()
        
        if not updated:
            return jsonify({'error': 'Error al actualizar el registro'}), 500
            
        return jsonify(dict(updated._mapping))
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@actividad_ejecucion_dpa_bp.route('/api/actividad_ejecucion_dpa/<int:id>', methods=['DELETE'])
def delete_actividad_ejecucion_dpa(id):
    """Eliminar una actividad de ejecución DPA (borrado lógico)
    ---
    tags:
      - Actividad Ejecución DPA
    parameters:
      - name: id
        in: path
        type: integer
        required: true
      - in: body
        name: body
        schema:
          type: object
          properties:
            modificador: {type: string}
    responses:
      200:
        description: Actividad de ejecución DPA eliminada
      404:
        description: No encontrado
    """
    data = request.get_json() or {}
    
    # Verificar que el registro existe
    existing = db.session.execute(
        db.text("SELECT * FROM actividad_ejecucion_dpa WHERE id = :id"),
        {'id': id}
    ).fetchone()
    
    if not existing:
        return jsonify({'error': 'Registro no encontrado'}), 404

    # Realizar borrado lógico
    query = db.text("""
        UPDATE actividad_ejecucion_dpa 
        SET activo = false,
            modificador = :modificador,
            modificacion = :modificacion
        WHERE id = :id
        RETURNING *
    """)
    
    params = {
        'id': id,
        'modificador': data.get('modificador', 'sistema'),
        'modificacion': datetime.now(timezone.utc)
    }

    try:
        result = db.session.execute(query, params)
        db.session.commit()
        deleted = result.fetchone()
        
        if not deleted:
            return jsonify({'error': 'Error al eliminar el registro'}), 500
            
        return jsonify({'mensaje': 'Registro eliminado correctamente'})
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500
