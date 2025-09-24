from flask import request, jsonify, Blueprint
from models import db
from datetime import datetime, timezone

afectacion_variable_registros_bp = Blueprint('afectacion_variable_registros', __name__)

@afectacion_variable_registros_bp.route('/api/afectacion_variable_registros', methods=['GET'])
def get_afectacion_variable_registros():
    """Retrieve all afectacion_variable_registros."""
    """Listar afectacion_variable_registros
    ---
    tags:
      - Afectacion Variable Registros
    responses:
        200:
          description: Lista de registros
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
                afectacion_variable_id: {type: integer}
                cantidad: {type: integer}
                costo: {type: integer}
                activo: {type: boolean}
                creador: {type: string}
                creacion: {type: string}
                modificador: {type: string}
                modificacion: {type: string}
    """
    result = db.session.execute(db.text("SELECT * FROM afectacion_variable_registros"))
    registros = []
    for row in result:
        registros.append({  # type: ignore
            'id': row.id,
            'emergencia_id': row.emergencia_id,
            'provincia_id': row.provincia_id,
            'canton_id': row.canton_id,
            'parroquia_id': row.parroquia_id,
            'afectacion_variable_id': row.afectacion_variable_id,
            'cantidad': row.cantidad,
            'costo': row.costo,
            'activo': row.activo,
            'creador': row.creador,
            'creacion': row.creacion.isoformat() if row.creacion else None,
            'modificador': row.modificador,
            'modificacion': row.modificacion.isoformat() if row.modificacion else None
        })
    return jsonify(registros)

@afectacion_variable_registros_bp.route('/api/afectaciones_registros/emergencia/<int:emergencia_id>/canton/<int:canton_id>/mesa_grupo/<int:mesa_grupo_id>/', methods=['GET'])
def get_data_afectaciones_registro_by_canton(emergencia_id, canton_id, mesa_grupo_id):
    """Obtener data afectaciones registro por canton y mesa_grupo
    ---
    tags:
      - Afectacion Variable Registros
    parameters:
      - name: emergencia_id
        in: path
        type: integer
        required: true
      - name: canton_id
        in: path
        type: integer
        required: true
      - name: mesa_grupo_id
        in: path
        type: integer
        required: true
    responses:
        200:
          description: Lista de registros
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
                afectacion_variable_id: {type: integer}
                variable_nombre: {type: string}
                requiere_gis: {type: boolean}
                cantidad: {type: integer}
                costo: {type: integer}
                activo: {type: boolean}
                creador: {type: string}
                creacion: {type: string}
                modificador: {type: string}
                modificacion: {type: string}
    """
    query = db.text("""
        SELECT p.id as parroquia_id, p.nombre as parroquia_nombre,
               v.id as afectacion_variable_id, v.nombre as variable_nombre, v.requiere_gis,
               COALESCE(r.cantidad, 0) as cantidad, COALESCE(r.costo, 0) as costo
        FROM parroquias p        
        CROSS JOIN afectacion_variables v
        LEFT JOIN afectacion_variable_registros r ON r.parroquia_id = p.id AND r.afectacion_variable_id = v.id  AND r.emergencia_id = :emergencia_id
        INNER JOIN emergencia_parroquias x ON p.id = x.parroquia_id
        WHERE p.canton_id = :canton_id AND v.mesa_grupo_id = :mesa_grupo_id
        ORDER BY p.id, v.id
    """)
    result = db.session.execute(query, {'emergencia_id': emergencia_id, 'canton_id': canton_id, 'mesa_grupo_id': mesa_grupo_id})
    registros = []
    for row in result:
        registros.append({  # type: ignore
            'parroquia_id': row.parroquia_id,
            'parroquia_nombre': row.parroquia_nombre,
            'afectacion_variable_id': row.afectacion_variable_id,
            'variable_nombre': row.variable_nombre,
            'requiere_gis': row.requiere_gis,
            'cantidad': row.cantidad,
            'costo': row.costo
        })
    return jsonify(registros)

@afectacion_variable_registros_bp.route('/api/afectacion_variable_registros/parroquia/<int:parroquia_id>/emergencia/<int:emergencia_id>/mesa_grupo/<int:mesa_grupo_id>', methods=['GET'])
def get_data_afectaciones_registro_by_parroquia(parroquia_id, emergencia_id, mesa_grupo_id):
    """Obtener data afectaciones registro por parroquia
    ---
    tags:
      - Afectacion Variable Registros
    parameters:
      - name: parroquia_id
        in: path
        type: integer
        required: true
      - name: emergencia_id
        in: path
        type: integer
        required: true
      - name: mesa_grupo_id
        in: path
        type: integer
        required: true
    responses:
        200:
          description: Lista de registros
          schema:
            type: array
            items:
              type: object
              properties:
                parroquia_id: {type: integer}
                parroquia_nombre: {type: string}
                afectacion_variable_id: {type: integer}
                variable_nombre: {type: string}
                requiere_gis: {type: boolean}
                cantidad: {type: integer}
                costo: {type: integer}
    """
    query = db.text("""
        SELECT p.id as parroquia_id, p.nombre as parroquia_nombre,
               v.id as afectacion_variable_id, v.nombre as variable_nombre, v.requiere_gis,
               COALESCE(r.cantidad, 0) as cantidad, COALESCE(r.costo, 0) as costo
        FROM parroquias p
        CROSS JOIN afectacion_variables v
        LEFT JOIN afectacion_variable_registros r ON r.parroquia_id = p.id AND r.afectacion_variable_id = v.id AND r.emergencia_id = :emergencia_id
        INNER JOIN emergencia_parroquias x ON p.id = x.parroquia_id
        WHERE p.id = :parroquia_id AND v.mesa_grupo_id = :mesa_grupo_id
        ORDER BY p.id, v.id
    """)
    result = db.session.execute(query, {'parroquia_id': parroquia_id, 'emergencia_id': emergencia_id, 'mesa_grupo_id': mesa_grupo_id})
    registros = []
    for row in result:
        registros.append({  # type: ignore
            'parroquia_id': row.parroquia_id,
            'parroquia_nombre': row.parroquia_nombre,
            'afectacion_variable_id': row.afectacion_variable_id,
            'variable_nombre': row.variable_nombre,
            'requiere_gis': row.requiere_gis,
            'cantidad': row.cantidad,
            'costo': row.costo
        })
    return jsonify(registros)

@afectacion_variable_registros_bp.route('/api/afectacion_variable_registros', methods=['POST'])
def create_afectacion_variable_registro():
    """Crear afectacion_variable_registro
    ---
    tags:
      - Afectacion Variable Registros
    consumes:
      - application/json
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          required: [emergencia_id, provincia_id, canton_id, parroquia_id, afectacion_variable_id, cantidad, costo]
          properties:
            emergencia_id: {type: integer}
            provincia_id: {type: integer}
            canton_id: {type: integer}
            parroquia_id: {type: integer}
            afectacion_variable_id: {type: integer}
            cantidad: {type: integer}
            costo: {type: integer}
            activo: {type: boolean}
            creador: {type: string}
    responses:
      201:
        description: Registro creado
        schema:
          type: object
          properties:
            id: {type: integer}
            emergencia_id: {type: integer}
            provincia_id: {type: integer}
            canton_id: {type: integer}
            parroquia_id: {type: integer}
            afectacion_variable_id: {type: integer}
            cantidad: {type: integer}
            costo: {type: integer}
            activo: {type: boolean}
            creador: {type: string}
            creacion: {type: string}
            modificador: {type: string}
            modificacion: {type: string}
    """
    data = request.get_json()
    required_fields = ['emergencia_id', 'provincia_id', 'canton_id', 'parroquia_id', 'afectacion_variable_id', 'cantidad', 'costo']
    for field in required_fields:
        if field not in data:
            return jsonify({'error': f'{field} is required'}), 400
    now = datetime.now(timezone.utc)

    query = db.text("""
        INSERT INTO afectacion_variable_registros (
            emergencia_id, provincia_id, canton_id, parroquia_id, afectacion_variable_id,
            cantidad, costo, activo, creador, creacion, modificador, modificacion
        )
        VALUES (
            :emergencia_id, :provincia_id, :canton_id, :parroquia_id, :afectacion_variable_id,
            :cantidad, :costo, :activo, :creador, :creacion, :modificador, :modificacion
        )
        RETURNING id
    """)

    result = db.session.execute(query, {
        'emergencia_id': data['emergencia_id'],
        'provincia_id': data['provincia_id'],
        'canton_id': data['canton_id'],
        'parroquia_id': data['parroquia_id'],
        'afectacion_variable_id': data['afectacion_variable_id'],
        'cantidad': data['cantidad'],
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
        return jsonify({'error': 'Failed to create registro'}), 500
    registro_id = row[0]
    db.session.commit()
    
    registro = db.session.execute(
        db.text("SELECT * FROM afectacion_variable_registros WHERE id = :id"),
        {'id': registro_id}
    ).fetchone()

    if not registro:
        return jsonify({'error': 'Registro no encontrado'}), 404

    return jsonify({  # type: ignore
        'id': registro.id,
        'emergencia_id': registro.emergencia_id,
        'provincia_id': registro.provincia_id,
        'canton_id': registro.canton_id,
        'parroquia_id': registro.parroquia_id,
        'afectacion_variable_id': registro.afectacion_variable_id,
        'cantidad': registro.cantidad,
        'costo': registro.costo,
        'activo': registro.activo,
        'creador': registro.creador,
        'creacion': registro.creacion.isoformat() if registro.creacion else None,
        'modificador': registro.modificador,
        'modificacion': registro.modificacion.isoformat() if registro.modificacion else None
    }), 201

@afectacion_variable_registros_bp.route('/api/afectacion_variable_registros/<int:id>', methods=['GET'])
def get_afectacion_variable_registro(id):
    """Obtener afectacion_variable_registro por ID
    ---
    tags:
      - Afectacion Variable Registros
    parameters:
      - name: id
        in: path
        type: integer
        required: true
    responses:
      200:
        description: Registro
      404:
        description: No encontrado
    """
    result = db.session.execute(
        db.text("SELECT * FROM afectacion_variable_registros WHERE id = :id"), 
        {'id': id}
    )
    registro = result.fetchone()
    
    if not registro:
        return jsonify({'error': 'Registro no encontrado'}), 404
    
    return jsonify({  # type: ignore
        'id': registro.id,
        'emergencia_id': registro.emergencia_id,
        'provincia_id': registro.provincia_id,
        'canton_id': registro.canton_id,
        'parroquia_id': registro.parroquia_id,
        'afectacion_variable_id': registro.afectacion_variable_id,
        'cantidad': registro.cantidad,
        'costo': registro.costo,
        'activo': registro.activo,
        'creador': registro.creador,
        'creacion': registro.creacion.isoformat() if registro.creacion else None,
        'modificador': registro.modificador,
        'modificacion': registro.modificacion.isoformat() if registro.modificacion else None
    })

@afectacion_variable_registros_bp.route('/api/afectacion_variable_registros/<int:id>', methods=['PUT'])
def update_afectacion_variable_registro(id):
    """Actualizar afectacion_variable_registro
    ---
    tags:
      - Afectacion Variable Registros
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
            cantidad: {type: integer}
            costo: {type: integer}
    responses:
      200:
        description: Registro actualizado
      404:
        description: No encontrado
    """
    data = request.get_json()
    now = datetime.now(timezone.utc)
    
    query = db.text("""
        UPDATE afectacion_variable_registros
        SET cantidad = :cantidad,
            costo = :costo
        WHERE id = :id
    """)

    params = {}
    if 'cantidad' in data:
        params['cantidad'] = data['cantidad']
    if 'costo' in data:
        params['costo'] = data['costo']
    params['id'] = id
    result = db.session.execute(query, params)
    
    if result.rowcount == 0:  # type: ignore
        return jsonify({'error': 'Registro no encontrado'}), 404
    
    db.session.commit()
    
    registro = db.session.execute(
        db.text("SELECT * FROM afectacion_variable_registros WHERE id = :id"),
        {'id': id}
    ).fetchone()

    if not registro:
        return jsonify({'error': 'Registro no encontrado'}), 404

    return jsonify({  # type: ignore
        'id': registro.id,
        'emergencia_id': registro.emergencia_id,
        'provincia_id': registro.provincia_id,
        'canton_id': registro.canton_id,
        'parroquia_id': registro.parroquia_id,
        'afectacion_variable_id': registro.afectacion_variable_id,
        'cantidad': registro.cantidad,
        'costo': registro.costo,
        'activo': registro.activo,
        'creador': registro.creador,
        'creacion': registro.creacion.isoformat() if registro.creacion else None,
        'modificador': registro.modificador,
        'modificacion': registro.modificacion.isoformat() if registro.modificacion else None
    })

@afectacion_variable_registros_bp.route('/api/afectacion_variable_registros/<int:id>', methods=['DELETE'])
def delete_afectacion_variable_registro(id):
    """Eliminar afectacion_variable_registro
    ---
    tags:
      - Afectacion Variable Registros
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
        db.text("DELETE FROM afectacion_variable_registros WHERE id = :id"), 
        {'id': id}
    )
    
    if result.rowcount == 0:  # type: ignore
        return jsonify({'error': 'Registro no encontrado'}), 404
    
    db.session.commit()
    return jsonify({'mensaje': 'Registro eliminado correctamente'})