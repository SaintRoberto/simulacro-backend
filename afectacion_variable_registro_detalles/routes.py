from flask import request, jsonify
from afectacion_variable_registro_detalles import afectacion_variable_registro_detalles_bp
from models import db
from datetime import datetime, timezone

@afectacion_variable_registro_detalles_bp.route('/api/afectacion_variable_registro_detalles', methods=['GET'])
def get_afectacion_variable_registro_detalles():
    """Listar afectacion_variable_registro_detalles
    ---
    tags:
      - Afectacion Variable Registro Detalles
    responses:
        200:
          description: Lista de afectacion_variable_registro_detalles
          schema:
            type: array
            items:
              type: object
              properties:
                id: {type: integer}
                afectacion_variable_registro_id: {type: integer}
                infraestructura_id: {type: integer}
                costo: {type: integer}
                activo: {type: boolean}
                creador: {type: string}
                creacion: {type: string}
                modificador: {type: string}
                modificacion: {type: string}
    """
    result = db.session.execute(db.text("SELECT * FROM afectacion_variable_registro_detalles"))
    afectacion_variable_registro_detalles = []
    for row in result:
        afectacion_variable_registro_detalles.append({  # type: ignore
            'id': row.id,
            'afectacion_variable_registro_id': row.afectacion_variable_registro_id,  # type: ignore[attr-defined]
            'infraestructura_id': row.infraestructura_id,  # type: ignore[attr-defined]
            'costo': row.costo,
            'activo': row.activo,
            'creador': row.creador,
            'creacion': row.creacion.isoformat() if row.creacion else None,
            'modificador': row.modificador,
            'modificacion': row.modificacion.isoformat() if row.modificacion else None
        })
    return jsonify(afectacion_variable_registro_detalles)

@afectacion_variable_registro_detalles_bp.route('/api/afectacion_variable_registro_detalles/parroquia/<int:parroquia_id>/variable/<int:afectacion_variable_id>', methods=['GET'])
def get_afectacion_variable_registro_detalles_by_variable_by_parroquia(parroquia_id, afectacion_variable_id):
    """Obtener afectacion_variable_registro_detalles por parroquia y variable
    ---
    tags:
      - Afectacion Variable Registro Detalles
    parameters:
      - name: parroquia_id
        in: path
        type: integer
        required: true
      - name: afectacion_variable_id
        in: path
        type: integer
        required: true
    responses:
        200:
          description: Lista de detalles
          schema:
            type: array
            items:
              type: object
              properties:
                registro_id: {type: integer}
                registro_detalle_id: {type: integer}
                infraestructura_id: {type: integer}
                infraestructura_tipo_id: {type: integer}
                nombre: {type: string}
    """
    query = db.text("""
        SELECT r.id registro_id, d.id registro_detalle_id, i.id infraestructura_id, i.infraestructura_tipo_id, i.nombre
        FROM public.afectacion_variable_registro_detalles d
        INNER JOIN public.afectacion_variable_registros r ON d.afectacion_variable_registro_id = r.id
        INNER JOIN infraestructuras i ON d.infraestructura_id = i.id
        WHERE r.parroquia_id = :parroquia_id AND r.afectacion_variable_id = :afectacion_variable_id
        ORDER BY d.id ASC
    """)
    result = db.session.execute(query, {'parroquia_id': parroquia_id, 'afectacion_variable_id': afectacion_variable_id})
    detalles = []
    for row in result:
        detalles.append({  # type: ignore
            'registro_id': row.registro_id,
            'registro_detalle_id': row.registro_detalle_id,
            'infraestructura_id': row.infraestructura_id,
            'infraestructura_tipo_id': row.infraestructura_tipo_id,
            'nombre': row.nombre
        })
    return jsonify(detalles)

@afectacion_variable_registro_detalles_bp.route('/api/afectacion_variable_registro_detalles/emergencia/<int:emergencia_id>/variable/<int:afectacion_variable_id>/parroquia/<int:parroquia_id>', methods=['GET'])
def get_afectacion_variable_registro_detalles_by_emergencia_by_variable_by_parroquia(emergencia_id, afectacion_variable_id, parroquia_id):
    """Obtener afectacion_variable_registro_detalles por emergencia, variable y parroquia
    ---
    tags:
      - Afectacion Variable Registro Detalles
    parameters:
      - name: emergencia_id
        in: path
        type: integer
        required: true
      - name: afectacion_variable_id
        in: path
        type: integer
        required: true
      - name: parroquia_id
        in: path
        type: integer
        required: true
    responses:
        200:
          description: Lista de infraestructuras con estado de registro
          schema:
            type: array
            items:
              type: object
              properties:
                id: {type: integer}
                nombre: {type: string}
                registrada: {type: boolean}
    """
    query = db.text("""
      WITH registradas_sel AS (
        -- Infraestructuras registradas en la VARIABLE SELECCIONADA (para la misma emergencia)
        SELECT DISTINCT ON (d.infraestructura_id)
              d.infraestructura_id,
              r.id AS registro_id,
              d.id AS detalle_id
        FROM afectacion_variable_registros r
        JOIN afectacion_variable_registro_detalles d
          ON d.afectacion_variable_registro_id = r.id
        WHERE r.parroquia_id = :parroquia_id
          AND r.emergencia_id = :emergencia_id
          AND r.afectacion_variable_id = :afectacion_variable_id
        ORDER BY d.infraestructura_id, d.id DESC
      ),
      comprometidas_otras AS (
        -- Infraestructuras comprometidas en OTRAS variables (misma emergencia),
        -- que debemos excluir si NO pertenecen a la variable seleccionada
        SELECT DISTINCT d.infraestructura_id
        FROM afectacion_variable_registros r
        JOIN afectacion_variable_registro_detalles d
          ON d.afectacion_variable_registro_id = r.id
        WHERE r.parroquia_id = :parroquia_id
          AND r.emergencia_id = :emergencia_id
          AND r.afectacion_variable_id <> :afectacion_variable_id
      )
      SELECT
        i.id infraestructura_id,
        i.nombre,
        (rs.infraestructura_id IS NOT NULL) AS registrada, -- true si ya está en la variable seleccionada
        rs.registro_id  AS afectacion_variable_registro_id,
        rs.detalle_id   AS afectacion_variable_registro_detalle_id
      FROM infraestructuras i
      LEFT JOIN registradas_sel   rs ON rs.infraestructura_id = i.id
      LEFT JOIN comprometidas_otras co ON co.infraestructura_id = i.id
      WHERE i.parroquia_id = :parroquia_id
        -- Quita el comentario si quieres filtrar por tipo (ej. escuelas):
        -- AND i.infraestructura_tipo_id = $4
        -- Regla de selección:
        AND (co.infraestructura_id IS NULL OR rs.infraestructura_id IS NOT NULL)
      ORDER BY registrada DESC, i.nombre;
    """)
    result = db.session.execute(query, {'emergencia_id': emergencia_id, 'afectacion_variable_id': afectacion_variable_id, 'parroquia_id': parroquia_id})
    detalles = []
    for row in result:
        detalles.append({  # type: ignore
            'infraestructura_id': row.infraestructura_id,
            'nombre': row.nombre,
            'registrada': row.registrada,
            'afectacion_variable_registro_id': row.afectacion_variable_registro_id,
            'afectacion_variable_registro_detalle_id': row.afectacion_variable_registro_detalle_id 
        })
    return jsonify(detalles)

@afectacion_variable_registro_detalles_bp.route('/api/afectacion_variable_registro_detalles', methods=['POST'])
def create_afectacion_variable_registro_detalle():
    """Crear afectacion_variable_registro_detalle
    ---
    tags:
      - Afectacion Variable Registro Detalles
    consumes:
      - application/json
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          required: [afectacion_variable_registro_id, infraestructura_id, costo]
          properties:
            afectacion_variable_registro_id: {type: integer}
            infraestructura_id: {type: integer}
            costo: {type: integer}
            activo: {type: boolean}
            creador: {type: string}
    responses:
      201:
        description: Afectacion variable registro detalle creado
        schema:
          type: object
          properties:
            id: {type: integer}
            afectacion_variable_registro_id: {type: integer}
            infraestructura_id: {type: integer}
            costo: {type: integer}
            activo: {type: boolean}
            creador: {type: string}
            creacion: {type: string}
            modificador: {type: string}
            modificacion: {type: string}
    """
    data = request.get_json()
    now = datetime.now(timezone.utc)

    query = db.text("""
        INSERT INTO afectacion_variable_registro_detalles (afectacion_variable_registro_id, infraestructura_id, costo, activo, creador, creacion, modificador, modificacion)
        VALUES (:afectacion_variable_registro_id, :infraestructura_id, :costo, :activo, :creador, :creacion, :modificador, :modificacion)
        RETURNING id
    """)

    result = db.session.execute(query, {
        'afectacion_variable_registro_id': data['afectacion_variable_registro_id'],
        'infraestructura_id': data['infraestructura_id'],
        'costo': data['costo'],
        'activo': data.get('activo', True),
        'creador': data.get('creador', 'Sistema'),
        'creacion': now,
        'modificador': data.get('creador', 'Sistema'),
        'modificacion': now
    })

    row = result.fetchone()
    if row is None:
        db.session.rollback()
        return jsonify({'error': 'Failed to create afectacion_variable_registro_detalle'}), 500
    afectacion_variable_registro_detalle_id = row[0]
    db.session.commit()

    afectacion_variable_registro_detalle = db.session.execute(
        db.text("SELECT * FROM afectacion_variable_registro_detalles WHERE id = :id"),
        {'id': afectacion_variable_registro_detalle_id}
    ).fetchone()

    if not afectacion_variable_registro_detalle:
        return jsonify({'error': 'Afectacion variable registro detalle not found after creation'}), 404

    return jsonify({  # type: ignore
        'id': afectacion_variable_registro_detalle.id,
        'afectacion_variable_registro_id': afectacion_variable_registro_detalle.afectacion_variable_registro_id,
        'infraestructura_id': afectacion_variable_registro_detalle.infraestructura_id,
        'costo': afectacion_variable_registro_detalle.costo,
        'activo': afectacion_variable_registro_detalle.activo,
        'creador': afectacion_variable_registro_detalle.creador,
        'creacion': afectacion_variable_registro_detalle.creacion.isoformat() if afectacion_variable_registro_detalle.creacion else None,
        'modificador': afectacion_variable_registro_detalle.modificador,
        'modificacion': afectacion_variable_registro_detalle.modificacion.isoformat() if afectacion_variable_registro_detalle.modificacion else None
    }), 201

@afectacion_variable_registro_detalles_bp.route('/api/afectacion_variable_registro_detalles/<int:id>', methods=['GET'])
def get_afectacion_variable_registro_detalle(id):
    """Obtener afectacion_variable_registro_detalle por ID
    ---
    tags:
      - Afectacion Variable Registro Detalles
    parameters:
      - name: id
        in: path
        type: integer
        required: true
    responses:
      200:
        description: Afectacion variable registro detalle
      404:
        description: No encontrado
    """
    result = db.session.execute(
        db.text("SELECT * FROM afectacion_variable_registro_detalles WHERE id = :id"),
        {'id': id}
    )
    afectacion_variable_registro_detalle = result.fetchone()

    if not afectacion_variable_registro_detalle:
        return jsonify({'error': 'Afectacion variable registro detalle no encontrado'}), 404

    return jsonify({
        'id': afectacion_variable_registro_detalle.id,
        'afectacion_variable_registro_id': afectacion_variable_registro_detalle.afectacion_variable_registro_id,
        'infraestructura_id': afectacion_variable_registro_detalle.infraestructura_id,
        'costo': afectacion_variable_registro_detalle.costo,
        'activo': afectacion_variable_registro_detalle.activo,
        'creador': afectacion_variable_registro_detalle.creador,
        'creacion': afectacion_variable_registro_detalle.creacion.isoformat() if afectacion_variable_registro_detalle.creacion else None,
        'modificador': afectacion_variable_registro_detalle.modificador,
        'modificacion': afectacion_variable_registro_detalle.modificacion.isoformat() if afectacion_variable_registro_detalle.modificacion else None
    })

@afectacion_variable_registro_detalles_bp.route('/api/afectacion_variable_registro_detalles/<int:id>', methods=['PUT'])
def update_afectacion_variable_registro_detalle(id):
    """Actualizar afectacion_variable_registro_detalle
    ---
    tags:
      - Afectacion Variable Registro Detalles
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
            afectacion_variable_registro_id: {type: integer}
            infraestructura_id: {type: integer}
            costo: {type: integer}
            activo: {type: boolean}
    responses:
      200:
        description: Afectacion variable registro detalle actualizado
      404:
        description: No encontrado
    """
    data = request.get_json()
    now = datetime.now(timezone.utc)

    query = db.text("""
        UPDATE afectacion_variable_registro_detalles
        SET afectacion_variable_registro_id = :afectacion_variable_registro_id,
            infraestructura_id = :infraestructura_id,
            costo = :costo,
            activo = :activo,
            modificador = :modificador,
            modificacion = :modificacion
        WHERE id = :id
    """)

    result = db.session.execute(query, {
        'id': id,
        'afectacion_variable_registro_id': data.get('afectacion_variable_registro_id'),
        'infraestructura_id': data.get('infraestructura_id'),
        'costo': data.get('costo'),
        'activo': data.get('activo'),
        'modificador': data.get('modificador', 'Sistema'),
        'modificacion': now
    })

    if result.rowcount == 0:  # type: ignore[attr-defined]
        return jsonify({'error': 'Afectacion variable registro detalle no encontrado'}), 404

    db.session.commit()

    afectacion_variable_registro_detalle = db.session.execute(
        db.text("SELECT * FROM afectacion_variable_registro_detalles WHERE id = :id"),
        {'id': id}
    ).fetchone()

    if not afectacion_variable_registro_detalle:
        return jsonify({'error': 'Afectacion variable registro detalle not found after update'}), 404

    return jsonify({  # type: ignore
        'id': afectacion_variable_registro_detalle.id,
        'afectacion_variable_registro_id': afectacion_variable_registro_detalle.afectacion_variable_registro_id,
        'infraestructura_id': afectacion_variable_registro_detalle.infraestructura_id,
        'costo': afectacion_variable_registro_detalle.costo,
        'activo': afectacion_variable_registro_detalle.activo,
        'creador': afectacion_variable_registro_detalle.creador,
        'creacion': afectacion_variable_registro_detalle.creacion.isoformat() if afectacion_variable_registro_detalle.creacion else None,
        'modificador': afectacion_variable_registro_detalle.modificador,
        'modificacion': afectacion_variable_registro_detalle.modificacion.isoformat() if afectacion_variable_registro_detalle.modificacion else None
    })

@afectacion_variable_registro_detalles_bp.route('/api/afectacion_variable_registro_detalles/<int:id>', methods=['DELETE'])
def delete_afectacion_variable_registro_detalle(id):
    """Eliminar afectacion_variable_registro_detalle
    ---
    tags:
      - Afectacion Variable Registro Detalles
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
        db.text("DELETE FROM afectacion_variable_registro_detalles WHERE id = :id"),
        {'id': id}
    )

    if result.rowcount == 0:  # type: ignore[attr-defined]
        return jsonify({'error': 'Afectacion variable registro detalle no encontrado'}), 404

    db.session.commit()
    return jsonify({'mensaje': 'Afectacion variable registro detalle eliminado correctamente'})