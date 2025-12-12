from flask import request, jsonify, current_app
from . import actividad_ejecucion_funciones_bp
from models import db
from datetime import datetime, timezone

def _row_to_dict(row):
    """Helper function to convert SQL result row to dict"""
    result = {}
    for key in row.keys():
        value = row[key]
        if isinstance(value, datetime):
            result[key] = value.isoformat()
        else:
            result[key] = value
    return result

@actividad_ejecucion_funciones_bp.route('/api/actividad_ejecucion_funciones', methods=['GET'])
def get_actividad_ejecucion_funciones():
    """Listar todas las funciones de ejecución de actividades
    ---
    tags:
      - Actividad Ejecución Funciones
    responses:
      200:
        description: Lista de funciones de ejecución de actividades
        schema:
          type: array
          items:
            type: object
            properties:
              id: {type: integer, description: 'ID único de la función'}
              coe_id: {type: integer, description: 'ID del COE relacionado'}
              mesa_id: {type: integer, description: 'ID de la mesa relacionada'}
              linea_accion: {type: string, description: 'Línea de acción', nullable: true}
              descripcion: {type: string, description: 'Descripción detallada', nullable: true}
              producto: {type: string, description: 'Producto esperado', nullable: true}
              activo: {type: boolean, description: 'Indica si el registro está activo'}
              creador: {type: string, description: 'Usuario que creó el registro', nullable: true}
              creacion: {type: string, format: date-time, description: 'Fecha de creación'}
              modificador: {type: string, description: 'Usuario que modificó el registro', nullable: true}
              modificacion: {type: string, format: date-time, nullable: true, description: 'Fecha de modificación'}
    """
    try:
        query = """
            SELECT id, coe_id, mesa_id, linea_accion, descripcion, producto, 
                   activo, creador, creacion, modificador, modificacion
            FROM actividad_ejecucion_funciones
            WHERE activo = TRUE
        """
        result = db.session.execute(query)
        funciones = [_row_to_dict(row) for row in result.mappings()]
        return jsonify(funciones)
    except Exception as e:
        current_app.logger.error(f"Error al obtener funciones: {str(e)}")
        return jsonify({"error": "Error al obtener las funciones de ejecución"}), 500

@actividad_ejecucion_funciones_bp.route('/api/actividad_ejecucion_funciones/<int:id>', methods=['GET'])
def get_actividad_ejecucion_funcion(id):
    """Obtener una función de ejecución por ID
    ---
    tags:
      - Actividad Ejecución Funciones
    parameters:
      - name: id
        in: path
        type: integer
        required: true
        description: ID de la función a consultar
    responses:
      200:
        description: Detalles de la función de ejecución
        schema:
          type: object
          properties:
            id: {type: integer, description: 'ID único de la función'}
            coe_id: {type: integer, description: 'ID del COE relacionado'}
            mesa_id: {type: integer, description: 'ID de la mesa relacionada'}
            linea_accion: {type: string, description: 'Línea de acción', nullable: true}
            descripcion: {type: string, description: 'Descripción detallada', nullable: true}
            producto: {type: string, description: 'Producto esperado', nullable: true}
            activo: {type: boolean, description: 'Indica si el registro está activo'}
            creador: {type: string, description: 'Usuario que creó el registro', nullable: true}
            creacion: {type: string, format: date-time, description: 'Fecha de creación'}
            modificador: {type: string, description: 'Usuario que modificó el registro', nullable: true}
            modificacion: {type: string, format: date-time, nullable: true, description: 'Fecha de modificación'}
      404:
        description: Función no encontrada
      500:
        description: Error del servidor
    """
    try:
        query = """
            SELECT id, coe_id, mesa_id, linea_accion, descripcion, producto, 
                   activo, creador, creacion, modificador, modificacion
            FROM actividad_ejecucion_funciones
            WHERE id = :id AND activo = TRUE
        """
        result = db.session.execute(query, {'id': id}).mappings().first()
        if not result:
            return jsonify({'error': 'Función de ejecución no encontrada'}), 404
        return jsonify(_row_to_dict(result))
    except Exception as e:
        current_app.logger.error(f"Error al obtener función {id}: {str(e)}")
        return jsonify({"error": "Error al obtener la función de ejecución"}), 500

@actividad_ejecucion_funciones_bp.route('/api/actividad_ejecucion_funciones/coe/<int:coe_id>/mesa/<int:mesa_id>', methods=['GET'])
def get_actividad_ejecucion_funcion_by_coe_by_mesa(coe_id, mesa_id):
    """Obtener funciones de ejecución por COE y Mesa
    ---
    tags:
      - Actividad Ejecución Funciones
    parameters:
      - name: coe_id
        in: path
        type: integer
        required: true
        description: ID del COE
      - name: mesa_id
        in: path
        type: integer
        required: true
        description: ID de la mesa
    responses:
      200:
        description: Lista de funciones de ejecución
        schema:
          type: array
          items:
            type: object
            properties:
              id: {type: integer, description: 'ID de la función'}
              descripcion: {type: string, description: 'Descripción formateada (linea_accion - descripcion)'}
    """
    try:
        query = """
            SELECT f.id, f.linea_accion || ' - ' || f.descripcion as descripcion 
            FROM public.actividad_ejecucion_funciones f
			      INNER JOIN public.mesas m ON f.mesa_grupo_id = m.mesa_grupo_id
            WHERE f.coe_id = :coe_id 
            AND m.id = :mesa_id
            AND f.activo = true
            ORDER BY f.id ASC
        """
        
        result = db.session.execute(
            query,
            {'coe_id': coe_id, 'mesa_id': mesa_id}
        )
        
        return jsonify([
            {'id': row[0], 'descripcion': row[1]}
            for row in result.fetchall()
        ])
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'error': 'Error al obtener las funciones de ejecución',
            'details': str(e)
        }), 500

@actividad_ejecucion_funciones_bp.route('/api/actividad_ejecucion_funciones', methods=['POST'])
def create_actividad_ejecucion_funcion():
    """Crear una nueva función de ejecución
    ---
    tags:
      - Actividad Ejecución Funciones
    consumes:
      - application/json
    parameters:
      - in: body
        name: body
        required: true
        description: Datos de la función de ejecución a crear
        schema:
          type: object
          required: [coe_id, mesa_id]
          properties:
            coe_id: 
              type: integer
              description: ID del COE relacionado
            mesa_id: 
              type: integer
              description: ID de la mesa relacionada
            linea_accion: 
              type: string
              description: Línea de acción (opcional)
            descripcion: 
              type: string
              description: Descripción detallada (opcional)
            producto: 
              type: string
              description: Producto esperado (opcional)
            creador: 
              type: string
              description: Usuario que crea el registro (opcional)
    responses:
      201:
        description: Función de ejecución creada exitosamente
        schema:
          type: object
          properties:
            id: {type: integer, description: 'ID de la función creada'}
            message: {type: string, description: 'Mensaje de confirmación'}
      400:
        description: Datos de entrada inválidos
      500:
        description: Error del servidor
    """
    data = request.get_json()
    
    # Validar datos requeridos
    if not all(key in data for key in ['coe_id', 'mesa_id']):
        return jsonify({'error': 'Faltan campos requeridos: coe_id y mesa_id'}), 400
            
    # Obtener datos con valores por defecto
    linea_accion = data.get('linea_accion')
    descripcion = data.get('descripcion')
    producto = data.get('producto')
    creador = data.get('creador')
    ahora = datetime.now(timezone.utc)
        
    # Insertar nueva función
    query = """
        INSERT INTO actividad_ejecucion_funciones 
            (coe_id, mesa_id, linea_accion, descripcion, producto, 
             activo, creador, creacion, modificador, modificacion)
        VALUES 
            (:coe_id, :mesa_id, :linea_accion, :descripcion, :producto,
             TRUE, :creador, :ahora, :creador, :ahora)
        RETURNING id
    """
    params = {
        'coe_id': data['coe_id'],
        'mesa_id': data['mesa_id'],
        'linea_accion': linea_accion,
        'descripcion': descripcion,
        'producto': producto,
        'creador': creador,
        'ahora': ahora
    }
        
    try:
        result = db.session.execute(query, params)
        db.session.commit()
        return jsonify({
            'id': result.scalar(),
            'message': 'Función de ejecución creada exitosamente'
        }), 201
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error al crear función: {str(e)}")
        return jsonify({'error': 'Error al crear la función de ejecución'}), 500

@actividad_ejecucion_funciones_bp.route('/api/actividad_ejecucion_funciones/<int:id>', methods=['PUT'])
def update_actividad_ejecucion_funcion(id):
    """Actualizar una función de ejecución existente
    ---
    tags:
      - Actividad Ejecución Funciones
    consumes:
      - application/json
    parameters:
      - name: id
        in: path
        type: integer
        required: true
        description: ID de la función a actualizar
      - in: body
        name: body
        required: true
        description: Campos a actualizar
        schema:
          type: object
          properties:
            coe_id: 
              type: integer
              description: ID del COE relacionado
            mesa_id: 
              type: integer
              description: ID de la mesa relacionada
            linea_accion: 
              type: string
              description: Línea de acción
            descripcion: 
              type: string
              description: Descripción detallada
            producto: 
              type: string
              description: Producto esperado
            activo: 
              type: boolean
              description: Indica si el registro está activo
            modificador: 
              type: string
              description: Usuario que realiza la modificación
    responses:
      200:
        description: Función de ejecución actualizada exitosamente
        schema:
          type: object
          properties:
            id: {type: integer, description: 'ID de la función actualizada'}
            message: {type: string, description: 'Mensaje de confirmación'}
      404:
        description: Función no encontrada
      500:
        description: Error del servidor
    """
    try:
        # Primero verificar si existe
        check_query = "SELECT id FROM actividad_ejecucion_funciones WHERE id = :id AND activo = TRUE"
        if not db.session.execute(check_query, {'id': id}).fetchone():
            return jsonify({'error': 'Función de ejecución no encontrada'}), 404
        
        data = request.get_json()
        
        # Construir la consulta dinámicamente basada en los campos proporcionados
        update_fields = []
        params = {'id': id}
        
        # Lista de campos actualizables
        allowed_fields = ['coe_id', 'mesa_id', 'linea_accion', 'descripcion', 
                         'producto', 'activo', 'modificador']
        
        for field in allowed_fields:
            if field in data:
                update_fields.append(f"{field} = :{field}")
                params[field] = data[field]
        
        # Agregar la fecha de modificación
        update_fields.append("modificacion = :modificacion")
        params['modificacion'] = datetime.now(timezone.utc)
        
        # Construir y ejecutar la consulta
        update_query = f"""
            UPDATE actividad_ejecucion_funciones 
            SET {', '.join(update_fields)}
            WHERE id = :id
            RETURNING id
        """
        
        result = db.session.execute(update_query, params)
        db.session.commit()
        
        if not result.rowcount:
            return jsonify({'error': 'No se pudo actualizar la función de ejecución'}), 500
            
        return jsonify({
            'id': id,
            'message': 'Función de ejecución actualizada exitosamente'
        })
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error al actualizar función {id}: {str(e)}")
        return jsonify({'error': 'Error al actualizar la función de ejecución'}), 500

@actividad_ejecucion_funciones_bp.route('/api/actividad_ejecucion_funciones/<int:id>', methods=['DELETE'])
def delete_actividad_ejecucion_funcion(id):
    """Eliminar una función de ejecución (eliminación lógica)
    ---
    tags:
      - Actividad Ejecución Funciones
    parameters:
      - name: id
        in: path
        type: integer
        required: true
        description: ID de la función a eliminar
    responses:
      200:
        description: Función de ejecución eliminada exitosamente
        schema:
          type: object
          properties:
            message: {type: string, description: 'Mensaje de confirmación'}
            id: {type: integer, description: 'ID de la función eliminada'}
      404:
        description: Función no encontrada
      500:
        description: Error del servidor
    """
    try:
        # Verificar si existe
        check_query = "SELECT id FROM actividad_ejecucion_funciones WHERE id = :id AND activo = TRUE"
        if not db.session.execute(check_query, {'id': id}).fetchone():
            return jsonify({'error': 'Función de ejecución no encontrada'}), 404
        
        # Eliminación lógica
        delete_query = """
            UPDATE actividad_ejecucion_funciones 
            SET activo = FALSE, 
                modificacion = :modificacion
            WHERE id = :id
            RETURNING id
        """
        
        result = db.session.execute(
            delete_query, 
            {'id': id, 'modificacion': datetime.now(timezone.utc)}
        )
        db.session.commit()
        
        if not result.rowcount:
            return jsonify({'error': 'No se pudo eliminar la función de ejecución'}), 500
            
        return jsonify({
            'message': 'Función de ejecución eliminada exitosamente',
            'id': id
        })
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error al eliminar función {id}: {str(e)}")
        return jsonify({'error': 'Error al eliminar la función de ejecución'}), 500
