from flask import request, jsonify
from alojamientos import alojamientos_bp
from models import db
from datetime import datetime, timezone


@alojamientos_bp.route('/api/alojamientos', methods=['GET'])
def get_alojamientos():
    """Listar alojamientos
    ---
    tags:
      - Alojamiento
    responses:
      200:
        description: Lista de alojamientos
        schema:
          type: array
          items:
            type: object
            properties:
              id: {type: integer}
              provincia_id: {type: integer}
              canton_id: {type: integer}
              parroquia_id: {type: integer}
              sector: {type: string}
              direccion: {type: string}
              nombre: {type: string}
              codigo: {type: string}
              tipo_id: {type: integer}
              fecha_inspeccion: {type: string}
              latitud: {type: number}
              longitud: {type: number}
              capacidad_personas: {type: integer}
              capacidad_familias: {type: integer}
              responsable_nombre: {type: string}
              responsable_telefono: {type: string}
              situacion_id: {type: integer}
              estado_id: {type: integer}
              activo: {type: boolean}
              creador: {type: string}
              creacion: {type: string}
              modificador: {type: string}
              modificacion: {type: string}
    """
    result = db.session.execute(db.text("SELECT * FROM alojamientos"))
    items = []
    for row in result:
        items.append({
            'id': row.id,
            'provincia_id': row.provincia_id,
            'canton_id': row.canton_id,
            'parroquia_id': row.parroquia_id,
            'sector': row.sector,
            'direccion': row.direccion,
            'nombre': row.nombre,
            'codigo': row.codigo,
            'tipo_id': row.tipo_id,
            'fecha_inspeccion': row.fecha_inspeccion.isoformat() if getattr(row, 'fecha_inspeccion', None) else None,
            'latitud': float(row.latitud) if getattr(row, 'latitud', None) is not None else None,
            'longitud': float(row.longitud) if getattr(row, 'longitud', None) is not None else None,
            'capacidad_personas': row.capacidad_personas,
            'capacidad_familias': row.capacidad_familias,
            'responsable_nombre': row.responsable_nombre,
            'responsable_telefono': row.responsable_telefono,
            'situacion_id': row.situacion_id,
            'estado_id': row.estado_id,
            'activo': row.activo,
            'creador': row.creador,
            'creacion': row.creacion.isoformat() if getattr(row, 'creacion', None) else None,
            'modificador': row.modificador,
            'modificacion': row.modificacion.isoformat() if getattr(row, 'modificacion', None) else None,
        })
    return jsonify(items)


@alojamientos_bp.route('/api/alojamientos/provincia/<int:provincia_id>/canton/<int:canton_id>', methods=['GET'])
def get_alojamientos_by_provincia_by_canton(provincia_id, canton_id):
    """Listar alojamientos por provincia y cantón
    ---
    tags:
      - Alojamiento
    parameters:
      - name: provincia_id
        in: path
        type: integer
        required: true
      - name: canton_id
        in: path
        type: integer
        required: true
    responses:
      200:
        description: Lista de alojamientos filtrados por provincia y cantón
        schema:
          type: array
          items:
            type: object
            properties:
              id: {type: integer}
              provincia_id: {type: integer}
              canton_id: {type: integer}
              parroquia_id: {type: integer}
              sector: {type: string}
              direccion: {type: string}
              nombre: {type: string}
              codigo: {type: string}
              tipo_id: {type: integer}
              fecha_inspeccion: {type: string}
              latitud: {type: number}
              longitud: {type: number}
              capacidad_personas: {type: integer}
              capacidad_familias: {type: integer}
              responsable_nombre: {type: string}
              responsable_telefono: {type: string}
              situacion_id: {type: integer}
              estado_id: {type: integer}
              activo: {type: boolean}
    """
    query = db.text("""
        SELECT *
        FROM alojamientos
        WHERE provincia_id = :provincia_id
          AND (canton_id = :canton_id or :canton_id = 0)
          AND activo = true
        ORDER BY id ASC;
    """)

    result = db.session.execute(query, {'provincia_id': provincia_id, 'canton_id': canton_id})
    items = []
    for row in result:
        items.append({
            'id': row.id,
            'provincia_id': row.provincia_id,
            'canton_id': row.canton_id,
            'parroquia_id': row.parroquia_id,
            'sector': row.sector,
            'direccion': row.direccion,
            'nombre': row.nombre,
            'codigo': row.codigo,
            'tipo_id': row.tipo_id,
            'fecha_inspeccion': row.fecha_inspeccion.isoformat() if getattr(row, 'fecha_inspeccion', None) else None,
            'latitud': float(row.latitud) if getattr(row, 'latitud', None) is not None else None,
            'longitud': float(row.longitud) if getattr(row, 'longitud', None) is not None else None,
            'capacidad_personas': row.capacidad_personas,
            'capacidad_familias': row.capacidad_familias,
            'responsable_nombre': row.responsable_nombre,
            'responsable_telefono': row.responsable_telefono,
            'situacion_id': row.situacion_id,
            'estado_id': row.estado_id,
            'activo': row.activo,
        })
    return jsonify(items)


@alojamientos_bp.route('/api/alojamientos', methods=['POST'])
def create_alojamiento():
    """Crear alojamiento
    ---
    tags:
      - Alojamiento
    consumes:
      - application/json
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          required: [
            provincia_id, canton_id, parroquia_id,
            sector, direccion, nombre,
            tipo_id,
            capacidad_personas, capacidad_familias,
            situacion_id, estado_id
          ]
          properties:
            provincia_id: {type: integer}
            canton_id: {type: integer}
            parroquia_id: {type: integer}
            sector: {type: string}
            direccion: {type: string}
            nombre: {type: string}
            codigo: {type: string}
            tipo_id: {type: integer}
            fecha_inspeccion: {type: string}
            latitud: {type: number}
            longitud: {type: number}
            capacidad_personas: {type: integer}
            capacidad_familias: {type: integer}
            responsable_nombre: {type: string}
            responsable_telefono: {type: string}
            situacion_id: {type: integer}
            estado_id: {type: integer}
            activo: {type: boolean}
            creador: {type: string}
    responses:
      201:
        description: Alojamiento creado
        schema:
          type: object
          properties:
            id: {type: integer}
            provincia_id: {type: integer}
            canton_id: {type: integer}
            parroquia_id: {type: integer}
            sector: {type: string}
            direccion: {type: string}
            nombre: {type: string}
            codigo: {type: string}
            tipo_id: {type: integer}
            fecha_inspeccion: {type: string}
            latitud: {type: number}
            longitud: {type: number}
            capacidad_personas: {type: integer}
            capacidad_familias: {type: integer}
            responsable_nombre: {type: string}
            responsable_telefono: {type: string}
            situacion_id: {type: integer}
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
        'provincia_id', 'canton_id', 'parroquia_id',
        'sector', 'direccion', 'nombre',
        'tipo_id',
        'capacidad_personas', 'capacidad_familias',
        'situacion_id', 'estado_id'
    ]
    for field in required_fields:
        if field not in data:
            return jsonify({'error': f'{field} is required'}), 400

    now = datetime.now(timezone.utc)

    query = db.text("""
        INSERT INTO alojamientos (
            provincia_id, canton_id, parroquia_id,
            sector, direccion, nombre,
            codigo,
            tipo_id,
            fecha_inspeccion, latitud, longitud,
            capacidad_personas, capacidad_familias,
            responsable_nombre, responsable_telefono,
            situacion_id, estado_id,
            activo, creador, creacion, modificador, modificacion
        )
        VALUES (
            :provincia_id, :canton_id, :parroquia_id,
            :sector, :direccion, :nombre,
            :codigo,
            :tipo_id,
            :fecha_inspeccion, :latitud, :longitud,
            :capacidad_personas, :capacidad_familias,
            :responsable_nombre, :responsable_telefono,
            :situacion_id, :estado_id,
            :activo, :creador, :creacion, :modificador, :modificacion
        )
        RETURNING id
    """)

    result = db.session.execute(query, {
        'provincia_id': data['provincia_id'],
        'canton_id': data['canton_id'],
        'parroquia_id': data['parroquia_id'],
        'sector': data['sector'],
        'direccion': data['direccion'],
        'nombre': data['nombre'],
        'codigo': data.get('codigo'),
        'tipo_id': data['tipo_id'],
        'fecha_inspeccion': data.get('fecha_inspeccion'),
        'latitud': data.get('latitud', 0),
        'longitud': data.get('longitud', 0),
        'capacidad_personas': data['capacidad_personas'],
        'capacidad_familias': data['capacidad_familias'],
        'responsable_nombre': data.get('responsable_nombre'),
        'responsable_telefono': data.get('responsable_telefono'),
        'situacion_id': data['situacion_id'],
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
        db.text("SELECT * FROM alojamientos WHERE id = :id"),
        {'id': item_id}
    ).fetchone()

    return jsonify({
        'id': item.id,
        'provincia_id': item.provincia_id,
        'canton_id': item.canton_id,
        'parroquia_id': item.parroquia_id,
        'sector': item.sector,
        'direccion': item.direccion,
        'nombre': item.nombre,
        'codigo': item.codigo,
        'tipo_id': item.tipo_id,
        'fecha_inspeccion': item.fecha_inspeccion.isoformat() if getattr(item, 'fecha_inspeccion', None) else None,
        'latitud': float(item.latitud) if getattr(item, 'latitud', None) is not None else None,
        'longitud': float(item.longitud) if getattr(item, 'longitud', None) is not None else None,
        'capacidad_personas': item.capacidad_personas,
        'capacidad_familias': item.capacidad_familias,
        'responsable_nombre': item.responsable_nombre,
        'responsable_telefono': item.responsable_telefono,
        'situacion_id': item.situacion_id,
        'estado_id': item.estado_id,
        'activo': item.activo,
        'creador': item.creador,
        'creacion': item.creacion.isoformat() if getattr(item, 'creacion', None) else None,
        'modificador': item.modificador,
        'modificacion': item.modificacion.isoformat() if getattr(item, 'modificacion', None) else None,
    }), 201


@alojamientos_bp.route('/api/alojamientos/<int:id>', methods=['GET'])
def get_alojamiento(id):
    """Obtener alojamiento por ID
    ---
    tags:
      - Alojamiento
    parameters:
      - name: id
        in: path
        type: integer
        required: true
    responses:
      200:
        description: Alojamiento
        schema:
          type: object
          properties:
            id: {type: integer}
            provincia_id: {type: integer}
            canton_id: {type: integer}
            parroquia_id: {type: integer}
            sector: {type: string}
            direccion: {type: string}
            nombre: {type: string}
            codigo: {type: string}
            tipo_id: {type: integer}
            fecha_inspeccion: {type: string}
            latitud: {type: number}
            longitud: {type: number}
            capacidad_personas: {type: integer}
            capacidad_familias: {type: integer}
            responsable_nombre: {type: string}
            responsable_telefono: {type: string}
            situacion_id: {type: integer}
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
        db.text("SELECT * FROM alojamientos WHERE id = :id"),
        {'id': id}
    )
    item = result.fetchone()

    if not item:
        return jsonify({'error': 'Alojamiento no encontrado'}), 404

    return jsonify({
        'id': item.id,
        'provincia_id': item.provincia_id,
        'canton_id': item.canton_id,
        'parroquia_id': item.parroquia_id,
        'sector': item.sector,
        'direccion': item.direccion,
        'nombre': item.nombre,
        'codigo': item.codigo,
        'tipo_id': item.tipo_id,
        'fecha_inspeccion': item.fecha_inspeccion.isoformat() if getattr(item, 'fecha_inspeccion', None) else None,
        'latitud': float(item.latitud) if getattr(item, 'latitud', None) is not None else None,
        'longitud': float(item.longitud) if getattr(item, 'longitud', None) is not None else None,
        'capacidad_personas': item.capacidad_personas,
        'capacidad_familias': item.capacidad_familias,
        'responsable_nombre': item.responsable_nombre,
        'responsable_telefono': item.responsable_telefono,
        'situacion_id': item.situacion_id,
        'estado_id': item.estado_id,
        'activo': item.activo,
        'creador': item.creador,
        'creacion': item.creacion.isoformat() if getattr(item, 'creacion', None) else None,
        'modificador': item.modificador,
        'modificacion': item.modificacion.isoformat() if getattr(item, 'modificacion', None) else None,
    })


@alojamientos_bp.route('/api/alojamientos/<int:id>', methods=['PUT'])
def update_alojamiento(id):
    """Actualizar alojamiento
    ---
    tags:
      - Alojamiento
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
            provincia_id: {type: integer}
            canton_id: {type: integer}
            parroquia_id: {type: integer}
            sector: {type: string}
            direccion: {type: string}
            nombre: {type: string}
            codigo: {type: string}
            tipo_id: {type: integer}
            fecha_inspeccion: {type: string}
            latitud: {type: number}
            longitud: {type: number}
            capacidad_personas: {type: integer}
            capacidad_familias: {type: integer}
            responsable_nombre: {type: string}
            responsable_telefono: {type: string}
            situacion_id: {type: integer}
            estado_id: {type: integer}
            activo: {type: boolean}
            modificador: {type: string}
    responses:
      200:
        description: Alojamiento actualizado
        schema:
          type: object
    """
    data = request.get_json()
    now = datetime.now(timezone.utc)

    fields = [
        'provincia_id', 'canton_id', 'parroquia_id',
        'sector', 'direccion', 'nombre',
        'codigo', 'tipo_id', 'fecha_inspeccion',
        'latitud', 'longitud',
        'capacidad_personas', 'capacidad_familias',
        'responsable_nombre', 'responsable_telefono',
        'situacion_id', 'estado_id', 'activo'
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
        UPDATE alojamientos
        SET {', '.join(update_fields)}
        WHERE id = :id
    """)

    result = db.session.execute(query, params)

    if getattr(result, 'rowcount', 0) == 0:
        return jsonify({'error': 'Alojamiento no encontrado'}), 404

    db.session.commit()

    item = db.session.execute(
        db.text("SELECT * FROM alojamientos WHERE id = :id"),
        {'id': id}
    ).fetchone()

    if not item:
        return jsonify({'error': 'Alojamiento no encontrado'}), 404

    return jsonify({
        'id': item.id,
        'provincia_id': item.provincia_id,
        'canton_id': item.canton_id,
        'parroquia_id': item.parroquia_id,
        'sector': item.sector,
        'direccion': item.direccion,
        'nombre': item.nombre,
        'codigo': item.codigo,
        'tipo_id': item.tipo_id,
        'fecha_inspeccion': item.fecha_inspeccion.isoformat() if getattr(item, 'fecha_inspeccion', None) else None,
        'latitud': float(item.latitud) if getattr(item, 'latitud', None) is not None else None,
        'longitud': float(item.longitud) if getattr(item, 'longitud', None) is not None else None,
        'capacidad_personas': item.capacidad_personas,
        'capacidad_familias': item.capacidad_familias,
        'responsable_nombre': item.responsable_nombre,
        'responsable_telefono': item.responsable_telefono,
        'situacion_id': item.situacion_id,
        'estado_id': item.estado_id,
        'activo': item.activo,
        'creador': item.creador,
        'creacion': item.creacion.isoformat() if getattr(item, 'creacion', None) else None,
        'modificador': item.modificador,
        'modificacion': item.modificacion.isoformat() if getattr(item, 'modificacion', None) else None,
    })


@alojamientos_bp.route('/api/alojamientos/<int:id>', methods=['DELETE'])
def delete_alojamiento(id):
    """Eliminar alojamiento
    ---
    tags:
      - Alojamiento
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
        db.text("DELETE FROM alojamientos WHERE id = :id"),
        {'id': id}
    )

    if getattr(result, 'rowcount', 0) == 0:
        return jsonify({'error': 'Alojamiento no encontrado'}), 404

    db.session.commit()
    return jsonify({'mensaje': 'Alojamiento eliminado correctamente'})
