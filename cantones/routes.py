from flask import request, jsonify
from cantones import cantones_bp
from models import db
from datetime import datetime, timezone

@cantones_bp.route('/api/cantones', methods=['GET'])
def get_cantones():
    """Listar cantones
    ---
    tags:
      - Cantones
    responses:
        200:
          description: Lista de cantones
          schema:
            type: array
            items:
              type: object
              properties:
                id: {type: integer}
                provincia_id: {type: integer}
                dpa: {type: string}
                nombre: {type: string}
                abreviatura: {type: string}
                activo: {type: boolean}
                creador: {type: string}
                creacion: {type: string}
                modificador: {type: string}
                modificacion: {type: string}
    """
    result = db.session.execute(db.text("SELECT * FROM cantones"))
    cantones = []
    for row in result:
        cantones.append({  # type: ignore
            'id': row.id,
            'provincia_id': row.provincia_id,
            'dpa': row.dpa,
            'nombre': row.nombre,
            'abreviatura': row.abreviatura,
            'activo': row.activo,
            'creador': row.creador,
            'creacion': row.creacion.isoformat() if row.creacion else None,
            'modificador': row.modificador,
            'modificacion': row.modificacion.isoformat() if row.modificacion else None
        })
    return jsonify(cantones)

@cantones_bp.route('/api/provincia/<int:provincia_id>/cantones/', methods=['GET'])
def get_cantones_by_provincia(provincia_id):
    """Listar cantones por provincia
    ---
    tags:
      - Cantones
    parameters:
      - name: provincia_id
        in: path
        type: integer
        required: true
    responses:
        200:
          description: Lista de cantones
          schema:
            type: array
            items:
              type: object
              properties:
                id: {type: integer}
                provincia_id: {type: integer}
                dpa: {type: string}
                nombre: {type: string}
                abreviatura: {type: string}
                activo: {type: boolean}
                creador: {type: string}
                creacion: {type: string}
                modificador: {type: string}
                modificacion: {type: string}
    """
    result = db.session.execute(db.text("SELECT * FROM cantones WHERE provincia_id = :provincia_id"), {'provincia_id': provincia_id})
    cantones = []
    for row in result:
        cantones.append({  # type: ignore
            'id': row.id,
            'provincia_id': row.provincia_id,
            'dpa': row.dpa,
            'nombre': row.nombre,
            'abreviatura': row.abreviatura,
            'activo': row.activo,
            'creador': row.creador,
            'creacion': row.creacion.isoformat() if row.creacion else None,
            'modificador': row.modificador,
            'modificacion': row.modificacion.isoformat() if row.modificacion else None
        })
    return jsonify(cantones)

@cantones_bp.route('/api/cantones', methods=['POST'])
def create_canton():
    """Crear canton
    ---
    tags:
      - Cantones
    consumes:
      - application/json
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          required: [provincia_id, nombre]
          properties:
            provincia_id: {type: integer}
            dpa: {type: string}
            nombre: {type: string}
            abreviatura: {type: string}
            activo: {type: boolean}
            creador: {type: string}
    responses:
      201:
        description: Canton creado
        schema:
          type: object
          properties:
            id: {type: integer}
            provincia_id: {type: integer}
            dpa: {type: string}
            nombre: {type: string}
            abreviatura: {type: string}
            activo: {type: boolean}
            creador: {type: string}
            creacion: {type: string}
            modificador: {type: string}
            modificacion: {type: string}
    """
    data = request.get_json()
    now = datetime.now(timezone.utc)
    
    query = db.text("""
        INSERT INTO cantones (provincia_id, dpa, nombre, abreviatura, activo, creador, creacion, modificador, modificacion)
        VALUES (:provincia_id, :dpa, :nombre, :abreviatura, :activo, :creador, :creacion, :modificador, :modificacion)
        RETURNING id
    """)
    
    result = db.session.execute(query, {
        'provincia_id': data['provincia_id'],
        'dpa': data['dpa'],
        'nombre': data['nombre'],
        'abreviatura': data.get('abreviatura'),
        'activo': data.get('activo', True),
        'creador': data.get('creador', 'Sistema'),
        'creacion': now,
        'modificador': data.get('creador', 'Sistema'),
        'modificacion': now
    })
    
    row = result.fetchone()
    if row is None:
        db.session.rollback()
        return jsonify({'error': 'Failed to create canton'}), 500
    canton_id = row[0]
    db.session.commit()

    canton = db.session.execute(
        db.text("SELECT * FROM cantones WHERE id = :id"),
        {'id': canton_id}
    ).fetchone()

    if not canton:
        return jsonify({'error': 'Canton not found after creation'}), 404

    return jsonify({  # type: ignore
        'id': canton.id,
        'provincia_id': canton.provincia_id,
        'dpa': canton.dpa,
        'nombre': canton.nombre,
        'abreviatura': canton.abreviatura,
        'activo': canton.activo,
        'creador': canton.creador,
        'creacion': canton.creacion.isoformat() if canton.creacion else None,
        'modificador': canton.modificador,
        'modificacion': canton.modificacion.isoformat() if canton.modificacion else None
    }), 201

@cantones_bp.route('/api/cantones/<int:id>', methods=['GET'])
def get_canton(id):
    """Obtener canton por ID
    ---
    tags:
      - Cantones
    parameters:
      - name: id
        in: path
        type: integer
        required: true
    responses:
      200:
        description: Canton
      404:
        description: No encontrado
    """
    result = db.session.execute(
        db.text("SELECT * FROM cantones WHERE id = :id"), 
        {'id': id}
    )
    canton = result.fetchone()
    
    if not canton:
        return jsonify({'error': 'Cantón no encontrado'}), 404
    
    return jsonify({
        'id': canton.id,
        'provincia_id': canton.provincia_id,
        'dpa': canton.dpa,
        'nombre': canton.nombre,
        'abreviatura': canton.abreviatura,
        'activo': canton.activo,
        'creador': canton.creador,
        'creacion': canton.creacion.isoformat() if canton.creacion else None,
        'modificador': canton.modificador,
        'modificacion': canton.modificacion.isoformat() if canton.modificacion else None
    })

@cantones_bp.route('/api/cantones/<int:id>', methods=['PUT'])
def update_canton(id):
    """Actualizar canton
    ---
    tags:
      - Cantones
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
            dpa: {type: string}
            nombre: {type: string}
            abreviatura: {type: string}
            activo: {type: boolean}
    responses:
      200:
        description: Canton actualizado
      404:
        description: No encontrado
    """
    data = request.get_json()
    now = datetime.now(timezone.utc)
    
    query = db.text("""
        UPDATE cantones 
        SET provincia_id = :provincia_id, 
            dpa = :dpa, 
            nombre = :nombre, 
            abreviatura = :abreviatura, 
            activo = :activo, 
            modificador = :modificador, 
            modificacion = :modificacion
        WHERE id = :id
    """)
    
    result = db.session.execute(query, {
        'id': id,
        'provincia_id': data.get('provincia_id'),
        'dpa': data.get('dpa'),
        'nombre': data.get('nombre'),
        'abreviatura': data.get('abreviatura'),
        'activo': data.get('activo'),
        'modificador': data.get('modificador', 'Sistema'),
        'modificacion': now
    })
    
    if result.rowcount == 0:  # type: ignore
        return jsonify({'error': 'Cantón no encontrado'}), 404

    db.session.commit()

    canton = db.session.execute(
        db.text("SELECT * FROM cantones WHERE id = :id"),
        {'id': id}
    ).fetchone()

    if not canton:
        return jsonify({'error': 'Canton not found after update'}), 404

    return jsonify({  # type: ignore
        'id': canton.id,
        'provincia_id': canton.provincia_id,
        'dpa': canton.dpa,
        'nombre': canton.nombre,
        'abreviatura': canton.abreviatura,
        'activo': canton.activo,
        'creador': canton.creador,
        'creacion': canton.creacion.isoformat() if canton.creacion else None,
        'modificador': canton.modificador,
        'modificacion': canton.modificacion.isoformat() if canton.modificacion else None
    })

@cantones_bp.route('/api/cantones/<int:id>', methods=['DELETE'])
def delete_canton(id):
    """Eliminar canton
    ---
    tags:
      - Cantones
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
        db.text("DELETE FROM cantones WHERE id = :id"), 
        {'id': id}
    )
    
    if result.rowcount == 0:  # type: ignore
        return jsonify({'error': 'Cantón no encontrado'}), 404
    
    db.session.commit()
    return jsonify({'mensaje': 'Cantón eliminado correctamente'})