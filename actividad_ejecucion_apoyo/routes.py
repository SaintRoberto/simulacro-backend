from flask import request, jsonify
from actividad_ejecucion_apoyo import actividad_ejecucion_apoyo_bp
from models import db
from datetime import datetime, timezone


@actividad_ejecucion_apoyo_bp.route('/api/actividad_ejecucion_apoyo', methods=['GET'])
def get_actividad_ejecucion_apoyo():
    """Listar actividad_ejecucion_apoyo
    ---
    tags:
      - Actividad Ejecucion Apoyo
    responses:
      200:
        description: Lista de actividad_ejecucion_apoyo
        schema:
          type: array
          items:
            type: object
            properties:
              id: {type: integer}
              actividad_ejecucion_id: {type: integer}
              institucion_id: {type: integer}
              activo: {type: boolean}
              creador: {type: string}
              creacion: {type: string}
              modificador: {type: string}
              modificacion: {type: string}
    """
    result = db.session.execute(db.text("SELECT * FROM actividad_ejecucion_apoyo"))
    items = []
    for row in result:
        items.append({  # type: ignore
            'id': row.id,
            'actividad_ejecucion_id': row.actividad_ejecucion_id,
            'institucion_id': row.institucion_id,
            'activo': row.activo,
            'creador': row.creador,
            'creacion': row.creacion.isoformat() if row.creacion else None,
            'modificador': row.modificador,
            'modificacion': row.modificacion.isoformat() if row.modificacion else None,
        })
    return jsonify(items)


@actividad_ejecucion_apoyo_bp.route('/api/actividad_ejecucion_apoyo', methods=['POST'])
def create_actividad_ejecucion_apoyo():
    """Crear actividad_ejecucion_apoyo
    ---
    tags:
      - Actividad Ejecucion Apoyo
    consumes:
      - application/json
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          required: [actividad_ejecucion_id, institucion_id]
          properties:
            actividad_ejecucion_id: {type: integer}
            institucion_id: {type: integer}
            activo: {type: boolean}
            creador: {type: string}
    responses:
      201:
        description: Registro de apoyo creado
        schema:
          type: object
          properties:
            id: {type: integer}
            actividad_ejecucion_id: {type: integer}
            institucion_id: {type: integer}
            activo: {type: boolean}
            creador: {type: string}
            creacion: {type: string}
            modificador: {type: string}
            modificacion: {type: string}
    """
    data = request.get_json() or {}
    if not data:
        return jsonify({'error': 'Request body required'}), 400

    now = datetime.now(timezone.utc)

    actividad_ejecucion_id = data['actividad_ejecucion_id']
    institucion_id = data['institucion_id']
    activo = data.get('activo', True)
    creador = data.get('creador', 'Sistema')
    modificador = data.get('modificador', creador)

    query = db.text("""
        INSERT INTO actividad_ejecucion_apoyo (
            actividad_ejecucion_id, institucion_id,
            activo, creador, creacion, modificador, modificacion
        )
        VALUES (
            :actividad_ejecucion_id, :institucion_id,
            :activo, :creador, :creacion, :modificador, :modificacion
        )
        RETURNING id
    """)

    params = {
        'actividad_ejecucion_id': actividad_ejecucion_id,
        'institucion_id': institucion_id,
        'activo': activo,
        'creador': creador,
        'creacion': now,
        'modificador': modificador,
        'modificacion': now,
    }

    result = db.session.execute(query, params)
    row = result.fetchone()
    if row is None:
        db.session.rollback()
        return jsonify({'error': 'Failed to create actividad_ejecucion_apoyo'}), 500

    new_id = row[0]
    db.session.commit()

    apoyo = db.session.execute(
        db.text("SELECT * FROM actividad_ejecucion_apoyo WHERE id = :id"),
        {'id': new_id},
    ).fetchone()

    if not apoyo:
        return jsonify({'error': 'actividad_ejecucion_apoyo not found after creation'}), 404

    return jsonify({  # type: ignore
        'id': apoyo.id,
        'actividad_ejecucion_id': apoyo.actividad_ejecucion_id,
        'institucion_id': apoyo.institucion_id,
        'activo': apoyo.activo,
        'creador': apoyo.creador,
        'creacion': apoyo.creacion.isoformat() if apoyo.creacion else None,
        'modificador': apoyo.modificador,
        'modificacion': apoyo.modificacion.isoformat() if apoyo.modificacion else None,
    }), 201


@actividad_ejecucion_apoyo_bp.route('/api/actividad_ejecucion_apoyo/<int:id>', methods=['GET'])
def get_actividad_ejecucion_apoyo_by_id(id):
    """Obtener actividad_ejecucion_apoyo por ID
    ---
    tags:
      - Actividad Ejecucion Apoyo
    parameters:
      - name: id
        in: path
        type: integer
        required: true
    responses:
      200:
        description: Registro de apoyo
      404:
        description: No encontrado
    """
    result = db.session.execute(
        db.text("SELECT * FROM actividad_ejecucion_apoyo WHERE id = :id"),
        {'id': id},
    )
    row = result.fetchone()

    if not row:
        return jsonify({'error': 'actividad_ejecucion_apoyo no encontrado'}), 404

    return jsonify({
        'id': row.id,
        'actividad_ejecucion_id': row.actividad_ejecucion_id,
        'institucion_id': row.institucion_id,
        'activo': row.activo,
        'creador': row.creador,
        'creacion': row.creacion.isoformat() if row.creacion else None,
        'modificador': row.modificador,
        'modificacion': row.modificacion.isoformat() if row.modificacion else None,
    })


@actividad_ejecucion_apoyo_bp.route('/api/actividad_ejecucion_apoyo/actividad_ejecucion/<int:actividad_ejecucion_id>', methods=['GET'])
def get_actividades_ejecucion_apoyo_by_actividad_ejecucion(actividad_ejecucion_id):
    """Obtener actividades de apoyo por ID de actividad de ejecución
    ---
    tags:
      - Actividad Ejecucion Apoyo
    parameters:
      - name: actividad_ejecucion_id
        in: path
        type: integer
        required: true
        description: ID de la actividad de ejecución
    responses:
      200:
        description: Lista de actividades de apoyo para la actividad de ejecución
        schema:
          type: array
          items:
            type: object
            properties:
              id: {type: integer}
              actividad_ejecucion_id: {type: integer}
              institucion_id: {type: integer}
              institucion_nombre: {type: string}
              institucion_siglas: {type: string}
              activo: {type: boolean}
              creador: {type: string}
              creacion: {type: string}
              modificador: {type: string}
              modificacion: {type: string}
    """
    query = db.text("""
        SELECT aea.*, 
               i.nombre as institucion_nombre,
               i.siglas as institucion_siglas
        FROM actividad_ejecucion_apoyo aea
        LEFT JOIN instituciones i ON aea.institucion_id = i.id
        WHERE aea.actividad_ejecucion_id = :actividad_ejecucion_id
        AND aea.activo = true
    """)
    
    result = db.session.execute(query, {'actividad_ejecucion_id': actividad_ejecucion_id})
    items = []
    for row in result:
        item = {
            'id': row.id,
            'actividad_ejecucion_id': row.actividad_ejecucion_id,
            'institucion_id': row.institucion_id,
            'institucion_nombre': row.institucion_nombre,
            'institucion_siglas': row.institucion_siglas,
            'activo': row.activo,
            'creador': row.creador,
            'modificador': row.modificador,
        }
        # Format datetime fields
        if hasattr(row, 'creacion') and row.creacion:
            item['creacion'] = row.creacion.isoformat()
        if hasattr(row, 'modificacion') and row.modificacion:
            item['modificacion'] = row.modificacion.isoformat()
        items.append(item)
    
    return jsonify(items)


@actividad_ejecucion_apoyo_bp.route('/api/actividad_ejecucion_apoyo/<int:id>', methods=['PUT'])
def update_actividad_ejecucion_apoyo(id):
    """Actualizar actividad_ejecucion_apoyo
    ---
    tags:
      - Actividad Ejecucion Apoyo
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
            actividad_ejecucion_id: {type: integer}
            institucion_id: {type: integer}
            activo: {type: boolean}
            modificador: {type: string}
    responses:
      200:
        description: Registro de apoyo actualizado
      404:
        description: No encontrado
    """
    data = request.get_json() or {}
    if not data:
        return jsonify({'error': 'Request body required'}), 400

    now = datetime.now(timezone.utc)
    data['modificador'] = data.get('modificador', 'Sistema')
    data['modificacion'] = now

    allowed = {
        'actividad_ejecucion_id',
        'institucion_id',
        'activo',
        'modificador',
        'modificacion',
    }

    set_parts = []
    params = {'id': id}
    for k, v in data.items():
        if k in allowed:
            set_parts.append(f"{k} = :{k}")
            params[k] = v

    if not set_parts:
        return jsonify({'error': 'No updatable fields provided'}), 400

    set_sql = ', '.join(set_parts)
    query = db.text(f"UPDATE actividad_ejecucion_apoyo SET {set_sql} WHERE id = :id")
    result = db.session.execute(query, params)

    if getattr(result, 'rowcount', 0) == 0:  # type: ignore
        return jsonify({'error': 'actividad_ejecucion_apoyo no encontrado'}), 404

    db.session.commit()

    row = db.session.execute(
        db.text("SELECT * FROM actividad_ejecucion_apoyo WHERE id = :id"),
        {'id': id},
    ).fetchone()

    if not row:
        return jsonify({'error': 'actividad_ejecucion_apoyo not found after update'}), 404

    return jsonify({  # type: ignore
        'id': row.id,
        'actividad_ejecucion_id': row.actividad_ejecucion_id,
        'institucion_id': row.institucion_id,
        'activo': row.activo,
        'creador': row.creador,
        'creacion': row.creacion.isoformat() if row.creacion else None,
        'modificador': row.modificador,
        'modificacion': row.modificacion.isoformat() if row.modificacion else None,
    })


@actividad_ejecucion_apoyo_bp.route('/api/actividad_ejecucion_apoyo/<int:id>', methods=['DELETE'])
def delete_actividad_ejecucion_apoyo(id):
    """Eliminar actividad_ejecucion_apoyo
    ---
    tags:
      - Actividad Ejecucion Apoyo
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
        db.text("DELETE FROM actividad_ejecucion_apoyo WHERE id = :id"),
        {'id': id},
    )

    if getattr(result, 'rowcount', 0) == 0:  # type: ignore
        return jsonify({'error': 'actividad_ejecucion_apoyo no encontrado'}), 404

    db.session.commit()
    return jsonify({'mensaje': 'actividad_ejecucion_apoyo eliminado correctamente'})
