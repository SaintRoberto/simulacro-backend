from flask import request, jsonify
from recursos_inventario import recursos_inventario_bp
from models import db
from datetime import datetime, timezone


@recursos_inventario_bp.route('/api/recursos_inventario', methods=['GET'])
def get_recursos_inventario():
    """Listar recursos inventario
    ---
    tags:
      - Recursos Inventario
    responses:
      200:
        description: Lista de recursos inventario
        schema:
          type: array
          items:
            type: object
            properties:
              id: {type: integer}
              institucion_duena_id: {type: integer}
              recurso_tipo_id: {type: integer}
              coe_id: {type: integer}
              mesa_id: {type: integer}
              provincia_id: {type: integer}
              canton_id: {type: integer}
              parroquia_id: {type: integer}
              existencias: {type: integer}
              activo: {type: boolean}
              creador: {type: string}
              creacion: {type: string}
              modificador: {type: string}
              modificacion: {type: string}
    """
    result = db.session.execute(db.text("SELECT * FROM recursos_inventario"))
    items = []
    for row in result:
        items.append({
            'id': row.id,
            'institucion_duena_id': row.institucion_duena_id,
            'recurso_tipo_id': row.recurso_tipo_id,
            'coe_id': row.coe_id,
            'mesa_id': row.mesa_id,
            'provincia_id': row.provincia_id,
            'canton_id': row.canton_id,
            'parroquia_id': row.parroquia_id,
            'existencias': row.existencias,
            'activo': row.activo,
            'creador': row.creador,
            'creacion': row.creacion.isoformat() if row.creacion else None,
            'modificador': row.modificador,
            'modificacion': row.modificacion.isoformat() if row.modificacion else None
        })
    return jsonify(items)


@recursos_inventario_bp.route(
    '/api/recursos_inventario/recurso_grupo/<int:recurso_grupo_id>/coe/<int:coe_id>/mesa/<int:mesa_id>/',
    methods=['GET']
)
def get_recursos_inventario_by_recurso_grupo_by_coe_by_mesa(recurso_grupo_id, coe_id, mesa_id):
    """Obtener recursos inventario por grupo de recurso, COE y mesa
    ---
    tags:
      - Recursos Inventario
    parameters:
      - name: recurso_grupo_id
        in: path
        type: integer
        required: true
      - name: coe_id
        in: path
        type: integer
        required: true
      - name: mesa_id
        in: path
        type: integer
        required: true
    responses:
      200:
        description: Lista de recursos inventario por grupo de recurso, COE y mesa
        schema:
          type: array
          items:
            type: object
            properties:
              recurso_inventario_id: {type: integer}
              institucion_id: {type: integer}
              institucion_siglas: {type: string}
              recurso_tipo_id: {type: integer}
              recurso_nombre: {type: string}
              recurso_retorna: {type: boolean}
              existencias: {type: integer}
              movilizado: {type: integer}
              disponible: {type: integer}
    """
    query = db.text("""
        SELECT
            ri.id AS recurso_inventario_id,
            i.id AS institucion_id,
            i.siglas AS institucion_siglas,
            rt.id AS recurso_tipo_id,
            rt.nombre AS recurso_nombre,
            rt.retorna AS recurso_retorna,
            COALESCE(ri.existencias, 0) AS existencias,
            COALESCE(
                SUM(
                    CASE
                        WHEN COALESCE(rm.factor, 0) = -1 THEN COALESCE(rm.cantidad, 0)
                        ELSE 0
                    END
                ),
                0
            ) AS movilizado,
            COALESCE(ri.existencias, 0) -
            COALESCE(
                SUM(
                    CASE
                        WHEN COALESCE(rm.factor, 0) = -1 THEN COALESCE(rm.cantidad, 0)
                        ELSE 0
                    END
                ),
                0
            ) AS disponible
        FROM public.instituciones_coe_mesa icm
        INNER JOIN public.instituciones i
            ON icm.institucion_id = i.id
        CROSS JOIN public.recurso_tipos rt
        LEFT JOIN public.recursos_inventario ri
            ON ri.institucion_duena_id = i.id
           AND ri.recurso_tipo_id = rt.id
           AND ri.coe_id = icm.coe_id
           AND ri.mesa_id = icm.mesa_id
           AND COALESCE(ri.activo, true) = true
        LEFT JOIN public.recursos_movilizados rm
            ON rm.recurso_inventario_id = ri.id
           AND COALESCE(rm.activo, true) = true
        WHERE icm.coe_id = :coe_id
          AND icm.mesa_id = :mesa_id
          AND rt.recurso_grupo_id = :recurso_grupo_id
          AND COALESCE(icm.activo, true) = true
          AND COALESCE(i.activo, true) = true
          AND COALESCE(rt.activo, true) = true
        GROUP BY
            i.id, i.nombre, i.siglas,
            rt.id, rt.nombre, rt.descripcion, rt.retorna,
            ri.id, ri.existencias
        ORDER BY i.nombre, rt.nombre;
    """)
    result = db.session.execute(query, {
        'recurso_grupo_id': recurso_grupo_id,
        'coe_id': coe_id,
        'mesa_id': mesa_id
    })
    items = []
    for row in result:
        items.append({
            'recurso_inventario_id': row.recurso_inventario_id,
            'institucion_id': row.institucion_id,
            'institucion_siglas': row.institucion_siglas,
            'recurso_tipo_id': row.recurso_tipo_id,
            'recurso_nombre': row.recurso_nombre,
            'recurso_retorna': row.recurso_retorna,
            'existencias': row.existencias,
            'movilizado': row.movilizado,
            'disponible': row.disponible
        })
    return jsonify(items)


@recursos_inventario_bp.route('/api/recursos_inventario', methods=['POST'])
def create_recurso_inventario():
    """Crear recurso inventario
    ---
    tags:
      - Recursos Inventario
    consumes:
      - application/json
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          required: [institucion_duena_id, recurso_tipo_id, coe_id, mesa_id, provincia_id, canton_id, parroquia_id]
          properties:
            institucion_duena_id: {type: integer}
            recurso_tipo_id: {type: integer}
            coe_id: {type: integer}
            mesa_id: {type: integer}
            provincia_id: {type: integer}
            canton_id: {type: integer}
            parroquia_id: {type: integer}
            existencias: {type: integer}
            activo: {type: boolean}
            creador: {type: string}
            modificador: {type: string}
    responses:
      201:
        description: Recurso inventario creado
        schema:
          type: object
          properties:
            id: {type: integer}
            institucion_duena_id: {type: integer}
            recurso_tipo_id: {type: integer}
            coe_id: {type: integer}
            mesa_id: {type: integer}
            provincia_id: {type: integer}
            canton_id: {type: integer}
            parroquia_id: {type: integer}
            existencias: {type: integer}
            activo: {type: boolean}
            creador: {type: string}
            creacion: {type: string}
            modificador: {type: string}
            modificacion: {type: string}
    """
    data = request.get_json() or {}
    required_fields = [
        'institucion_duena_id', 'recurso_tipo_id', 'coe_id', 'mesa_id',
        'provincia_id', 'canton_id', 'parroquia_id'
    ]
    missing_fields = [field for field in required_fields if field not in data]
    if missing_fields:
        return jsonify({'error': f"Campos requeridos faltantes: {', '.join(missing_fields)}"}), 400

    now = datetime.now(timezone.utc)

    query = db.text("""
        INSERT INTO recursos_inventario (
            institucion_duena_id, recurso_tipo_id, coe_id, mesa_id,
            provincia_id, canton_id, parroquia_id, existencias,
            activo, creador, creacion, modificador, modificacion
        )
        VALUES (
            :institucion_duena_id, :recurso_tipo_id, :coe_id, :mesa_id,
            :provincia_id, :canton_id, :parroquia_id, :existencias,
            :activo, :creador, :creacion, :modificador, :modificacion
        )
        RETURNING id
    """)

    result = db.session.execute(query, {
        'institucion_duena_id': data['institucion_duena_id'],
        'recurso_tipo_id': data['recurso_tipo_id'],
        'coe_id': data['coe_id'],
        'mesa_id': data['mesa_id'],
        'provincia_id': data['provincia_id'],
        'canton_id': data['canton_id'],
        'parroquia_id': data['parroquia_id'],
        'existencias': data.get('existencias', 0),
        'activo': data.get('activo', True),
        'creador': data.get('creador', 'Sistema'),
        'creacion': now,
        'modificador': data.get('modificador', data.get('creador', 'Sistema')),
        'modificacion': now
    })

    row = result.fetchone()
    if row is None:
        db.session.rollback()
        return jsonify({'error': 'Failed to create recurso_inventario'}), 500

    item_id = row[0]
    db.session.commit()

    item = db.session.execute(
        db.text("SELECT * FROM recursos_inventario WHERE id = :id"),
        {'id': item_id}
    ).fetchone()

    if not item:
        return jsonify({'error': 'Recurso inventario no encontrado despues de crear'}), 404

    return jsonify({
        'id': item.id,
        'institucion_duena_id': item.institucion_duena_id,
        'recurso_tipo_id': item.recurso_tipo_id,
        'coe_id': item.coe_id,
        'mesa_id': item.mesa_id,
        'provincia_id': item.provincia_id,
        'canton_id': item.canton_id,
        'parroquia_id': item.parroquia_id,
        'existencias': item.existencias,
        'activo': item.activo,
        'creador': item.creador,
        'creacion': item.creacion.isoformat() if item.creacion else None,
        'modificador': item.modificador,
        'modificacion': item.modificacion.isoformat() if item.modificacion else None
    }), 201


@recursos_inventario_bp.route('/api/recursos_inventario/<int:id>', methods=['GET'])
def get_recurso_inventario(id):
    """Obtener recurso inventario por ID
    ---
    tags:
      - Recursos Inventario
    parameters:
      - name: id
        in: path
        type: integer
        required: true
    responses:
      200:
        description: Recurso inventario
      404:
        description: No encontrado
    """
    result = db.session.execute(
        db.text("SELECT * FROM recursos_inventario WHERE id = :id"),
        {'id': id}
    )
    item = result.fetchone()

    if not item:
        return jsonify({'error': 'Recurso inventario no encontrado'}), 404

    return jsonify({
        'id': item.id,
        'institucion_duena_id': item.institucion_duena_id,
        'recurso_tipo_id': item.recurso_tipo_id,
        'coe_id': item.coe_id,
        'mesa_id': item.mesa_id,
        'provincia_id': item.provincia_id,
        'canton_id': item.canton_id,
        'parroquia_id': item.parroquia_id,
        'existencias': item.existencias,
        'activo': item.activo,
        'creador': item.creador,
        'creacion': item.creacion.isoformat() if item.creacion else None,
        'modificador': item.modificador,
        'modificacion': item.modificacion.isoformat() if item.modificacion else None
    })


@recursos_inventario_bp.route('/api/recursos_inventario/<int:id>', methods=['PUT'])
def update_recurso_inventario(id):
    """Actualizar recurso inventario
    ---
    tags:
      - Recursos Inventario
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
            institucion_duena_id: {type: integer}
            recurso_tipo_id: {type: integer}
            coe_id: {type: integer}
            mesa_id: {type: integer}
            provincia_id: {type: integer}
            canton_id: {type: integer}
            parroquia_id: {type: integer}
            existencias: {type: integer}
            activo: {type: boolean}
            modificador: {type: string}
    responses:
      200:
        description: Recurso inventario actualizado
      404:
        description: No encontrado
    """
    data = request.get_json() or {}
    now = datetime.now(timezone.utc)

    update_fields = []
    params = {
        'id': id,
        'modificador': data.get('modificador', 'Sistema'),
        'modificacion': now
    }

    for field in [
        'institucion_duena_id', 'recurso_tipo_id', 'coe_id', 'mesa_id',
        'provincia_id', 'canton_id', 'parroquia_id', 'existencias', 'activo'
    ]:
        if field in data:
            update_fields.append(f"{field} = :{field}")
            params[field] = data[field]

    update_fields.append('modificador = :modificador')
    update_fields.append('modificacion = :modificacion')

    query = db.text(f"""
        UPDATE recursos_inventario
        SET {', '.join(update_fields)}
        WHERE id = :id
    """)

    result = db.session.execute(query, params)

    if getattr(result, 'rowcount', 0) == 0:
        return jsonify({'error': 'Recurso inventario no encontrado'}), 404

    db.session.commit()

    item = db.session.execute(
        db.text("SELECT * FROM recursos_inventario WHERE id = :id"),
        {'id': id}
    ).fetchone()

    if not item:
        return jsonify({'error': 'Recurso inventario no encontrado despues de actualizar'}), 404

    return jsonify({
        'id': item.id,
        'institucion_duena_id': item.institucion_duena_id,
        'recurso_tipo_id': item.recurso_tipo_id,
        'coe_id': item.coe_id,
        'mesa_id': item.mesa_id,
        'provincia_id': item.provincia_id,
        'canton_id': item.canton_id,
        'parroquia_id': item.parroquia_id,
        'existencias': item.existencias,
        'activo': item.activo,
        'creador': item.creador,
        'creacion': item.creacion.isoformat() if item.creacion else None,
        'modificador': item.modificador,
        'modificacion': item.modificacion.isoformat() if item.modificacion else None
    })


@recursos_inventario_bp.route('/api/recursos_inventario/<int:id>', methods=['DELETE'])
def delete_recurso_inventario(id):
    """Eliminar recurso inventario
    ---
    tags:
      - Recursos Inventario
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
        db.text("DELETE FROM recursos_inventario WHERE id = :id"),
        {'id': id}
    )

    if getattr(result, 'rowcount', 0) == 0:
        return jsonify({'error': 'Recurso inventario no encontrado'}), 404

    db.session.commit()
    return jsonify({'mensaje': 'Recurso inventario eliminado correctamente'})
