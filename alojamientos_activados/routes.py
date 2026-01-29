from flask import request, jsonify
from alojamientos_activados import alojamientos_activados_bp
from models import db
from datetime import datetime, timezone


@alojamientos_activados_bp.route('/api/alojamientos_activados', methods=['GET'])
def get_alojamientos_activados():
    """Listar alojamientos activados
    ---
    tags:
      - Alojamiento Activados
    responses:
      200:
        description: Lista de alojamientos activados
        schema:
          type: array
          items:
            type: object
            properties:
              id: {type: integer}
              emergencia_id: {type: integer}
              alojamiento_id: {type: integer}
              fecha_activacion: {type: string}
              fecha_cierre: {type: string}
              responsable_nombre: {type: string}
              responsable_telefono: {type: string}
              personas_ingresaron: {type: integer}
              familias_ingresaron: {type: integer}
              personas_salieron: {type: integer}
              familias_salieron: {type: integer}
              estado_id: {type: integer}
              activo: {type: boolean}
              creador: {type: string}
              creacion: {type: string}
              modificador: {type: string}
              modificacion: {type: string}
    """
    result = db.session.execute(db.text("SELECT * FROM alojamientos_activados"))
    items = []
    for row in result:
        items.append({
            'id': row.id,
            'emergencia_id': row.emergencia_id,
            'alojamiento_id': row.alojamiento_id,
            'fecha_activacion': row.fecha_activacion.isoformat() if getattr(row, 'fecha_activacion', None) else None,
            'fecha_cierre': row.fecha_cierre.isoformat() if getattr(row, 'fecha_cierre', None) else None,
            'responsable_nombre': row.responsable_nombre,
            'responsable_telefono': row.responsable_telefono,
            'personas_ingresaron': row.personas_ingresaron,
            'familias_ingresaron': row.familias_ingresaron,
            'personas_salieron': row.personas_salieron,
            'familias_salieron': row.familias_salieron,
            'estado_id': row.estado_id,
            'activo': row.activo,
            'creador': row.creador,
            'creacion': row.creacion.isoformat() if getattr(row, 'creacion', None) else None,
            'modificador': row.modificador,
            'modificacion': row.modificacion.isoformat() if getattr(row, 'modificacion', None) else None,
        })
    return jsonify(items)


@alojamientos_activados_bp.route('/api/alojamientos_activados/emergencia/<int:emergencia_id>/usuario/<int:usuario_id>', methods=['GET'])
def get_alojamientos_activados_by_emergencia_by_usuario(emergencia_id, usuario_id):
    """Obtener alojamientos activados por emergencia y usuario
    ---
    tags:
      - Alojamiento Activados
    parameters:
      - name: emergencia_id
        in: path
        type: integer
        required: true
      - name: usuario_id
        in: path
        type: integer
        required: true
    responses:
      200:
        description: Lista de alojamientos activados filtrados por emergencia y usuario
        schema:
          type: array
          items:
            type: object
            properties:
              id: {type: integer}
              parroquia_nombre: {type: string}
              fecha_activacion: {type: string}
              alojamiento_nombre: {type: string}
              alojamiento_estado: {type: string}
              alojamiento_tipo: {type: string}
              capacidad_personas: {type: integer}
              capacidad_familias: {type: integer}
              personas_ingresaron: {type: integer}
              familias_ingresaron: {type: integer}
              personas_salieron: {type: integer}
              familias_salieron: {type: integer}
    """
    query = db.text("""
        SELECT aa.id, q.nombre parroquia_nombre, aa.fecha_activacion, a.nombre alojamiento_nombre, e.nombre alojamiento_estado,
        t.nombre alojamiento_tipo, a.capacidad_personas, a.capacidad_familias, aa.personas_ingresaron, aa.familias_ingresaron,
        aa.personas_salieron, aa.familias_salieron
        FROM public.alojamientos_activados aa
        INNER JOIN public.alojamientos a ON aa.alojamiento_id = a.id
        INNER JOIN public.usuario_perfil_coe_dpa_mesa x ON a.provincia_id = x.provincia_id AND (a.canton_id = x.canton_id OR x.canton_id = 0)
        INNER JOIN parroquias q ON a.provincia_id = q.provincia_id AND a.canton_id = q.canton_id AND a.parroquia_id = q.id
        INNER JOIN alojamiento_estados e ON aa.estado_id = e.id
        INNER JOIN alojamiento_tipos t ON a.tipo_id = t.id
        WHERE aa.emergencia_id = :emergencia_id
        AND x.usuario_id = :usuario_id
        AND aa.activo = true
        ORDER BY aa.id ASC;
    """)

    result = db.session.execute(query, {'emergencia_id': emergencia_id, 'usuario_id': usuario_id})
    items = []
    for row in result:
        items.append({
            'id': row.id,
            'parroquia_nombre': row.parroquia_nombre,
            'fecha_activacion': row.fecha_activacion.isoformat() if getattr(row, 'fecha_activacion', None) else None,
            'alojamiento_nombre': row.alojamiento_nombre,
            'alojamiento_estado': row.alojamiento_estado,
            'alojamiento_tipo': row.alojamiento_tipo,
            'capacidad_personas': row.capacidad_personas,
            'capacidad_familias': row.capacidad_familias,
            'personas_ingresaron': row.personas_ingresaron,
            'familias_ingresaron': row.familias_ingresaron,
            'personas_salieron': row.personas_salieron,
            'familias_salieron': row.familias_salieron,
        })

    return jsonify(items)


@alojamientos_activados_bp.route('/api/alojamientos_activados', methods=['POST'])
def create_alojamiento_activado():
    """Crear alojamiento activado
    ---
    tags:
      - Alojamiento Activados
    consumes:
      - application/json
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          required: [
            emergencia_id, alojamiento_id,
            estado_id
          ]
          properties:
            emergencia_id: {type: integer}
            alojamiento_id: {type: integer}
            fecha_activacion: {type: string}
            fecha_cierre: {type: string}
            responsable_nombre: {type: string}
            responsable_telefono: {type: string}
            personas_ingresaron: {type: integer}
            familias_ingresaron: {type: integer}
            personas_salieron: {type: integer}
            familias_salieron: {type: integer}
            estado_id: {type: integer}
            activo: {type: boolean}
            creador: {type: string}
    responses:
      201:
        description: Alojamiento activado creado
        schema:
          type: object
          properties:
            id: {type: integer}
            emergencia_id: {type: integer}
            alojamiento_id: {type: integer}
            fecha_activacion: {type: string}
            fecha_cierre: {type: string}
            responsable_nombre: {type: string}
            responsable_telefono: {type: string}
            personas_ingresaron: {type: integer}
            familias_ingresaron: {type: integer}
            personas_salieron: {type: integer}
            familias_salieron: {type: integer}
            estado_id: {type: integer}
            activo: {type: boolean}
            creador: {type: string}
            creacion: {type: string}
            modificador: {type: string}
            modificacion: {type: string}
    """
    data = request.get_json()
    if not data:
        return jsonify({'error': 'Invalid JSON body'}), 400

    required_fields = [
        'emergencia_id', 'alojamiento_id',
        'estado_id'
    ]
    for field in required_fields:
        if field not in data:
            return jsonify({'error': f'{field} is required'}), 400

    now = datetime.now(timezone.utc)

    query = db.text("""
        INSERT INTO alojamientos_activados (
            emergencia_id, alojamiento_id,
            fecha_activacion, fecha_cierre,
            responsable_nombre, responsable_telefono,
            personas_ingresaron, familias_ingresaron,
            personas_salieron, familias_salieron,
            estado_id,
            activo, creador, creacion, modificador, modificacion
        )
        VALUES (
            :emergencia_id, :alojamiento_id,
            :fecha_activacion, :fecha_cierre,
            :responsable_nombre, :responsable_telefono,
            :personas_ingresaron, :familias_ingresaron,
            :personas_salieron, :familias_salieron,
            :estado_id,
            :activo, :creador, :creacion, :modificador, :modificacion
        )
        RETURNING id
    """)

    result = db.session.execute(query, {
        'emergencia_id': data['emergencia_id'],
        'alojamiento_id': data['alojamiento_id'],
        'fecha_activacion': data.get('fecha_activacion'),
        'fecha_cierre': data.get('fecha_cierre'),
        'responsable_nombre': data.get('responsable_nombre'),
        'responsable_telefono': data.get('responsable_telefono'),
        'personas_ingresaron': data.get('personas_ingresaron', 0),
        'familias_ingresaron': data.get('familias_ingresaron', 0),
        'personas_salieron': data.get('personas_salieron', 0),
        'familias_salieron': data.get('familias_salieron', 0),
        'estado_id': data['estado_id'],
        'activo': data.get('activo', True),
        'creador': data.get('creador', 'Sistema'),
        'creacion': now,
        'modificador': data.get('creador', 'Sistema'),
        'modificacion': now,
    })

    row = result.fetchone()
    if row is None:
        return jsonify({'error': 'No se pudo crear el registro'}), 500
    item_id = row[0]
    db.session.commit()

    item = db.session.execute(
        db.text("SELECT * FROM alojamientos_activados WHERE id = :id"),
        {'id': item_id}
    ).fetchone()

    return jsonify({
        'id': item.id,
        'emergencia_id': item.emergencia_id,
        'alojamiento_id': item.alojamiento_id,
        'fecha_activacion': item.fecha_activacion.isoformat() if getattr(item, 'fecha_activacion', None) else None,
        'fecha_cierre': item.fecha_cierre.isoformat() if getattr(item, 'fecha_cierre', None) else None,
        'responsable_nombre': item.responsable_nombre,
        'responsable_telefono': item.responsable_telefono,
        'personas_ingresaron': item.personas_ingresaron,
        'familias_ingresaron': item.familias_ingresaron,
        'personas_salieron': item.personas_salieron,
        'familias_salieron': item.familias_salieron,
        'estado_id': item.estado_id,
        'activo': item.activo,
        'creador': item.creador,
        'creacion': item.creacion.isoformat() if getattr(item, 'creacion', None) else None,
        'modificador': item.modificador,
        'modificacion': item.modificacion.isoformat() if getattr(item, 'modificacion', None) else None,
    }), 201


@alojamientos_activados_bp.route('/api/alojamientos_activados/<int:id>', methods=['GET'])
def get_alojamiento_activado(id):
    """Obtener alojamiento activado por ID
    ---
    tags:
      - Alojamiento Activados
    parameters:
      - name: id
        in: path
        type: integer
        required: true
    responses:
      200:
        description: Alojamiento activado
        schema:
          type: object
          properties:
            id: {type: integer}
            emergencia_id: {type: integer}
            alojamiento_id: {type: integer}
            fecha_activacion: {type: string}
            fecha_cierre: {type: string}
            responsable_nombre: {type: string}
            responsable_telefono: {type: string}
            personas_ingresaron: {type: integer}
            familias_ingresaron: {type: integer}
            personas_salieron: {type: integer}
            familias_salieron: {type: integer}
            estado_id: {type: integer}
            activo: {type: boolean}
            creador: {type: string}
            creacion: {type: string}
            modificador: {type: string}
            modificacion: {type: string}
      404:
        description: No encontrado
    """
    result = db.session.execute(
        db.text("SELECT * FROM alojamientos_activados WHERE id = :id"),
        {'id': id}
    )
    item = result.fetchone()

    if not item:
        return jsonify({'error': 'Alojamiento activado no encontrado'}), 404

    return jsonify({
        'id': item.id,
        'emergencia_id': item.emergencia_id,
        'alojamiento_id': item.alojamiento_id,
        'fecha_activacion': item.fecha_activacion.isoformat() if getattr(item, 'fecha_activacion', None) else None,
        'fecha_cierre': item.fecha_cierre.isoformat() if getattr(item, 'fecha_cierre', None) else None,
        'responsable_nombre': item.responsable_nombre,
        'responsable_telefono': item.responsable_telefono,
        'personas_ingresaron': item.personas_ingresaron,
        'familias_ingresaron': item.familias_ingresaron,
        'personas_salieron': item.personas_salieron,
        'familias_salieron': item.familias_salieron,
        'estado_id': item.estado_id,
        'activo': item.activo,
        'creador': item.creador,
        'creacion': item.creacion.isoformat() if getattr(item, 'creacion', None) else None,
        'modificador': item.modificador,
        'modificacion': item.modificacion.isoformat() if getattr(item, 'modificacion', None) else None,
    })


@alojamientos_activados_bp.route('/api/alojamientos_activados/<int:id>', methods=['PUT'])
def update_alojamiento_activado(id):
    """Actualizar alojamiento activado
    ---
    tags:
      - Alojamiento Activados
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
            alojamiento_id: {type: integer}
            fecha_activacion: {type: string}
            fecha_cierre: {type: string}
            responsable_nombre: {type: string}
            responsable_telefono: {type: string}
            personas_ingresaron: {type: integer}
            familias_ingresaron: {type: integer}
            personas_salieron: {type: integer}
            familias_salieron: {type: integer}
            estado_id: {type: integer}
            activo: {type: boolean}
            modificador: {type: string}
    responses:
      200:
        description: Alojamiento activado actualizado
        schema:
          type: object
    """
    data = request.get_json()
    now = datetime.now(timezone.utc)

    fields = [
        'emergencia_id', 'alojamiento_id',
        'fecha_activacion', 'fecha_cierre',
        'responsable_nombre', 'responsable_telefono',
        'personas_ingresaron', 'familias_ingresaron',
        'personas_salieron', 'familias_salieron',
        'estado_id', 'activo'
    ]

    update_fields = []
    params = {'id': id, 'modificador': data.get('modificador', 'Sistema'), 'modificacion': now}

    for field in fields:
        if field in data:
            update_fields.append(f"{field} = :{field}")
            params[field] = data[field]

    update_fields.append('modificador = :modificador')
    update_fields.append('modificacion = :modificacion')

    if not update_fields:
        return jsonify({'error': 'No fields to update'}), 400

    query = db.text(f"""
        UPDATE alojamientos_activados
        SET {', '.join(update_fields)}
        WHERE id = :id
    """)

    result = db.session.execute(query, params)

    if getattr(result, 'rowcount', 0) == 0:
        return jsonify({'error': 'Alojamiento activado no encontrado'}), 404

    db.session.commit()

    item = db.session.execute(
        db.text("SELECT * FROM alojamientos_activados WHERE id = :id"),
        {'id': id}
    ).fetchone()

    if not item:
        return jsonify({'error': 'Alojamiento activado no encontrado'}), 404

    return jsonify({
        'id': item.id,
        'emergencia_id': item.emergencia_id,
        'alojamiento_id': item.alojamiento_id,
        'fecha_activacion': item.fecha_activacion.isoformat() if getattr(item, 'fecha_activacion', None) else None,
        'fecha_cierre': item.fecha_cierre.isoformat() if getattr(item, 'fecha_cierre', None) else None,
        'responsable_nombre': item.responsable_nombre,
        'responsable_telefono': item.responsable_telefono,
        'personas_ingresaron': item.personas_ingresaron,
        'familias_ingresaron': item.familias_ingresaron,
        'personas_salieron': item.personas_salieron,
        'familias_salieron': item.familias_salieron,
        'estado_id': item.estado_id,
        'activo': item.activo,
        'creador': item.creador,
        'creacion': item.creacion.isoformat() if getattr(item, 'creacion', None) else None,
        'modificador': item.modificador,
        'modificacion': item.modificacion.isoformat() if getattr(item, 'modificacion', None) else None,
    })


@alojamientos_activados_bp.route('/api/alojamientos_activados/<int:id>', methods=['DELETE'])
def delete_alojamiento_activado(id):
    """Eliminar alojamiento activado
    ---
    tags:
      - Alojamiento Activados
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
    result = db.session.execute(
        db.text("DELETE FROM alojamientos_activados WHERE id = :id"),
        {'id': id}
    )

    if getattr(result, 'rowcount', 0) == 0:
        return jsonify({'error': 'Alojamiento activado no encontrado'}), 404

    db.session.commit()
    return jsonify({'mensaje': 'Alojamiento activado eliminado correctamente'})
