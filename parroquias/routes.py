from flask import request, jsonify
from parroquias import parroquias_bp
from models import db
from datetime import datetime, timezone

@parroquias_bp.route('/api/parroquias', methods=['GET'])
def get_parroquias():
    """Listar parroquias
    ---
    tags:
      - Parroquias
    responses:
        200:
          description: Lista de parroquias
          schema:
            type: array
            items:
              type: object
              properties:
                id: {type: integer}
                provincia_id: {type: integer}
                canton_id: {type: integer}
                dpa: {type: string}
                nombre: {type: string}
                abreviatura: {type: string}
                activo: {type: boolean}
                creador: {type: string}
                creacion: {type: string}
                modificador: {type: string}
                modificacion: {type: string}
    """
    result = db.session.execute(db.text("SELECT * FROM parroquias"))
    parroquias = []
    for row in result:
        parroquias.append({  # type: ignore
            'id': row.id,
            'provincia_id': row.provincia_id,
            'canton_id': row.canton_id,
            'dpa': row.dpa,
            'nombre': row.nombre,
            'abreviatura': row.abreviatura,
            'activo': row.activo,
            'creador': row.creador,
            'creacion': row.creacion.isoformat() if row.creacion else None,
            'modificador': row.modificador,
            'modificacion': row.modificacion.isoformat() if row.modificacion else None
        })
    return jsonify(parroquias)

@parroquias_bp.route('/api/canton/<int:canton_id>/parroquias/', methods=['GET'])
def get_parroquias_by_canton(canton_id):
    """Listar parroquias por canton
    ---
    tags:
      - Parroquias
    parameters:
      - name: canton_id
        in: path
        type: integer
        required: true
    responses:
        200:
          description: Lista de parroquias
          schema:
            type: array
            items:
              type: object
              properties:
                id: {type: integer}
                provincia_id: {type: integer}
                canton_id: {type: integer}
                dpa: {type: string}
                nombre: {type: string}
                abreviatura: {type: string}
                activo: {type: boolean}
                creador: {type: string}
                creacion: {type: string}
                modificador: {type: string}
                modificacion: {type: string}
    """
    result = db.session.execute(db.text("SELECT * FROM parroquias WHERE canton_id = :canton_id"), {'canton_id': canton_id})
    parroquias = []
    for row in result:
        parroquias.append({  # type: ignore
            'id': row.id,
            'provincia_id': row.provincia_id,
            'canton_id': row.canton_id,
            'dpa': row.dpa,
            'nombre': row.nombre,
            'abreviatura': row.abreviatura,
            'activo': row.activo,
            'creador': row.creador,
            'creacion': row.creacion.isoformat() if row.creacion else None,
            'modificador': row.modificador,
            'modificacion': row.modificacion.isoformat() if row.modificacion else None
        })
    return jsonify(parroquias)

@parroquias_bp.route('/api/parroquias/canton/<int:canton_id>/emergencia/<int:emergencia_id>', methods=['GET'])
def get_parroquias_by_emergencia_by_canton(emergencia_id, canton_id):
    """Obtener parroquias por emergencia y canton
    ---
    tags:
      - Parroquias
    parameters:
      - name: emergencia_id
        in: path
        type: integer
        required: true
      - name: canton_id
        in: path
        type: integer
        required: true
    responses:
        200:
          description: Lista de parroquias
          schema:
            type: array
            items:
              type: object
              properties:
                id: {type: integer}
                provincia_id: {type: integer}
                canton_id: {type: integer}
                dpa: {type: string}
                nombre: {type: string}
                abreviatura: {type: string}
                activo: {type: boolean}
                creador: {type: string}
                creacion: {type: string}
                modificador: {type: string}
                modificacion: {type: string}
    """
    query = db.text("""
        SELECT DISTINCT q.id, q.dpa, q.nombre, q.abreviatura
        FROM public.parroquias q
        INNER JOIN public.emergencia_parroquias x ON q.id = x.parroquia_id
        WHERE q.canton_id = :canton_id AND x.emergencia_id = :emergencia_id
        ORDER BY q.id ASC
    """)
    result = db.session.execute(query, {'emergencia_id': emergencia_id, 'canton_id': canton_id})
    parroquias = []
    for row in result:
        parroquias.append({  # type: ignore
            'id': row.id,
            'dpa': row.dpa,
            'nombre': row.nombre,
            'abreviatura': row.abreviatura
        })
    return jsonify(parroquias)

@parroquias_bp.route('/api/parroquias', methods=['POST'])
def create_parroquia():
    """Crear parroquia
    ---
    tags:
      - Parroquias
    consumes:
      - application/json
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          required: [provincia_id, canton_id, nombre]
          properties:
            provincia_id: {type: integer}
            canton_id: {type: integer}
            dpa: {type: string}
            nombre: {type: string}
            abreviatura: {type: string}
            activo: {type: boolean}
            creador: {type: string}
    responses:
      201:
        description: Parroquia creada
        schema:
          type: object
          properties:
            id: {type: integer}
            provincia_id: {type: integer}
            canton_id: {type: integer}
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
        INSERT INTO parroquias (provincia_id, canton_id, dpa, nombre, abreviatura, activo, creador, creacion, modificador, modificacion)
        VALUES (:provincia_id, :canton_id, :dpa, :nombre, :abreviatura, :activo, :creador, :creacion, :modificador, :modificacion)
        RETURNING id
    """)
    
    result = db.session.execute(query, {
        'provincia_id': data['provincia_id'],
        'canton_id': data['canton_id'],
        'dpa': data.get('dpa'),
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
        return jsonify({'error': 'Failed to create parroquia'}), 500
    parroquia_id = row[0]
    db.session.commit()

    parroquia = db.session.execute(
        db.text("SELECT * FROM parroquias WHERE id = :id"),
        {'id': parroquia_id}
    ).fetchone()

    if not parroquia:
        return jsonify({'error': 'Parroquia not found after creation'}), 404

    return jsonify({  # type: ignore
        'id': parroquia.id,
        'provincia_id': parroquia.provincia_id,
        'canton_id': parroquia.canton_id,
        'dpa': parroquia.dpa,
        'nombre': parroquia.nombre,
        'abreviatura': parroquia.abreviatura,
        'activo': parroquia.activo,
        'creador': parroquia.creador,
        'creacion': parroquia.creacion.isoformat() if parroquia.creacion else None,
        'modificador': parroquia.modificador,
        'modificacion': parroquia.modificacion.isoformat() if parroquia.modificacion else None
    }), 201

@parroquias_bp.route('/api/parroquias/<int:id>', methods=['GET'])
def get_parroquia(id):
    """Obtener parroquia por ID
    ---
    tags:
      - Parroquias
    parameters:
      - name: id
        in: path
        type: integer
        required: true
    responses:
      200:
        description: Parroquia
      404:
        description: No encontrada
    """
    result = db.session.execute(
        db.text("SELECT * FROM parroquias WHERE id = :id"), 
        {'id': id}
    )
    parroquia = result.fetchone()
    
    if not parroquia:
        return jsonify({'error': 'Parroquia no encontrada'}), 404
    
    return jsonify({
        'id': parroquia.id,
        'provincia_id': parroquia.provincia_id,
        'canton_id': parroquia.canton_id,
        'dpa': parroquia.dpa,
        'nombre': parroquia.nombre,
        'abreviatura': parroquia.abreviatura,
        'activo': parroquia.activo,
        'creador': parroquia.creador,
        'creacion': parroquia.creacion.isoformat() if parroquia.creacion else None,
        'modificador': parroquia.modificador,
        'modificacion': parroquia.modificacion.isoformat() if parroquia.modificacion else None
    })

@parroquias_bp.route('/api/parroquias/<int:id>', methods=['PUT'])
def update_parroquia(id):
    """Actualizar parroquia
    ---
    tags:
      - Parroquias
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
            dpa: {type: string}
            nombre: {type: string}
            abreviatura: {type: string}
            activo: {type: boolean}
    responses:
      200:
        description: Parroquia actualizada
      404:
        description: No encontrada
    """
    data = request.get_json()
    now = datetime.now(timezone.utc)
    
    query = db.text("""
        UPDATE parroquias 
        SET provincia_id = :provincia_id, 
            canton_id = :canton_id, 
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
        'canton_id': data.get('canton_id'),
        'dpa': data.get('dpa'),
        'nombre': data.get('nombre'),
        'abreviatura': data.get('abreviatura'),
        'activo': data.get('activo'),
        'modificador': data.get('modificador', 'Sistema'),
        'modificacion': now
    })
    
    if result.rowcount == 0:  # type: ignore
        return jsonify({'error': 'Parroquia no encontrada'}), 404

    db.session.commit()

    parroquia = db.session.execute(
        db.text("SELECT * FROM parroquias WHERE id = :id"),
        {'id': id}
    ).fetchone()

    if not parroquia:
        return jsonify({'error': 'Parroquia not found after update'}), 404

    return jsonify({  # type: ignore
        'id': parroquia.id,
        'provincia_id': parroquia.provincia_id,
        'canton_id': parroquia.canton_id,
        'dpa': parroquia.dpa,
        'nombre': parroquia.nombre,
        'abreviatura': parroquia.abreviatura,
        'activo': parroquia.activo,
        'creador': parroquia.creador,
        'creacion': parroquia.creacion.isoformat() if parroquia.creacion else None,
        'modificador': parroquia.modificador,
        'modificacion': parroquia.modificacion.isoformat() if parroquia.modificacion else None
    })

@parroquias_bp.route('/api/parroquias/<int:id>', methods=['DELETE'])
def delete_parroquia(id):
    """Eliminar parroquia
    ---
    tags:
      - Parroquias
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
        db.text("DELETE FROM parroquias WHERE id = :id"), 
        {'id': id}
    )
    
    if result.rowcount == 0:  # type: ignore
        return jsonify({'error': 'Parroquia no encontrada'}), 404
    
    db.session.commit()
    return jsonify({'mensaje': 'Parroquia eliminada correctamente'})