from flask import request, jsonify
from actividades_ejecucion import actividades_ejecucion_bp
from models import db, ActividadEjecucion
from datetime import datetime, timezone

def _row_to_dict(row):
    try:
        mapping = dict(row._mapping)  # SQLAlchemy Row
    except Exception:
        mapping = {k: getattr(row, k) for k in row.keys()}
    for k, v in list(mapping.items()):
        if isinstance(v, datetime):
            mapping[k] = v.isoformat()
    return mapping

@actividades_ejecucion_bp.route('/api/actividades_ejecucion', methods=['GET'])
def get_actividades_ejecucion():
    """Listar actividades de ejecución
    ---
    tags:
      - Actividades Ejecucion
    responses:
      200:
        description: Lista de actividades de ejecución
        schema:
          type: array
          items:
            type: object
            properties:
              id: {type: integer, description: 'ID único de la actividad de ejecución'}
              accion_respuesta_id: {type: integer, description: 'ID de la acción de respuesta relacionada'}
              actividad_ejecucion_funcion_id: {type: integer, description: 'ID de la función de ejecución'}
              institucion_ejecutora_id: {type: integer, description: 'ID de la institución ejecutora'}
              fecha_inicio: {type: string, format: date-time, description: 'Fecha de inicio de la actividad'}
              porcentaje_avance_id: {type: integer, description: 'ID del porcentaje de avance'}
              fecha_final: {type: string, format: date-time, nullable: true, description: 'Fecha de finalización de la actividad'}
              actividad_ejecucion_estado_id: {type: integer, description: 'ID del estado de la actividad'}
              detalle: {type: string, description: 'Detalle descriptivo de la actividad', nullable: true}
              activo: {type: boolean, description: 'Indica si el registro está activo'}
              creador: {type: string, description: 'Usuario que creó el registro', nullable: true}
              creacion: {type: string, format: date-time, description: 'Fecha de creación del registro'}
              modificador: {type: string, description: 'Usuario que modificó por última vez el registro', nullable: true}
              modificacion: {type: string, format: date-time, nullable: true, description: 'Fecha de la última modificación'}
    """
    actividades = ActividadEjecucion.query.filter_by(activo=True).all()
    return jsonify([actividad.to_dict() for actividad in actividades])

@actividades_ejecucion_bp.route('/api/actividades_ejecucion/accion_respuesta/<int:accion_respuesta_id>', methods=['GET'])
def get_actividades_ejecucion_by_accion_respuesta(accion_respuesta_id):
    """Listar actividades de ejecución por ID de acción de respuesta
    ---
    tags:
      - Actividades Ejecucion
    parameters:
      - name: accion_respuesta_id
        in: path
        type: integer
        required: true
        description: ID de la acción de respuesta
    responses:
      200:
        description: Lista de actividades para la acción de respuesta especificada
        schema:
          type: array
          items:
            type: object
            properties:
              id: {type: integer, description: 'ID único de la actividad'}
              accion_respuesta_id: {type: integer, description: 'ID de la acción de respuesta'}
              actividad_ejecucion_funcion_id: {type: integer, description: 'ID de la función de ejecución'}
              institucion_ejecutora_id: {type: integer, description: 'ID de la institución ejecutora'}
              institucion_ejecutora_nombre: {type: string, description: 'Nombre de la institución ejecutora'}
              institucion_ejecutora_siglas: {type: string, description: 'Siglas de la institución ejecutora'}
              fecha_inicio: {type: string, format: date-time, description: 'Fecha de inicio de la actividad'}
              porcentaje_avance_id: {type: integer, description: 'ID del porcentaje de avance'}
              fecha_final: {type: string, format: date-time, nullable: true, description: 'Fecha de finalización de la actividad'}
              actividad_ejecucion_estado_id: {type: integer, description: 'ID del estado de la actividad'}
              actividad_ejecucion_estado: {type: string, description: 'Nombre del estado de la actividad'}
              detalle: {type: string, description: 'Detalle descriptivo de la actividad', nullable: true}
              activo: {type: boolean, description: 'Indica si el registro está activo'}
    """
    query = """
        SELECT 
            ae.*,
            i.nombre as institucion_ejecutora_nombre,
            i.siglas as institucion_ejecutora_siglas,
            e.nombre as actividad_ejecucion_estado
        FROM actividades_ejecucion ae
        LEFT JOIN instituciones i ON ae.institucion_ejecutora_id = i.id
        LEFT JOIN estados e ON ae.actividad_ejecucion_estado_id = e.id
        WHERE ae.accion_respuesta_id = :accion_respuesta_id
        AND ae.activo = true
        ORDER BY ae.fecha_inicio DESC
    """
    result = db.session.execute(db.text(query), {'accion_respuesta_id': accion_respuesta_id})
    items = []
    for row in result:
        item = _row_to_dict(row)
        # Remove raw database fields that are not needed in the response
        item.pop('creador', None)
        item.pop('creacion', None)
        item.pop('modificador', None)
        item.pop('modificacion', None)
        items.append(item)
    return jsonify(items)

@actividades_ejecucion_bp.route('/api/actividades_ejecucion', methods=['POST'])
def create_actividad_ejecucion():
    """Crear una nueva actividad de ejecución
    ---
    tags:
      - Actividades Ejecucion
    consumes:
      - application/json
    parameters:
      - in: body
        name: body
        required: true
        description: Datos de la actividad de ejecución a crear
        schema:
          type: object
          required: 
            - accion_respuesta_id
            - actividad_ejecucion_funcion_id
            - institucion_ejecutora_id
            - fecha_inicio
            - actividad_ejecucion_estado_id
          properties:
            accion_respuesta_id: 
              type: integer
              description: ID de la acción de respuesta relacionada
            actividad_ejecucion_funcion_id: 
              type: integer
              description: ID de la función de ejecución
            institucion_ejecutora_id: 
              type: integer
              description: ID de la institución ejecutora
            fecha_inicio: 
              type: string
              format: date-time
              description: Fecha de inicio de la actividad
            porcentaje_avance_id: 
              type: integer
              description: ID del porcentaje de avance (opcional, por defecto 0)
              default: 0
            fecha_final: 
              type: string
              format: date-time
              description: Fecha de finalización de la actividad (opcional)
            actividad_ejecucion_estado_id: 
              type: integer
              description: ID del estado de la actividad
            detalle: 
              type: string
              description: Detalle descriptivo de la actividad (opcional)
            creador: 
              type: string
              description: Usuario que crea el registro (opcional)
    responses:
      201:
        description: Actividad de ejecución creada exitosamente
        schema:
          type: object
          properties:
            id: 
              type: integer
              description: ID de la actividad creada
            message: 
              type: string
              description: Mensaje de confirmación
      400:
        description: Datos de entrada inválidos o faltantes
      500:
        description: Error interno del servidor
    """
    data = request.get_json()
    
    # Validar campos requeridos
    required_fields = [
        'accion_respuesta_id', 
        'actividad_ejecucion_funcion_id', 
        'institucion_ejecutora_id', 
        'fecha_inicio',
        'actividad_ejecucion_estado_id'
    ]
    
    missing_fields = [field for field in required_fields if field not in data]
    if missing_fields:
        return jsonify({
            'error': 'Campos requeridos faltantes',
            'missing': missing_fields
        }), 400
    
    try:
        # Crear nueva actividad de ejecución
        actividad = ActividadEjecucion(
            accion_respuesta_id=data['accion_respuesta_id'],
            actividad_ejecucion_funcion_id=data['actividad_ejecucion_funcion_id'],
            institucion_ejecutora_id=data['institucion_ejecutora_id'],
            fecha_inicio=datetime.fromisoformat(data['fecha_inicio']),
            porcentaje_avance_id=data.get('porcentaje_avance_id', 0),
            fecha_final=datetime.fromisoformat(data['fecha_final']) if data.get('fecha_final') else None,
            actividad_ejecucion_estado_id=data['actividad_ejecucion_estado_id'],
            detalle=data.get('detalle'),
            creador=data.get('creador', 'Sistema'),
            activo=True
        )
        
        db.session.add(actividad)
        db.session.commit()
        
        return jsonify({
            'id': actividad.id,
            'message': 'Actividad de ejecución creada exitosamente'
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'error': 'Error al crear la actividad de ejecución',
            'details': str(e)
        }), 500

@actividades_ejecucion_bp.route('/api/actividades_ejecucion/<int:id>', methods=['GET'])
def get_actividad_ejecucion(id):
    """Obtener actividad de ejecución por ID
    ---
    tags:
      - Actividades Ejecucion
    parameters:
      - name: id
        in: path
        type: integer
        required: true
        description: ID de la actividad de ejecución a consultar
    responses:
      200:
        description: Detalles completos de la actividad de ejecución
        schema:
          type: object
          properties:
            id: {type: integer, description: 'ID único de la actividad'}
            accion_respuesta_id: {type: integer, description: 'ID de la acción de respuesta relacionada'}
            actividad_ejecucion_funcion_id: {type: integer, description: 'ID de la función de ejecución'}
            institucion_ejecutora_id: {type: integer, description: 'ID de la institución ejecutora'}
            institucion_ejecutora_nombre: {type: string, description: 'Nombre de la institución ejecutora'}
            fecha_inicio: {type: string, format: date-time, description: 'Fecha de inicio de la actividad'}
            porcentaje_avance_id: {type: integer, description: 'ID del porcentaje de avance'}
            fecha_final: {type: string, format: date-time, nullable: true, description: 'Fecha de finalización de la actividad'}
            actividad_ejecucion_estado_id: {type: integer, description: 'ID del estado de la actividad'}
            actividad_ejecucion_estado: {type: string, description: 'Nombre del estado de la actividad'}
            detalle: {type: string, description: 'Detalle descriptivo de la actividad', nullable: true}
            activo: {type: boolean, description: 'Indica si el registro está activo'}
            creador: {type: string, description: 'Usuario que creó el registro', nullable: true}
            creacion: {type: string, format: date-time, description: 'Fecha de creación del registro'}
            modificador: {type: string, description: 'Usuario que modificó por última vez el registro', nullable: true}
            modificacion: {type: string, format: date-time, nullable: true, description: 'Fecha de la última modificación'}
      404:
        description: La actividad de ejecución no fue encontrada
      500:
        description: Error interno del servidor
    """
    try:
        query = """
            SELECT 
                ae.*,
                i.nombre as institucion_ejecutora_nombre,
                e.nombre as actividad_ejecucion_estado
            FROM actividades_ejecucion ae
            LEFT JOIN instituciones i ON ae.institucion_ejecutora_id = i.id
            LEFT JOIN estados e ON ae.actividad_ejecucion_estado_id = e.id
            WHERE ae.id = :id AND ae.activo = true
        """
        result = db.session.execute(db.text(query), {'id': id}).fetchone()
        
        if not result:
            return jsonify({'error': 'Actividad de ejecución no encontrada'}), 404
        
        return jsonify(_row_to_dict(result))
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@actividades_ejecucion_bp.route('/api/actividades_ejecucion/<int:id>', methods=['PUT'])
def update_actividad_ejecucion(id):
    """Actualizar una actividad de ejecución existente
    ---
    tags:
      - Actividades Ejecucion
    consumes:
      - application/json
    parameters:
      - name: id
        in: path
        type: integer
        required: true
        description: ID de la actividad de ejecución a actualizar
      - in: body
        name: body
        required: true
        description: Campos a actualizar de la actividad
        schema:
          type: object
          properties:
            accion_respuesta_id: 
              type: integer
              description: ID de la acción de respuesta relacionada
            actividad_ejecucion_funcion_id: 
              type: integer
              description: ID de la función de ejecución
            institucion_ejecutora_id: 
              type: integer
              description: ID de la institución ejecutora
            fecha_inicio: 
              type: string
              format: date-time
              description: Fecha de inicio de la actividad
            porcentaje_avance_id: 
              type: integer
              description: ID del porcentaje de avance
            fecha_final: 
              type: string
              format: date-time
              description: Fecha de finalización de la actividad
            actividad_ejecucion_estado_id: 
              type: integer
              description: ID del estado de la actividad
            detalle: 
              type: string
              description: Detalle descriptivo de la actividad
            activo: 
              type: boolean
              description: Indica si la actividad está activa
            modificador: 
              type: string
              description: Usuario que realiza la modificación
    responses:
      200:
        description: Actividad de ejecución actualizada exitosamente
        schema:
          type: object
          properties:
            id: 
              type: integer
              description: ID de la actividad actualizada
            message: 
              type: string
              description: Mensaje de confirmación
      400:
        description: Datos de entrada inválidos
      404:
        description: La actividad de ejecución no fue encontrada
      500:
        description: Error interno del servidor
    """
    data = request.get_json()
    
    # Verificar si la actividad existe
    actividad = ActividadEjecucion.query.filter_by(id=id, activo=True).first()
    if not actividad:
        return jsonify({'error': 'Actividad de ejecución no encontrada'}), 404
    
    try:
        # Actualizar campos permitidos
        field_mapping = {
            'accion_respuesta_id': 'accion_respuesta_id',
            'actividad_ejecucion_funcion_id': 'actividad_ejecucion_funcion_id',
            'institucion_ejecutora_id': 'institucion_ejecutora_id',
            'porcentaje_avance_id': 'porcentaje_avance_id',
            'actividad_ejecucion_estado_id': 'actividad_ejecucion_estado_id',
            'detalle': 'detalle',
            'activo': 'activo',
            'modificador': 'modificador'
        }
        
        for json_field, model_field in field_mapping.items():
            if json_field in data:
                setattr(actividad, model_field, data[json_field])
        
        # Manejo especial para fechas
        if 'fecha_inicio' in data:
            actividad.fecha_inicio = datetime.fromisoformat(data['fecha_inicio'])
            
        if 'fecha_final' in data:
            actividad.fecha_final = datetime.fromisoformat(data['fecha_final']) if data['fecha_final'] else None
        
        # Actualizar la fecha de modificación
        actividad.modificacion = datetime.now(timezone.utc)
        
        db.session.commit()
        
        return jsonify({
            'id': actividad.id,
            'message': 'Actividad de ejecución actualizada exitosamente'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'error': 'Error al actualizar la actividad de ejecución',
            'details': str(e)
        }), 500

@actividades_ejecucion_bp.route('/api/actividades_ejecucion/<int:id>', methods=['DELETE'])
def delete_actividad_ejecucion(id):
    """Eliminar actividad de ejecución
    ---
    tags:
      - Actividades Ejecucion
    parameters:
      - name: id
        in: path
        type: integer
        required: true
    responses:
      200:
        description: Eliminado
      404:
        description: No encontrado
    """
    result = db.session.execute(db.text("DELETE FROM actividades_ejecucion WHERE id = :id"), {'id': id})
    if getattr(result, 'rowcount', 0) == 0:
        return jsonify({'error': 'No encontrado'}), 404
    db.session.commit()
    return jsonify({'mensaje': 'Eliminado correctamente'})