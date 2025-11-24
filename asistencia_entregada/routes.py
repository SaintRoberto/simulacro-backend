from flask import request, jsonify
from asistencia_entregada import asistencia_entregada_bp
from models import db
from datetime import datetime, timezone


@asistencia_entregada_bp.route('/api/asistencia_entregada', methods=['GET'])
def get_asistencia_entregada():
    """Listar asistencias entregadas
    ---
    tags:
      - Asistencia Entregada
    responses:
      200:
        description: Lista de asistencias entregadas
        schema:
          type: array
          items:
            type: object
            properties:
              id: {type: integer}
              emergencia_id: {type: integer}
              provincia_id: {type: integer}
              canton_id: {type: integer}
              parroquia_id: {type: integer}
              sector: {type: string}
              asistencia_categoria_id: {type: integer}
              asistencia_grupo_id: {type: integer}
              asistencia_item_id: {type: integer}
              institucion_donante_id: {type: integer}
              fecha_entrega: {type: string}
              cantidad: {type: integer}
              longitud: {type: number}
              latitud: {type: number}
              familias: {type: integer}
              personas: {type: integer}
              activo: {type: boolean}
              creador: {type: string}
              creacion: {type: string}
              modificador: {type: string}
              modificacion: {type: string}
    """
    result = db.session.execute(db.text("SELECT * FROM asistencia_entregada"))
    items = []
    for row in result:
        items.append({
            'id': row.id,
            'emergencia_id': row.emergencia_id,
            'provincia_id': row.provincia_id,
            'canton_id': row.canton_id,
            'parroquia_id': row.parroquia_id,
            'sector': row.sector,
            'asistencia_categoria_id': row.asistencia_categoria_id,
            'asistencia_grupo_id': row.asistencia_grupo_id,
            'asistencia_item_id': row.asistencia_item_id,
            'institucion_donante_id': row.institucion_donante_id,
            'fecha_entrega': row.fecha_entrega.isoformat() if getattr(row, 'fecha_entrega', None) else None,
            'cantidad': row.cantidad,
            'longitud': float(row.longitud) if getattr(row, 'longitud', None) is not None else None,
            'latitud': float(row.latitud) if getattr(row, 'latitud', None) is not None else None,
            'familias': row.familias,
            'personas': row.personas,
            'activo': row.activo,
            'creador': row.creador,
            'creacion': row.creacion.isoformat() if getattr(row, 'creacion', None) else None,
            'modificador': row.modificador,
            'modificacion': row.modificacion.isoformat() if getattr(row, 'modificacion', None) else None,
        })
    return jsonify(items)


@asistencia_entregada_bp.route('/api/asistencia_entregada/emergencia/<int:emergencia_id>/usuario/<int:usuario_id>', methods=['GET'])
def get_asistencia_entregada_by_emergencia_by_usuario(emergencia_id, usuario_id):
    """Obtener asistencia entregada por emergencia y usuario
    ---
    tags:
      - Asistencia Entregada
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
        description: Lista de asistencias entregadas filtradas por emergencia y usuario
        schema:
          type: array
          items:
            type: object
            properties:
              id: {type: integer}
              parroquia_nombre: {type: string}
              sector: {type: string}
              asistencia_grupo: {type: string}
              asistencia_item: {type: string}
              institucion_donante: {type: string}
              fecha_entrega: {type: string}
              cantidad: {type: integer}
              latitud: {type: number}
              longitud: {type: number}
              familias: {type: integer}
              personas: {type: integer}
    """
    query = db.text("""
        SELECT DISTINCT a.id, q.nombre parroquia_nombre, a.sector, g.nombre asistencia_grupo, t.nombre asistencia_item,
        i.nombre institucion_donante, a.fecha_entrega, a.cantidad, a.latitud, a.longitud, a.familias, a.personas
        FROM asistencia_entregada a
        INNER JOIN public.usuario_perfil_coe_dpa_mesa x ON a.provincia_id = x.provincia_id AND a.canton_id = x.canton_id
        INNER JOIN parroquias q ON a.provincia_id = q.provincia_id AND a.canton_id = q.canton_id AND a.parroquia_id = q.id
        INNER JOIN recurso_grupos g ON g.recurso_categoria_id = 1 AND g.id = a.asistencia_grupo_id
        INNER JOIN recurso_tipos t ON a.asistencia_grupo_id = t.recurso_grupo_id AND a.asistencia_item_id = t.id
        INNER JOIN instituciones i ON a.institucion_donante_id = i.id
        WHERE a.emergencia_id = :emergencia_id
        AND x.usuario_id = :usuario_id
        AND a.activo = true
        ORDER BY a.id ASC;
    """)

    result = db.session.execute(
        query,
        {'emergencia_id': emergencia_id, 'usuario_id': usuario_id}
    )

    items = []
    for row in result:
        items.append({
            'id': row.id,
            'parroquia_nombre': row.parroquia_nombre,
            'sector': row.sector,
            'asistencia_grupo': row.asistencia_grupo,
            'asistencia_item': row.asistencia_item,
            'institucion_donante': row.institucion_donante,
            'fecha_entrega': row.fecha_entrega.isoformat() if getattr(row, 'fecha_entrega', None) else None,
            'cantidad': row.cantidad,
            'latitud': float(row.latitud) if getattr(row, 'latitud', None) is not None else None,
            'longitud': float(row.longitud) if getattr(row, 'longitud', None) is not None else None,
            'familias': row.familias,
            'personas': row.personas,
        })

    return jsonify(items)


@asistencia_entregada_bp.route('/api/asistencia_entregada', methods=['POST'])
def create_asistencia_entregada():
    """Crear asistencia entregada
    ---
    tags:
      - Asistencia Entregada
    consumes:
      - application/json
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          required: [
            emergencia_id, provincia_id, canton_id, parroquia_id,
            sector,
            asistencia_categoria_id, asistencia_grupo_id, asistencia_item_id,
            institucion_donante_id,
            familias, personas
          ]
          properties:
            emergencia_id: {type: integer}
            provincia_id: {type: integer}
            canton_id: {type: integer}
            parroquia_id: {type: integer}
            sector: {type: string}
            asistencia_categoria_id: {type: integer}
            asistencia_grupo_id: {type: integer}
            asistencia_item_id: {type: integer}
            institucion_donante_id: {type: integer}
            fecha_entrega: {type: string}
            cantidad: {type: integer}
            longitud: {type: number}
            latitud: {type: number}
            familias: {type: integer}
            personas: {type: integer}
            activo: {type: boolean}
            creador: {type: string}
    responses:
      201:
        description: Asistencia entregada creada
        schema:
          type: object
          properties:
            id: {type: integer}
            emergencia_id: {type: integer}
            provincia_id: {type: integer}
            canton_id: {type: integer}
            parroquia_id: {type: integer}
            sector: {type: string}
            asistencia_categoria_id: {type: integer}
            asistencia_grupo_id: {type: integer}
            asistencia_item_id: {type: integer}
            institucion_donante_id: {type: integer}
            fecha_entrega: {type: string}
            cantidad: {type: integer}
            longitud: {type: number}
            latitud: {type: number}
            familias: {type: integer}
            personas: {type: integer}
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
        'emergencia_id', 'provincia_id', 'canton_id', 'parroquia_id',
        'sector',
        'asistencia_categoria_id', 'asistencia_grupo_id', 'asistencia_item_id',
        'institucion_donante_id',
        'familias', 'personas'
    ]
    for field in required_fields:
        if field not in data:
            return jsonify({'error': f'{field} is required'}), 400

    now = datetime.now(timezone.utc)

    query = db.text("""
        INSERT INTO asistencia_entregada (
            emergencia_id, provincia_id, canton_id, parroquia_id,
            sector,
            asistencia_categoria_id, asistencia_grupo_id, asistencia_item_id,
            institucion_donante_id,
            fecha_entrega, cantidad, longitud, latitud,
            familias, personas,
            activo, creador, creacion, modificador, modificacion
        )
        VALUES (
            :emergencia_id, :provincia_id, :canton_id, :parroquia_id,
            :sector,
            :asistencia_categoria_id, :asistencia_grupo_id, :asistencia_item_id,
            :institucion_donante_id,
            :fecha_entrega, :cantidad, :longitud, :latitud,
            :familias, :personas,
            :activo, :creador, :creacion, :modificador, :modificacion
        )
        RETURNING id
    """)

    result = db.session.execute(query, {
        'emergencia_id': data['emergencia_id'],
        'provincia_id': data['provincia_id'],
        'canton_id': data['canton_id'],
        'parroquia_id': data['parroquia_id'],
        'sector': data['sector'],
        'asistencia_categoria_id': data['asistencia_categoria_id'],
        'asistencia_grupo_id': data['asistencia_grupo_id'],
        'asistencia_item_id': data['asistencia_item_id'],
        'institucion_donante_id': data['institucion_donante_id'],
        'fecha_entrega': data.get('fecha_entrega'),
        'cantidad': data.get('cantidad', 0),
        'longitud': data.get('longitud', 0),
        'latitud': data.get('latitud', 0),
        'familias': data['familias'],
        'personas': data['personas'],
        'activo': data.get('activo', True),
        'creador': data.get('creador', 'Sistema'),
        'creacion': now,
        'modificador': data.get('creador', 'Sistema'),
        'modificacion': now
    })

    row = result.fetchone()
    if row is None:
        return jsonify({'error': 'No se pudo crear el registro'}), 500
    item_id = row[0]
    db.session.commit()

    item = db.session.execute(
        db.text("SELECT * FROM asistencia_entregada WHERE id = :id"),
        {'id': item_id}
    ).fetchone()

    return jsonify({
        'id': item.id,
        'emergencia_id': item.emergencia_id,
        'provincia_id': item.provincia_id,
        'canton_id': item.canton_id,
        'parroquia_id': item.parroquia_id,
        'sector': item.sector,
        'asistencia_categoria_id': item.asistencia_categoria_id,
        'asistencia_grupo_id': item.asistencia_grupo_id,
        'asistencia_item_id': item.asistencia_item_id,
        'institucion_donante_id': item.institucion_donante_id,
        'fecha_entrega': item.fecha_entrega.isoformat() if getattr(item, 'fecha_entrega', None) else None,
        'cantidad': item.cantidad,
        'longitud': float(item.longitud) if getattr(item, 'longitud', None) is not None else None,
        'latitud': float(item.latitud) if getattr(item, 'latitud', None) is not None else None,
        'familias': item.familias,
        'personas': item.personas,
        'activo': item.activo,
        'creador': item.creador,
        'creacion': item.creacion.isoformat() if getattr(item, 'creacion', None) else None,
        'modificador': item.modificador,
        'modificacion': item.modificacion.isoformat() if getattr(item, 'modificacion', None) else None,
    }), 201


@asistencia_entregada_bp.route('/api/asistencia_entregada/<int:id>', methods=['GET'])
def get_asistencia_entregada_item(id):
    """Obtener asistencia entregada por ID
    ---
    tags:
      - Asistencia Entregada
    parameters:
      - name: id
        in: path
        type: integer
        required: true
    responses:
      200:
        description: Asistencia entregada
        schema:
          type: object
          properties:
            id: {type: integer}
            emergencia_id: {type: integer}
            provincia_id: {type: integer}
            canton_id: {type: integer}
            parroquia_id: {type: integer}
            sector: {type: string}
            asistencia_categoria_id: {type: integer}
            asistencia_grupo_id: {type: integer}
            asistencia_item_id: {type: integer}
            institucion_donante_id: {type: integer}
            fecha_entrega: {type: string}
            cantidad: {type: integer}
            longitud: {type: number}
            latitud: {type: number}
            familias: {type: integer}
            personas: {type: integer}
            activo: {type: boolean}
            creador: {type: string}
            creacion: {type: string}
            modificador: {type: string}
            modificacion: {type: string}
      404:
        description: No encontrado
    """
    result = db.session.execute(
        db.text("SELECT * FROM asistencia_entregada WHERE id = :id"),
        {'id': id}
    )
    item = result.fetchone()

    if not item:
        return jsonify({'error': 'Asistencia entregada no encontrada'}), 404

    return jsonify({
        'id': item.id,
        'emergencia_id': item.emergencia_id,
        'provincia_id': item.provincia_id,
        'canton_id': item.canton_id,
        'parroquia_id': item.parroquia_id,
        'sector': item.sector,
        'asistencia_categoria_id': item.asistencia_categoria_id,
        'asistencia_grupo_id': item.asistencia_grupo_id,
        'asistencia_item_id': item.asistencia_item_id,
        'institucion_donante_id': item.institucion_donante_id,
        'fecha_entrega': item.fecha_entrega.isoformat() if getattr(item, 'fecha_entrega', None) else None,
        'cantidad': item.cantidad,
        'longitud': float(item.longitud) if getattr(item, 'longitud', None) is not None else None,
        'latitud': float(item.latitud) if getattr(item, 'latitud', None) is not None else None,
        'familias': item.familias,
        'personas': item.personas,
        'activo': item.activo,
        'creador': item.creador,
        'creacion': item.creacion.isoformat() if getattr(item, 'creacion', None) else None,
        'modificador': item.modificador,
        'modificacion': item.modificacion.isoformat() if getattr(item, 'modificacion', None) else None,
    })


@asistencia_entregada_bp.route('/api/asistencia_entregada/<int:id>', methods=['PUT'])
def update_asistencia_entregada(id):
    """Actualizar asistencia entregada
    ---
    tags:
      - Asistencia Entregada
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
            provincia_id: {type: integer}
            canton_id: {type: integer}
            parroquia_id: {type: integer}
            sector: {type: string}
            asistencia_categoria_id: {type: integer}
            asistencia_grupo_id: {type: integer}
            asistencia_item_id: {type: integer}
            institucion_donante_id: {type: integer}
            fecha_entrega: {type: string}
            cantidad: {type: integer}
            longitud: {type: number}
            latitud: {type: number}
            familias: {type: integer}
            personas: {type: integer}
            activo: {type: boolean}
            modificador: {type: string}
    responses:
      200:
        description: Asistencia entregada actualizada
        schema:
          type: object
    """
    data = request.get_json()
    now = datetime.now(timezone.utc)

    fields = [
        'emergencia_id', 'provincia_id', 'canton_id', 'parroquia_id',
        'sector',
        'asistencia_categoria_id', 'asistencia_grupo_id', 'asistencia_item_id',
        'institucion_donante_id',
        'fecha_entrega', 'cantidad', 'longitud', 'latitud',
        'familias', 'personas', 'activo'
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
        UPDATE asistencia_entregada
        SET {', '.join(update_fields)}
        WHERE id = :id
    """)

    result = db.session.execute(query, params)

    if getattr(result, 'rowcount', 0) == 0:
        return jsonify({'error': 'Asistencia entregada no encontrada'}), 404

    db.session.commit()

    item = db.session.execute(
        db.text("SELECT * FROM asistencia_entregada WHERE id = :id"),
        {'id': id}
    ).fetchone()

    if not item:
        return jsonify({'error': 'Asistencia entregada no encontrada'}), 404

    return jsonify({
        'id': item.id,
        'emergencia_id': item.emergencia_id,
        'provincia_id': item.provincia_id,
        'canton_id': item.canton_id,
        'parroquia_id': item.parroquia_id,
        'sector': item.sector,
        'asistencia_categoria_id': item.asistencia_categoria_id,
        'asistencia_grupo_id': item.asistencia_grupo_id,
        'asistencia_item_id': item.asistencia_item_id,
        'institucion_donante_id': item.institucion_donante_id,
        'fecha_entrega': item.fecha_entrega.isoformat() if getattr(item, 'fecha_entrega', None) else None,
        'cantidad': item.cantidad,
        'longitud': float(item.longitud) if getattr(item, 'longitud', None) is not None else None,
        'latitud': float(item.latitud) if getattr(item, 'latitud', None) is not None else None,
        'familias': item.familias,
        'personas': item.personas,
        'activo': item.activo,
        'creador': item.creador,
        'creacion': item.creacion.isoformat() if getattr(item, 'creacion', None) else None,
        'modificador': item.modificador,
        'modificacion': item.modificacion.isoformat() if getattr(item, 'modificacion', None) else None,
    })


@asistencia_entregada_bp.route('/api/asistencia_entregada/<int:id>', methods=['DELETE'])
def delete_asistencia_entregada(id):
    """Eliminar asistencia entregada
    ---
    tags:
      - Asistencia Entregada
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
        db.text("DELETE FROM asistencia_entregada WHERE id = :id"),
        {'id': id}
    )

    if getattr(result, 'rowcount', 0) == 0:
        return jsonify({'error': 'Asistencia entregada no encontrada'}), 404

    db.session.commit()
    return jsonify({'mensaje': 'Asistencia entregada eliminada correctamente'})
