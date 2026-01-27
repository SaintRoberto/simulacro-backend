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
              funcion_descripcion: {type: string, description: 'Nombre de la funcion a ejecutar'}
              funcion_linea_accion: {type: string, description: 'Nombre de la linea de ejecucion de la funcion a ejecutar'}
              institucion_ejecutora_id: {type: integer, description: 'ID de la institución ejecutora'}
              institucion_ejecutora_nombre: {type: string, description: 'Nombre de la institución ejecutora'}
              institucion_ejecutora_siglas: {type: string, description: 'Siglas de la institución ejecutora'}
              fecha_inicio: {type: string, format: date-time, description: 'Fecha de inicio de la actividad'}
              porcentaje_avance_id: {type: integer, description: 'ID del porcentaje de avance'}
              porcentaje_avance: {type: string, description: 'Nombre del porcentaje de avance'}
              instituciones_apoyo: {type: string, description: 'Instituciones de apoyo para la actividad', nullable: true}
              ubicaciones_atendidas: {type: string, description: 'Ubicaciones atendidas por la actividad', nullable: true}
              fecha_final: {type: string, format: date-time, nullable: true, description: 'Fecha de finalización de la actividad'}
              actividad_ejecucion_estado_id: {type: integer, description: 'ID del estado de la actividad'}
              actividad_ejecucion_estado: {type: string, description: 'Nombre del estado de la actividad'}
              detalle: {type: string, description: 'Detalle descriptivo de la actividad', nullable: true}
    """
    query = """
          SELECT 
              ae.id, 
              ae.accion_respuesta_id,
              ae.actividad_ejecucion_funcion_id,
              f.descripcion as funcion_descripcion,
              f.linea_accion as funcion_linea_accion,
              ae.institucion_ejecutora_id,
              i.nombre as institucion_ejecutora_nombre,
              i.siglas as institucion_ejecutora_siglas,
              ae.fecha_inicio, 
              ae.porcentaje_avance_id, p.nombre as porcentaje_avance,
              ae.instituciones_apoyo,
              ae.ubicaciones_atendidas,
              ae.fecha_final,
              ae.actividad_ejecucion_estado_id,
              e.nombre as actividad_ejecucion_estado,
              ae.detalle
          FROM actividades_ejecucion ae
          LEFT JOIN instituciones i ON ae.institucion_ejecutora_id = i.id
          LEFT JOIN actividad_ejecucion_estados e ON ae.actividad_ejecucion_estado_id = e.id
          LEFT JOIN respuesta_avances p ON ae.porcentaje_avance_id = p.id
          LEFT JOIN actividad_ejecucion_funciones f ON ae.actividad_ejecucion_funcion_id = f.id
          WHERE ae.activo = true
          ORDER BY ae.fecha_inicio DESC
    """
    result = db.session.execute(db.text(query))
    items = []
    for row in result:
        item = _row_to_dict(row)
        response_item = {
            'id': item.get('id'),
            'accion_respuesta_id': item.get('accion_respuesta_id'),
            'actividad_ejecucion_funcion_id': item.get('actividad_ejecucion_funcion_id'),
            'funcion_descripcion': item.get('funcion_descripcion'),
            'funcion_linea_accion': item.get('funcion_linea_accion'),
            'institucion_ejecutora_id': item.get('institucion_ejecutora_id'),
            'institucion_ejecutora_nombre': item.get('institucion_ejecutora_nombre'),
            'institucion_ejecutora_siglas': item.get('institucion_ejecutora_siglas'),
            'fecha_inicio': item.get('fecha_inicio'),
            'porcentaje_avance_id': item.get('porcentaje_avance_id'),
            'porcentaje_avance': item.get('porcentaje_avance'),
            'instituciones_apoyo': item.get('instituciones_apoyo'),
            'ubicaciones_atendidas': item.get('ubicaciones_atendidas'),
            'fecha_final': item.get('fecha_final'),
            'actividad_ejecucion_estado_id': item.get('actividad_ejecucion_estado_id'),
            'actividad_ejecucion_estado': item.get('actividad_ejecucion_estado'),
            'detalle': item.get('detalle')
        }
        items.append(response_item)
    return jsonify(items)

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
              id: {type: integer, description: 'ID único de la actividad de ejecución'}
              accion_respuesta_id: {type: integer, description: 'ID de la acción de respuesta relacionada'}
              actividad_ejecucion_funcion_id: {type: integer, description: 'ID de la función de ejecución'}
              funcion_descripcion: {type: string, description: 'Nombre de la funcion a ejecutar'}
              funcion_linea_accion: {type: string, description: 'Nombre de la linea de ejecucion de la funcion a ejecutar'}
              institucion_ejecutora_id: {type: integer, description: 'ID de la institución ejecutora'}
              institucion_ejecutora_nombre: {type: string, description: 'Nombre de la institución ejecutora'}
              institucion_ejecutora_siglas: {type: string, description: 'Siglas de la institución ejecutora'}
              fecha_inicio: {type: string, format: date-time, description: 'Fecha de inicio de la actividad'}
              porcentaje_avance_id: {type: integer, description: 'ID del porcentaje de avance'}
              porcentaje_avance: {type: string, description: 'Nombre del porcentaje de avance'}
              instituciones_apoyo: {type: string, nullable: true, description: 'Instituciones de apoyo para la actividad'}
              ubicaciones_atendidas: {type: string, nullable: true, description: 'Ubicaciones atendidas por la actividad'}
              fecha_final: {type: string, format: date-time, nullable: true, description: 'Fecha de finalización de la actividad'}
              actividad_ejecucion_estado_id: {type: integer, description: 'ID del estado de la actividad'}
              actividad_ejecucion_estado: {type: string, description: 'Nombre del estado de la actividad'}
              detalle: {type: string, description: 'Detalle descriptivo de la actividad', nullable: true}
    """
    query = """
        SELECT 
            ae.id, 
            ae.accion_respuesta_id,
            ae.actividad_ejecucion_funcion_id,
            f.descripcion as funcion_descripcion,
            f.linea_accion as funcion_linea_accion,
            ae.institucion_ejecutora_id,
            i.nombre as institucion_ejecutora_nombre,
            i.siglas as institucion_ejecutora_siglas,
            ae.fecha_inicio, 
            ae.porcentaje_avance_id as porcentaje_avance,
            ae.instituciones_apoyo,
            ae.ubicaciones_atendidas,
            ae.fecha_final,
            ae.actividad_ejecucion_estado_id,
            e.nombre as actividad_ejecucion_estado,
            ae.detalle
        FROM actividades_ejecucion ae
        LEFT JOIN instituciones i ON ae.institucion_ejecutora_id = i.id
        LEFT JOIN actividad_ejecucion_estados e ON ae.actividad_ejecucion_estado_id = e.id
        
        LEFT JOIN actividad_ejecucion_funciones f ON ae.actividad_ejecucion_funcion_id = f.id
        WHERE ae.accion_respuesta_id = :accion_respuesta_id
        AND ae.activo = true
        ORDER BY ae.fecha_inicio DESC
    """
    result = db.session.execute(db.text(query), {'accion_respuesta_id': accion_respuesta_id})
    items = []
    for row in result:
        item = _row_to_dict(row)
        response_item = {
            'id': item.get('id'),
            'accion_respuesta_id': item.get('accion_respuesta_id'),
            'actividad_ejecucion_funcion_id': item.get('actividad_ejecucion_funcion_id'),
            'funcion_descripcion': item.get('funcion_descripcion'),
            'funcion_linea_accion': item.get('funcion_linea_accion'),
            'institucion_ejecutora_id': item.get('institucion_ejecutora_id'),
            'institucion_ejecutora_nombre': item.get('institucion_ejecutora_nombre'),
            'institucion_ejecutora_siglas': item.get('institucion_ejecutora_siglas'),
            'fecha_inicio': item.get('fecha_inicio'),
            'porcentaje_avance': item.get('porcentaje_avance'),
            'instituciones_apoyo': item.get('instituciones_apoyo'),
            'ubicaciones_atendidas': item.get('ubicaciones_atendidas'),
            'fecha_final': item.get('fecha_final'),
            'actividad_ejecucion_estado_id': item.get('actividad_ejecucion_estado_id'),
            'actividad_ejecucion_estado': item.get('actividad_ejecucion_estado'),
            'detalle': item.get('detalle')
        }
        items.append(response_item)
    return jsonify(items)

@actividades_ejecucion_bp.route('/api/actividades_ejecucion/coe/<int:coe_id>/mesa_grupo/<int:mesa_grupo_id>/accion_respuesta/<int:accion_respuesta_id>', methods=['GET'])
def get_actividades_ejecucion_by_coe_mesa_grupo_accion_respuesta(coe_id, mesa_grupo_id, accion_respuesta_id):
    """Listar actividades de ejecución por COE, mesa/grupo y acción de respuesta
    ---
    tags:
      - Actividades Ejecucion
    parameters:
      - name: coe_id
        in: path
        type: integer
        required: true
        description: ID del COE
      - name: mesa_grupo_id
        in: path
        type: integer
        required: true
        description: ID de la mesa o grupo de trabajo
      - name: accion_respuesta_id
        in: path
        type: integer
        required: true
        description: ID de la acción de respuesta
    responses:
      200:
        description: Lista de funciones y actividades de ejecución para la combinación especificada
        schema:
          type: array
          items:
            type: object
            properties:
              funcion_id: {type: integer, description: 'ID de la función de ejecución'}
              descripcion: {type: string, description: 'Descripción de la función de ejecución'}
              ejecucion_id: {type: integer, nullable: true, description: 'ID de la actividad de ejecución (si existe)'}
              institucion_ejecutora_nombre: {type: string, nullable: true, description: 'Nombre de la institución ejecutora'}
              fecha_inicio: {type: string, format: date-time, nullable: true, description: 'Fecha de inicio de la actividad'}
              porcentaje_avance: {type: string, nullable: true, description: 'Nombre del porcentaje de avance'}
              fecha_final: {type: string, format: date-time, nullable: true, description: 'Fecha de finalización de la actividad'}
              estado_actividad: {type: string, nullable: true, description: 'Estado de la actividad de ejecución'}
              instituciones_apoyo: {type: string, nullable: true, description: 'Instituciones de apoyo para la actividad'}
              ubicaciones_atendidas: {type: string, nullable: true, description: 'Ubicaciones atendidas por la actividad'}
    """
    query = db.text("""
        SELECT f.id funcion_id, f.descripcion, e.id ejecucion_id, i.nombre institucion_ejecutora_nombre, e.fecha_inicio,
               e.porcentaje_avance_id porcentaje_avance, e.fecha_final, s.nombre estado_actividad, e.instituciones_apoyo, e.ubicaciones_atendidas
        FROM public.actividad_ejecucion_funciones f
        LEFT JOIN public.actividades_ejecucion e ON f.id = e.actividad_ejecucion_funcion_id AND e.accion_respuesta_id = :accion_respuesta_id
        LEFT JOIN public.instituciones i ON e.institucion_ejecutora_id = i.id
        LEFT JOIN public.actividad_ejecucion_estados s ON e.actividad_ejecucion_estado_id = s.id
        WHERE f.coe_id = :coe_id AND  f.mesa_grupo_id = :mesa_grupo_id
        ORDER BY f.id ASC
    """)
    result = db.session.execute(query, {
        'coe_id': coe_id,
        'mesa_grupo_id': mesa_grupo_id,
        'accion_respuesta_id': accion_respuesta_id,
    })

    items = []
    for row in result:
        item = _row_to_dict(row)
        items.append({
            'funcion_id': item.get('funcion_id'),
            'descripcion': item.get('descripcion'),
            'ejecucion_id': item.get('ejecucion_id'),
            'institucion_ejecutora_nombre': item.get('institucion_ejecutora_nombre'),
            'fecha_inicio': item.get('fecha_inicio'),
            'porcentaje_avance': item.get('porcentaje_avance'),
            'fecha_final': item.get('fecha_final'),
            'estado_actividad': item.get('estado_actividad'),
            'instituciones_apoyo': item.get('instituciones_apoyo'),
            'ubicaciones_atendidas': item.get('ubicaciones_atendidas'),
        })

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
            instituciones_apoyo:
              type: string
              description: Instituciones de apoyo para la actividad (opcional)
            ubicaciones_atendidas:
              type: string
              description: Ubicaciones atendidas por la actividad (opcional)
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

    # Validar campos requeridos (mantener compatibilidad con la validación previa)
    required_fields = [
      'accion_respuesta_id',
      'actividad_ejecucion_funcion_id',
      'institucion_ejecutora_id',
      'fecha_inicio',
      'actividad_ejecucion_estado_id'
    ]

    missing_fields = [field for field in required_fields if field not in data]
    if missing_fields:
      return jsonify({'error': 'Campos requeridos faltantes', 'missing': missing_fields}), 400

    try:
      now = datetime.now(timezone.utc)

      fecha_inicio = datetime.fromisoformat(data['fecha_inicio'])
      fecha_final = None
      if data.get('fecha_final'):
        fecha_final = datetime.fromisoformat(data['fecha_final'])

      query = db.text("""
        INSERT INTO actividades_ejecucion (
          accion_respuesta_id,
          actividad_ejecucion_funcion_id,
          institucion_ejecutora_id,
          fecha_inicio,
          porcentaje_avance_id,
          instituciones_apoyo,
          ubicaciones_atendidas,
          fecha_final,
          actividad_ejecucion_estado_id,
          detalle,
          activo,
          creador,
          creacion,
          modificador,
          modificacion
        )
        VALUES (
          :accion_respuesta_id,
          :actividad_ejecucion_funcion_id,
          :institucion_ejecutora_id,
          :fecha_inicio,
          :porcentaje_avance_id,
          :instituciones_apoyo,
          :ubicaciones_atendidas,
          :fecha_final,
          :actividad_ejecucion_estado_id,
          :detalle,
          :activo,
          :creador,
          :creacion,
          :modificador,
          :modificacion
        )
        RETURNING id
      """)

      params = {
        'accion_respuesta_id': data['accion_respuesta_id'],
        'actividad_ejecucion_funcion_id': data['actividad_ejecucion_funcion_id'],
        'institucion_ejecutora_id': data['institucion_ejecutora_id'],
        'fecha_inicio': fecha_inicio,
        'porcentaje_avance_id': data.get('porcentaje_avance_id', 0),
        'instituciones_apoyo': data.get('instituciones_apoyo'),
        'ubicaciones_atendidas': data.get('ubicaciones_atendidas'),
        'fecha_final': fecha_final,
        'actividad_ejecucion_estado_id': data['actividad_ejecucion_estado_id'],
        'detalle': data.get('detalle'),
        'activo': data.get('activo', True),
        'creador': data.get('creador', 'Sistema'),
        'creacion': now,
        'modificador': data.get('creador', 'Sistema'),
        'modificacion': now
      }

      result = db.session.execute(query, params)
      row = result.fetchone()
      if row is None:
        db.session.rollback()
        return jsonify({'error': 'No se pudo crear la actividad de ejecución'}), 500
      nuevo_id = row[0]
      db.session.commit()

      return jsonify({'id': nuevo_id, 'message': 'Actividad de ejecución creada exitosamente'}), 201

    except Exception as e:
      db.session.rollback()
      return jsonify({'error': 'Error al crear la actividad de ejecución', 'details': str(e)}), 500

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
              id: {type: integer, description: 'ID único de la actividad de ejecución'}
              accion_respuesta_id: {type: integer, description: 'ID de la acción de respuesta relacionada'}
              actividad_ejecucion_funcion_id: {type: integer, description: 'ID de la función de ejecución'}
              funcion_descripcion: {type: string, description: 'Nombre de la funcion a ejecutar'}
              funcion_linea_accion: {type: string, description: 'Nombre de la linea de ejecucion de la funcion a ejecutar'}
              institucion_ejecutora_id: {type: integer, description: 'ID de la institución ejecutora'}
              institucion_ejecutora_nombre: {type: string, description: 'Nombre de la institución ejecutora'}
              institucion_ejecutora_siglas: {type: string, description: 'Siglas de la institución ejecutora'}
              fecha_inicio: {type: string, format: date-time, description: 'Fecha de inicio de la actividad'}
              porcentaje_avance_id: {type: integer, description: 'ID del porcentaje de avance'}
              porcentaje_avance: {type: string, description: 'Nombre del porcentaje de avance'}
              instituciones_apoyo: {type: string, nullable: true, description: 'Instituciones de apoyo para la actividad'}
              ubicaciones_atendidas: {type: string, nullable: true, description: 'Ubicaciones atendidas por la actividad'}
              fecha_final: {type: string, format: date-time, nullable: true, description: 'Fecha de finalización de la actividad'}
              actividad_ejecucion_estado_id: {type: integer, description: 'ID del estado de la actividad'}
              actividad_ejecucion_estado: {type: string, description: 'Nombre del estado de la actividad'}
              detalle: {type: string, description: 'Detalle descriptivo de la actividad', nullable: true}
    """
    try:
      # Query to get the actividad_ejecucion with related data
      query = db.text("""
        SELECT 
          ae.*,
          aef.descripcion as funcion_descripcion,
          aef.linea_accion as funcion_linea_accion,
          i.nombre as institucion_ejecutora_nombre,
          i.siglas as institucion_ejecutora_siglas,
          ae.porcentaje_avance_id as porcentaje_avance,
          aee.descripcion as actividad_ejecucion_estado,
          ae.instituciones_apoyo,
          ae.ubicaciones_atendidas
        FROM 
          actividades_ejecucion ae
          LEFT JOIN actividad_ejecucion_funciones aef ON ae.actividad_ejecucion_funcion_id = aef.id
          LEFT JOIN instituciones i ON ae.institucion_ejecutora_id = i.id
          LEFT JOIN actividad_ejecucion_estados aee ON ae.actividad_ejecucion_estado_id = aee.id
        WHERE 
          ae.id = :id
      """)

      result = db.session.execute(query, {'id': id}).fetchone()
        
      if not result:
          return jsonify({'message': 'Actividad de ejecución no encontrada'}), 404
          
      return jsonify(_row_to_dict(result))
        
    except Exception as e:
        return jsonify({'message': f'Error al obtener la actividad de ejecución: {str(e)}'}), 500


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
              description: ID del porcentaje de avance (opcional, por defecto 0)
              default: 0
            instituciones_apoyo:
              type: string
              description: Instituciones de apoyo para la actividad (opcional)
            ubicaciones_atendidas:
              type: string
              description: Ubicaciones atendidas por la actividad (opcional)
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
            activo: 
              type: boolean
              description: Indica si la actividad está activa (opcional)
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
    try:
        query = """
            SELECT * FROM actividades_ejecucion 
            WHERE id = :id AND activo = true
        """
        result = db.session.execute(db.text(query), {'id': id}).fetchone()
        if not result:
            return jsonify({'error': 'Actividad de ejecución no encontrada'}), 404
        update_fields = []
        params = {'id': id}
        allowed_fields = [
            'accion_respuesta_id',
            'actividad_ejecucion_funcion_id',
            'institucion_ejecutora_id',
            'porcentaje_avance_id',
            'instituciones_apoyo',
            'ubicaciones_atendidas',
            'actividad_ejecucion_estado_id',
            'detalle',
            'activo',
            'modificador'
        ]
        for field in allowed_fields:
            if field in data:
                update_fields.append(f"{field} = :{field}")
                params[field] = data[field]
        if 'fecha_inicio' in data:
            update_fields.append("fecha_inicio = :fecha_inicio")
            params['fecha_inicio'] = datetime.fromisoformat(data['fecha_inicio'])
        if 'fecha_final' in data:
            if data['fecha_final']:
                update_fields.append("fecha_final = :fecha_final")
                params['fecha_final'] = datetime.fromisoformat(data['fecha_final'])
            else:
                update_fields.append("fecha_final = NULL")
        update_fields.append("modificacion = :modificacion")
        params['modificacion'] = datetime.now(timezone.utc)
        if update_fields:
            update_query = f"""
                UPDATE actividades_ejecucion 
                SET {', '.join(update_fields)}
                WHERE id = :id
                RETURNING id
            """
            result = db.session.execute(db.text(update_query), params).fetchone()
            db.session.commit()
            return jsonify({
                'id': result.id,
                'message': 'Actividad de ejecución actualizada exitosamente'
            })
        else:
            return jsonify({
                'id': id,
                'message': 'No se especificaron campos para actualizar'
            })
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'error': 'Error al actualizar la actividad de ejecución',
            'details': str(e)
        }), 500

@actividades_ejecucion_bp.route('/api/actividades_ejecucion/<int:id>', methods=['DELETE'])
def delete_actividad_ejecucion(id):
    """Eliminar una actividad de ejecución
    ---
    tags:
      - Actividades Ejecucion
    parameters:
      - name: id
        in: path
        type: integer
        required: true
        description: ID de la actividad de ejecución a eliminar
    responses:
      200:
        description: Actividad de ejecución eliminada exitosamente
      404:
        description: La actividad de ejecución no fue encontrada
      500:
        description: Error interno del servidor
    """
    try:
        # Verificar si la actividad existe
        check_query = "SELECT id FROM actividades_ejecucion WHERE id = :id AND activo = true"
        result = db.session.execute(db.text(check_query), {'id': id}).fetchone()
        
        if not result:
            return jsonify({'error': 'Actividad de ejecución no encontrada'}), 404
        
        # Realizar eliminación lógica (marcar como inactivo)
        delete_query = """
            UPDATE actividades_ejecucion 
            SET activo = false, 
                modificacion = :modificacion
            WHERE id = :id
            RETURNING id
        """
        
        db.session.execute(
            db.text(delete_query),
            {'id': id, 'modificacion': datetime.now(timezone.utc)}
        )
        db.session.commit()
        
        return jsonify({'message': 'Actividad de ejecución eliminada exitosamente'})
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'error': 'Error al eliminar la actividad de ejecución',
            'details': str(e)
        }), 500