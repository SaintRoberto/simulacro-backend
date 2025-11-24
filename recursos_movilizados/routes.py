from flask import request, jsonify
from recursos_movilizados import recursos_movilizados_bp
from models import db
from datetime import datetime, timezone


@recursos_movilizados_bp.route('/api/recursos_movilizados', methods=['GET'])
def get_recursos_movilizados():
    """Listar recursos movilizados
    ---
    tags:
      - Recursos Movilizados
    responses:
      200:
        description: Lista de recursos movilizados
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
              recurso_categoria_id: {type: integer}
              recurso_grupo_id: {type: integer}
              recurso_tipo_id: {type: integer}
              institucion_id: {type: integer}
              fecha_inicio: {type: string}
              fecha_fin: {type: string}
              cantidad: {type: integer}
              longitud: {type: number}
              latitud: {type: number}
              disponible: {type: boolean}
              activo: {type: boolean}
              creador: {type: string}
              creacion: {type: string}
              modificador: {type: string}
              modificacion: {type: string}
    """
    result = db.session.execute(db.text("SELECT * FROM recursos_movilizados"))
    recursos = []
    for row in result:
        recursos.append({
            'id': row.id,
            'emergencia_id': row.emergencia_id,
            'provincia_id': row.provincia_id,
            'canton_id': row.canton_id,
            'parroquia_id': row.parroquia_id,
            'recurso_categoria_id': row.recurso_categoria_id,
            'recurso_grupo_id': row.recurso_grupo_id,
            'recurso_tipo_id': row.recurso_tipo_id,
            'institucion_id': row.institucion_id,
            'fecha_inicio': row.fecha_inicio.isoformat() if getattr(row, 'fecha_inicio', None) else None,
            'fecha_fin': row.fecha_fin.isoformat() if getattr(row, 'fecha_fin', None) else None,
            'cantidad': row.cantidad,
            'longitud': float(row.longitud) if getattr(row, 'longitud', None) is not None else None,
            'latitud': float(row.latitud) if getattr(row, 'latitud', None) is not None else None,
            'disponible': row.disponible,
            'activo': row.activo,
            'creador': row.creador,
            'creacion': row.creacion.isoformat() if getattr(row, 'creacion', None) else None,
            'modificador': row.modificador,
            'modificacion': row.modificacion.isoformat() if getattr(row, 'modificacion', None) else None,
        })
    return jsonify(recursos)

@recursos_movilizados_bp.route(
    '/api/recursos_movilizados/emergencia/<int:emergencia_id>/usuario/<int:usuario_id>',
    methods=['GET']
)

def get_recursos_movilizados_by_emergencia_by_usuario(emergencia_id, usuario_id):
    """Obtener recursos movilizados por emergencia y usuario
    ---
    tags:
      - Recursos Movilizados
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
        description: Lista de recursos movilizados filtrados por emergencia y usuario
        schema:
          type: array
          items:
            type: object
            properties:
              id: {type: integer}
              parroquia_nombre: {type: string}
              recurso_grupo: {type: string}
              recurso_tipo: {type: string}
              institucion: {type: string}
              fecha_inicio: {type: string}
              fecha_fin: {type: string}
              cantidad: {type: integer}
              disponible: {type: boolean}
              latitud: {type: number}
              longitud: {type: number}
    """
    query = db.text("""
        SELECT DISTINCT r.id, q.nombre parroquia_nombre, g.nombre recurso_grupo, t.nombre recurso_tipo, 
        i.nombre institucion, r.fecha_inicio, r.fecha_fin, r.cantidad, r.disponible, r.latitud, r.longitud
        FROM recursos_movilizados r
        INNER JOIN public.usuario_perfil_coe_dpa_mesa x
          ON r.provincia_id = x.provincia_id AND r.canton_id = x.canton_id
        INNER JOIN parroquias q
          ON r.provincia_id = q.provincia_id AND r.canton_id = q.canton_id AND r.parroquia_id = q.id
        INNER JOIN recurso_grupos g
          ON g.recurso_categoria_id = 2 AND g.id = r.recurso_grupo_id
        INNER JOIN recurso_tipos t
          ON r.recurso_grupo_id = t.recurso_grupo_id AND r.recurso_tipo_id = t.id
        INNER JOIN instituciones i
          ON r.institucion_id = i.id
        WHERE r.emergencia_id = :emergencia_id
          AND x.usuario_id = :usuario_id
          AND r.activo = true
        ORDER BY r.id ASC;
    """)
    result = db.session.execute(
        query,
        {'emergencia_id': emergencia_id, 'usuario_id': usuario_id}
    )
    recursos = []
    for row in result:
        recursos.append({
            'id': row.id,
            'parroquia_nombre': row.parroquia_nombre,
            'recurso_grupo': row.recurso_grupo,
            'recurso_tipo': row.recurso_tipo,
            'institucion': row.institucion,
            'fecha_inicio': row.fecha_inicio.isoformat() if getattr(row, 'fecha_inicio', None) else None,
            'fecha_fin': row.fecha_fin.isoformat() if getattr(row, 'fecha_fin', None) else None,
            'cantidad': row.cantidad,
            'disponible': row.disponible,
            'latitud': float(row.latitud) if getattr(row, 'latitud', None) is not None else None,
            'longitud': float(row.longitud) if getattr(row, 'longitud', None) is not None else None,
        })
    return jsonify(recursos)

@recursos_movilizados_bp.route('/api/recursos_movilizados', methods=['POST'])
def create_recurso_movilizado():
    """Crear recurso movilizado
    ---
    tags:
      - Recursos Movilizados
    consumes:
      - application/json
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          required: [emergencia_id, provincia_id, canton_id, parroquia_id, recurso_categoria_id, recurso_grupo_id, recurso_tipo_id, institucion_id]
          properties:
            emergencia_id: {type: integer}
            provincia_id: {type: integer}
            canton_id: {type: integer}
            parroquia_id: {type: integer}
            recurso_categoria_id: {type: integer}
            recurso_grupo_id: {type: integer}
            recurso_tipo_id: {type: integer}
            institucion_id: {type: integer}
            fecha_inicio: {type: string}
            fecha_fin: {type: string}
            cantidad: {type: integer}
            longitud: {type: number}
            latitud: {type: number}
            disponible: {type: boolean}
            activo: {type: boolean}
            creador: {type: string}
    responses:
      201:
        description: Recurso movilizado creado
        schema:
          type: object
          properties:
            id: {type: integer}
            emergencia_id: {type: integer}
            provincia_id: {type: integer}
            canton_id: {type: integer}
            parroquia_id: {type: integer}
            recurso_categoria_id: {type: integer}
            recurso_grupo_id: {type: integer}
            recurso_tipo_id: {type: integer}
            institucion_id: {type: integer}
            fecha_inicio: {type: string}
            fecha_fin: {type: string}
            cantidad: {type: integer}
            longitud: {type: number}
            latitud: {type: number}
            disponible: {type: boolean}
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
        'recurso_categoria_id', 'recurso_grupo_id', 'recurso_tipo_id', 'institucion_id'
    ]
    for field in required_fields:
        if field not in data:
            return jsonify({'error': f'{field} is required'}), 400

    now = datetime.now(timezone.utc)

    query = db.text("""
        INSERT INTO recursos_movilizados (
            emergencia_id, provincia_id, canton_id, parroquia_id,
            recurso_categoria_id, recurso_grupo_id, recurso_tipo_id, institucion_id,
            fecha_inicio, fecha_fin, cantidad, longitud, latitud,
            disponible, activo, creador, creacion, modificador, modificacion
        )
        VALUES (
            :emergencia_id, :provincia_id, :canton_id, :parroquia_id,
            :recurso_categoria_id, :recurso_grupo_id, :recurso_tipo_id, :institucion_id,
            :fecha_inicio, :fecha_fin, :cantidad, :longitud, :latitud,
            :disponible, :activo, :creador, :creacion, :modificador, :modificacion
        )
        RETURNING id
    """)

    result = db.session.execute(query, {
        'emergencia_id': data['emergencia_id'],
        'provincia_id': data['provincia_id'],
        'canton_id': data['canton_id'],
        'parroquia_id': data['parroquia_id'],
        'recurso_categoria_id': data['recurso_categoria_id'],
        'recurso_grupo_id': data['recurso_grupo_id'],
        'recurso_tipo_id': data['recurso_tipo_id'],
        'institucion_id': data['institucion_id'],
        'fecha_inicio': data.get('fecha_inicio'),
        'fecha_fin': data.get('fecha_fin'),
        'cantidad': data.get('cantidad', 0),
        'longitud': data.get('longitud', 0),
        'latitud': data.get('latitud', 0),
        'disponible': data.get('disponible', True),
        'activo': data.get('activo', True),
        'creador': data.get('creador', 'Sistema'),
        'creacion': now,
        'modificador': data.get('creador', 'Sistema'),
        'modificacion': now,
    })

    row = result.fetchone()
    if row is None:
        db.session.rollback()
        return jsonify({'error': 'Failed to create recurso_movilizado'}), 500

    recurso_id = row[0]
    db.session.commit()

    recurso = db.session.execute(
        db.text("SELECT * FROM recursos_movilizados WHERE id = :id"),
        {'id': recurso_id}
    ).fetchone()

    if not recurso:
        return jsonify({'error': 'Recurso movilizado no encontrado'}), 404

    return jsonify({
        'id': recurso.id,
        'emergencia_id': recurso.emergencia_id,
        'provincia_id': recurso.provincia_id,
        'canton_id': recurso.canton_id,
        'parroquia_id': recurso.parroquia_id,
        'recurso_categoria_id': recurso.recurso_categoria_id,
        'recurso_grupo_id': recurso.recurso_grupo_id,
        'recurso_tipo_id': recurso.recurso_tipo_id,
        'institucion_id': recurso.institucion_id,
        'fecha_inicio': recurso.fecha_inicio.isoformat() if getattr(recurso, 'fecha_inicio', None) else None,
        'fecha_fin': recurso.fecha_fin.isoformat() if getattr(recurso, 'fecha_fin', None) else None,
        'cantidad': recurso.cantidad,
        'longitud': float(recurso.longitud) if getattr(recurso, 'longitud', None) is not None else None,
        'latitud': float(recurso.latitud) if getattr(recurso, 'latitud', None) is not None else None,
        'disponible': recurso.disponible,
        'activo': recurso.activo,
        'creador': recurso.creador,
        'creacion': recurso.creacion.isoformat() if getattr(recurso, 'creacion', None) else None,
        'modificador': recurso.modificador,
        'modificacion': recurso.modificacion.isoformat() if getattr(recurso, 'modificacion', None) else None,
    }), 201


@recursos_movilizados_bp.route('/api/recursos_movilizados/<int:id>', methods=['GET'])
def get_recurso_movilizado(id):
    """Obtener recurso movilizado por ID
    ---
    tags:
      - Recursos Movilizados
    parameters:
      - name: id
        in: path
        type: integer
        required: true
    responses:
      200:
        description: Recurso movilizado
        schema:
          type: object
          properties:
            id: {type: integer}
            emergencia_id: {type: integer}
            provincia_id: {type: integer}
            canton_id: {type: integer}
            parroquia_id: {type: integer}
            recurso_categoria_id: {type: integer}
            recurso_grupo_id: {type: integer}
            recurso_tipo_id: {type: integer}
            institucion_id: {type: integer}
            fecha_inicio: {type: string}
            fecha_fin: {type: string}
            cantidad: {type: integer}
            longitud: {type: number}
            latitud: {type: number}
            disponible: {type: boolean}
            activo: {type: boolean}
            creador: {type: string}
            creacion: {type: string}
            modificador: {type: string}
            modificacion: {type: string}
      404:
        description: No encontrado
    """
    result = db.session.execute(
        db.text("SELECT * FROM recursos_movilizados WHERE id = :id"),
        {'id': id}
    )
    recurso = result.fetchone()

    if not recurso:
        return jsonify({'error': 'Recurso movilizado no encontrado'}), 404

    return jsonify({
        'id': recurso.id,
        'emergencia_id': recurso.emergencia_id,
        'provincia_id': recurso.provincia_id,
        'canton_id': recurso.canton_id,
        'parroquia_id': recurso.parroquia_id,
        'recurso_categoria_id': recurso.recurso_categoria_id,
        'recurso_grupo_id': recurso.recurso_grupo_id,
        'recurso_tipo_id': recurso.recurso_tipo_id,
        'institucion_id': recurso.institucion_id,
        'fecha_inicio': recurso.fecha_inicio.isoformat() if getattr(recurso, 'fecha_inicio', None) else None,
        'fecha_fin': recurso.fecha_fin.isoformat() if getattr(recurso, 'fecha_fin', None) else None,
        'cantidad': recurso.cantidad,
        'longitud': float(recurso.longitud) if getattr(recurso, 'longitud', None) is not None else None,
        'latitud': float(recurso.latitud) if getattr(recurso, 'latitud', None) is not None else None,
        'disponible': recurso.disponible,
        'activo': recurso.activo,
        'creador': recurso.creador,
        'creacion': recurso.creacion.isoformat() if getattr(recurso, 'creacion', None) else None,
        'modificador': recurso.modificador,
        'modificacion': recurso.modificacion.isoformat() if getattr(recurso, 'modificacion', None) else None,
    })


@recursos_movilizados_bp.route('/api/recursos_movilizados/<int:id>', methods=['PUT'])
def update_recurso_movilizado(id):
    """Actualizar recurso movilizado
    ---
    tags:
      - Recursos Movilizados
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
            recurso_categoria_id: {type: integer}
            recurso_grupo_id: {type: integer}
            recurso_tipo_id: {type: integer}
            institucion_id: {type: integer}
            fecha_inicio: {type: string}
            fecha_fin: {type: string}
            cantidad: {type: integer}
            longitud: {type: number}
            latitud: {type: number}
            disponible: {type: boolean}
            activo: {type: boolean}
            modificador: {type: string}
    responses:
      200:
        description: Recurso movilizado actualizado
        schema:
          type: object
          properties:
            id: {type: integer}
            emergencia_id: {type: integer}
            provincia_id: {type: integer}
            canton_id: {type: integer}
            parroquia_id: {type: integer}
            recurso_categoria_id: {type: integer}
            recurso_grupo_id: {type: integer}
            recurso_tipo_id: {type: integer}
            institucion_id: {type: integer}
            fecha_inicio: {type: string}
            fecha_fin: {type: string}
            cantidad: {type: integer}
            longitud: {type: number}
            latitud: {type: number}
            disponible: {type: boolean}
            activo: {type: boolean}
            creador: {type: string}
            creacion: {type: string}
            modificador: {type: string}
            modificacion: {type: string}
      404:
        description: No encontrado
    """
    data = request.get_json()
    now = datetime.now(timezone.utc)

    fields = [
        'emergencia_id', 'provincia_id', 'canton_id', 'parroquia_id',
        'recurso_categoria_id', 'recurso_grupo_id', 'recurso_tipo_id', 'institucion_id',
        'fecha_inicio', 'fecha_fin', 'cantidad', 'longitud', 'latitud',
        'disponible', 'activo'
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
        UPDATE recursos_movilizados
        SET {', '.join(update_fields)}
        WHERE id = :id
    """)

    result = db.session.execute(query, params)

    if getattr(result, 'rowcount', 0) == 0:
        return jsonify({'error': 'Recurso movilizado no encontrado'}), 404

    db.session.commit()

    recurso = db.session.execute(
        db.text("SELECT * FROM recursos_movilizados WHERE id = :id"),
        {'id': id}
    ).fetchone()

    if not recurso:
        return jsonify({'error': 'Recurso movilizado no encontrado'}), 404

    return jsonify({
        'id': recurso.id,
        'emergencia_id': recurso.emergencia_id,
        'provincia_id': recurso.provincia_id,
        'canton_id': recurso.canton_id,
        'parroquia_id': recurso.parroquia_id,
        'recurso_categoria_id': recurso.recurso_categoria_id,
        'recurso_grupo_id': recurso.recurso_grupo_id,
        'recurso_tipo_id': recurso.recurso_tipo_id,
        'institucion_id': recurso.institucion_id,
        'fecha_inicio': recurso.fecha_inicio.isoformat() if getattr(recurso, 'fecha_inicio', None) else None,
        'fecha_fin': recurso.fecha_fin.isoformat() if getattr(recurso, 'fecha_fin', None) else None,
        'cantidad': recurso.cantidad,
        'longitud': float(recurso.longitud) if getattr(recurso, 'longitud', None) is not None else None,
        'latitud': float(recurso.latitud) if getattr(recurso, 'latitud', None) is not None else None,
        'disponible': recurso.disponible,
        'activo': recurso.activo,
        'creador': recurso.creador,
        'creacion': recurso.creacion.isoformat() if getattr(recurso, 'creacion', None) else None,
        'modificador': recurso.modificador,
        'modificacion': recurso.modificacion.isoformat() if getattr(recurso, 'modificacion', None) else None,
    })


@recursos_movilizados_bp.route('/api/recursos_movilizados/<int:id>', methods=['DELETE'])
def delete_recurso_movilizado(id):
    """Eliminar recurso movilizado
    ---
    tags:
      - Recursos Movilizados
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
        db.text("DELETE FROM recursos_movilizados WHERE id = :id"),
        {'id': id}
    )

    if getattr(result, 'rowcount', 0) == 0:
        return jsonify({'error': 'Recurso movilizado no encontrado'}), 404

    db.session.commit()
    return jsonify({'mensaje': 'Recurso movilizado eliminado correctamente'})
