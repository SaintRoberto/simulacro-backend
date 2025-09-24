from flask import request, jsonify, Blueprint
from models import db
from datetime import datetime, timezone

afectacion_variables_bp = Blueprint('afectacion_variables', __name__)

@afectacion_variables_bp.route('/api/afectacion_variables', methods=['GET'])
def get_afectacion_variables():
    """Listar afectacion_variables
    ---
    tags:
      - Afectacion Variables
    responses:
        200:
          description: Lista de variables
          schema:
            type: array
            items:
              type: object
              properties:
                id: {type: integer}
                coe_id: {type: integer}
                mesa_grupo_id: {type: integer}
                nombre: {type: string}
                dato_tipo_id: {type: integer}
                requiere_costo: {type: boolean}
                requiere_gis: {type: boolean}
                observaciones: {type: string}
                infraestructura_tipo_id: {type: integer}
                activo: {type: boolean}
                creador: {type: string}
                creacion: {type: string}
                modificador: {type: string}
                modificacion: {type: string}
    """
    result = db.session.execute(db.text("SELECT * FROM afectacion_variables"))
    variables = []
    for row in result:
        variables.append({  # type: ignore
            'id': row.id,
            'coe_id': row.coe_id,
            'mesa_grupo_id': row.mesa_grupo_id,
            'nombre': row.nombre,
            'dato_tipo_id': row.dato_tipo_id,
            'requiere_costo': row.requiere_costo,
            'requiere_gis': row.requiere_gis,
            'observaciones': row.observaciones,
            'infraestructura_tipo_id': row.infraestructura_tipo_id,
            'activo': row.activo,
            'creador': row.creador,
            'creacion': row.creacion.isoformat() if row.creacion else None,
            'modificador': row.modificador,
            'modificacion': row.modificacion.isoformat() if row.modificacion else None
        })
    return jsonify(variables)

@afectacion_variables_bp.route('/api/mesa_grupo/<int:mesa_grupo_id>/afectacion_varibles/', methods=['GET'])
def get_afectacion_variables_by_mesa_grupo(mesa_grupo_id):
    """Listar afectacion_variables por mesa_grupo
    ---
    tags:
      - Afectacion Variables
    parameters:
      - name: mesa_grupo_id
        in: path
        type: integer
        required: true
    responses:
        200:
          description: Lista de variables
          schema:
            type: array
            items:
              type: object
              properties:
                id: {type: integer}
                coe_id: {type: integer}
                mesa_grupo_id: {type: integer}
                nombre: {type: string}
                dato_tipo_id: {type: integer}
                requiere_costo: {type: boolean}
                requiere_gis: {type: boolean}
                observaciones: {type: string}
                infraestructura_tipo_id: {type: integer}
                activo: {type: boolean}
                creador: {type: string}
                creacion: {type: string}
                modificador: {type: string}
                modificacion: {type: string}
    """
    result = db.session.execute(db.text("SELECT * FROM afectacion_variables WHERE mesa_grupo_id = :mesa_grupo_id"), {'mesa_grupo_id': mesa_grupo_id})
    variables = []
    for row in result:
        variables.append({  # type: ignore
            'id': row.id,
            'coe_id': row.coe_id,
            'mesa_grupo_id': row.mesa_grupo_id,
            'nombre': row.nombre,
            'dato_tipo_id': row.dato_tipo_id,
            'requiere_costo': row.requiere_costo,
            'requiere_gis': row.requiere_gis,
            'observaciones': row.observaciones,
            'infraestructura_tipo_id': row.infraestructura_tipo_id,
            'activo': row.activo,
            'creador': row.creador,
            'creacion': row.creacion.isoformat() if row.creacion else None,
            'modificador': row.modificador,
            'modificacion': row.modificacion.isoformat() if row.modificacion else None
        })
    return jsonify(variables)

@afectacion_variables_bp.route('/api/afectacion_variables', methods=['POST'])
def create_afectacion_variable():
    """Crear afectacion_variable
    ---
    tags:
      - Afectacion Variables
    consumes:
      - application/json
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          required: [coe_id, mesa_grupo_id, nombre, dato_tipo_id, observaciones]
          properties:
            coe_id: {type: integer}
            mesa_grupo_id: {type: integer}
            nombre: {type: string}
            dato_tipo_id: {type: integer}
            requiere_costo: {type: boolean}
            requiere_gis: {type: boolean}
            observaciones: {type: string}
            infraestructura_tipo_id: {type: integer}
            activo: {type: boolean}
            creador: {type: string}
    responses:
      201:
        description: Variable creada
        schema:
          type: object
          properties:
            id: {type: integer}
            coe_id: {type: integer}
            mesa_grupo_id: {type: integer}
            nombre: {type: string}
            dato_tipo_id: {type: integer}
            requiere_costo: {type: boolean}
            requiere_gis: {type: boolean}
            observaciones: {type: string}
            infraestructura_tipo_id: {type: integer}
            activo: {type: boolean}
            creador: {type: string}
            creacion: {type: string}
            modificador: {type: string}
            modificacion: {type: string}
    """
    data = request.get_json()
    now = datetime.now(timezone.utc)
    
    query = db.text("""
        INSERT INTO afectacion_variables (
            coe_id, mesa_grupo_id, nombre, dato_tipo_id, requiere_costo, requiere_gis,
            observaciones, infraestructura_tipo_id, activo, creador, creacion, modificador, modificacion
        )
        VALUES (
            :coe_id, :mesa_grupo_id, :nombre, :dato_tipo_id, :requiere_costo, :requiere_gis,
            :observaciones, :infraestructura_tipo_id, :activo, :creador, :creacion, :modificador, :modificacion
        )
        RETURNING id
    """)

    result = db.session.execute(query, {
        'coe_id': data['coe_id'],
        'mesa_grupo_id': data['mesa_grupo_id'],
        'nombre': data['nombre'],
        'dato_tipo_id': data['dato_tipo_id'],
        'requiere_costo': data.get('requiere_costo', False),
        'requiere_gis': data.get('requiere_gis', False),
        'observaciones': data['observaciones'],
        'infraestructura_tipo_id': data.get('infraestructura_tipo_id', -1),
        'activo': data.get('activo', True),
        'creador': data.get('creador', 'Sistema'),
        'creacion': now,
        'modificador': data.get('creador', 'Sistema'),
        'modificacion': now
    })

    row = result.fetchone()
    if row is None:
        db.session.rollback()
        return jsonify({'error': 'Failed to create variable'}), 500
    variable_id = row[0]
    db.session.commit()
    
    variable = db.session.execute(
        db.text("SELECT * FROM afectacion_variables WHERE id = :id"), 
        {'id': variable_id}
    ).fetchone()

    if not variable:
        return jsonify({'error': 'Variable not found after creation'}), 404

    return jsonify({  # type: ignore
        'id': variable.id,
        'coe_id': variable.coe_id,
        'mesa_grupo_id': variable.mesa_grupo_id,
        'nombre': variable.nombre,
        'dato_tipo_id': variable.dato_tipo_id,
        'requiere_costo': variable.requiere_costo,
        'requiere_gis': variable.requiere_gis,
        'observaciones': variable.observaciones,
        'infraestructura_tipo_id': variable.infraestructura_tipo_id,
        'activo': variable.activo,
        'creador': variable.creador,
        'creacion': variable.creacion.isoformat() if variable.creacion else None,
        'modificador': variable.modificador,
        'modificacion': variable.modificacion.isoformat() if variable.modificacion else None
    }), 201

@afectacion_variables_bp.route('/api/afectacion_variables/<int:id>', methods=['GET'])
def get_afectacion_variable(id):
    """Obtener afectacion_variable por ID
    ---
    tags:
      - Afectacion Variables
    parameters:
      - name: id
        in: path
        type: integer
        required: true
    responses:
      200:
        description: Variable
      404:
        description: No encontrada
    """
    result = db.session.execute(
        db.text("SELECT * FROM afectacion_variables WHERE id = :id"), 
        {'id': id}
    )
    variable = result.fetchone()
    
    if not variable:
        return jsonify({'error': 'Variable no encontrada'}), 404
    
    return jsonify({
        'id': variable.id,
        'coe_id': variable.coe_id,
        'mesa_grupo_id': variable.mesa_grupo_id,
        'nombre': variable.nombre,
        'dato_tipo_id': variable.dato_tipo_id,
        'requiere_costo': variable.requiere_costo,
        'requiere_gis': variable.requiere_gis,
        'observaciones': variable.observaciones,
        'infraestructura_tipo_id': variable.infraestructura_tipo_id,
        'activo': variable.activo,
        'creador': variable.creador,
        'creacion': variable.creacion.isoformat() if variable.creacion else None,
        'modificador': variable.modificador,
        'modificacion': variable.modificacion.isoformat() if variable.modificacion else None
    })

@afectacion_variables_bp.route('/api/afectacion_variables/<int:id>', methods=['PUT'])
def update_afectacion_variable(id):
    """Actualizar afectacion_variable
    ---
    tags:
      - Afectacion Variables
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
            nombre: {type: string}
            dato_tipo_id: {type: integer}
            requiere_costo: {type: boolean}
            requiere_gis: {type: boolean}
            observaciones: {type: string}
            infraestructura_tipo_id: {type: integer}
            activo: {type: boolean}
    responses:
      200:
        description: Variable actualizada
      404:
        description: No encontrada
    """
    data = request.get_json()
    now = datetime.now(timezone.utc)
    
    query = db.text("""
        UPDATE afectacion_variables
        SET nombre = :nombre,
            dato_tipo_id = :dato_tipo_id,
            requiere_costo = :requiere_costo,
            requiere_gis = :requiere_gis,
            observaciones = :observaciones,
            infraestructura_tipo_id = :infraestructura_tipo_id,
            activo = :activo
        WHERE id = :id
    """)

    result = db.session.execute(query, {
        'nombre': data.get('nombre'),
        'dato_tipo_id': data.get('dato_tipo_id'),
        'requiere_costo': data.get('requiere_costo'),
        'requiere_gis': data.get('requiere_gis'),
        'observaciones': data.get('observaciones'),
        'infraestructura_tipo_id': data.get('infraestructura_tipo_id'),
        'activo': data.get('activo'),
        'id': id
    })
    
    if result.rowcount == 0:  # type: ignore
        return jsonify({'error': 'Variable no encontrada'}), 404
    
    db.session.commit()
    
    variable = db.session.execute(
        db.text("SELECT * FROM afectacion_variables WHERE id = :id"), 
        {'id': id}
    ).fetchone()

    if not variable:
        return jsonify({'error': 'Variable not found after update'}), 404
    
    return jsonify({  # type: ignore
        'id': variable.id,
        'coe_id': variable.coe_id,
        'mesa_grupo_id': variable.mesa_grupo_id,
        'nombre': variable.nombre,
        'dato_tipo_id': variable.dato_tipo_id,
        'requiere_costo': variable.requiere_costo,
        'requiere_gis': variable.requiere_gis,
        'observaciones': variable.observaciones,
        'infraestructura_tipo_id': variable.infraestructura_tipo_id,
        'activo': variable.activo,
        'creador': variable.creador,
        'creacion': variable.creacion.isoformat() if variable.creacion else None,
        'modificador': variable.modificador,
        'modificacion': variable.modificacion.isoformat() if variable.modificacion else None
    })

@afectacion_variables_bp.route('/api/afectacion_variables/<int:id>', methods=['DELETE'])
def delete_afectacion_variable(id):
    """Eliminar afectacion_variable
    ---
    tags:
      - Afectacion Variables
    parameters:
      - name: id
        in: path
        type: integer
        required: true
    responses:
      200:
        description: Eliminada
      404:
        description: No encontrada
    """
    result = db.session.execute(
        db.text("DELETE FROM afectacion_variables WHERE id = :id"), 
        {'id': id}
    )
    
    if result.rowcount == 0:  # type: ignore
        return jsonify({'error': 'Variable no encontrada'}), 404
    
    db.session.commit()
    return jsonify({'mensaje': 'Variable eliminada correctamente'})