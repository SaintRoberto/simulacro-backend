from flask import request, jsonify
from provincias import provincias_bp
from models import db
from datetime import datetime, timezone

@provincias_bp.route('/api/provincias', methods=['GET'])
def get_provincias():
    """Listar provincias
    ---
    tags:
      - Provincias
    responses:
        200:
          description: Lista de provincias
          schema:
            type: array
            items:
              type: object
              properties:
                id: {type: integer}
                dpa: {type: string}
                nombre: {type: string}
                abreviatura: {type: string}
                activo: {type: boolean}
                creador: {type: string}
                creacion: {type: string}
                modificador: {type: string}
                modificacion: {type: string}
    """
    result = db.session.execute(db.text("SELECT * FROM provincias"))
    provincias = []
    for row in result:
        provincias.append({  # type: ignore
            'id': row.id,
            'dpa': row.dpa,
            'nombre': row.nombre,
            'abreviatura': row.abreviatura,
            'activo': row.activo,
            'creador': row.creador,
            'creacion': row.creacion.isoformat() if row.creacion else None,
            'modificador': row.modificador,
            'modificacion': row.modificacion.isoformat() if row.modificacion else None
        })
    return jsonify(provincias)

@provincias_bp.route('/api/provincias', methods=['POST'])
def create_provincia():
    """Crear provincia
    ---
    tags:
      - Provincias
    consumes:
      - application/json
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          required: [nombre, abreviatura]
          properties:
            dpa: {type: string}
            nombre: {type: string}
            abreviatura: {type: string}
            activo: {type: boolean}
            creador: {type: string}
    responses:
      201:
        description: Provincia creada
        schema:
          type: object
          properties:
            id: {type: integer}
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
        INSERT INTO provincias (dpa, nombre, abreviatura, activo, creador, creacion, modificador, modificacion)
        VALUES (:dpa, :nombre, :abreviatura, :activo, :creador, :creacion, :modificador, :modificacion)
        RETURNING id
    """)
    
    result = db.session.execute(query, {
        'dpa': data.get('dpa'),
        'nombre': data['nombre'],
        'abreviatura': data['abreviatura'],
        'activo': data.get('activo', True),
        'creador': data.get('creador', 'Sistema'),
        'creacion': now,
        'modificador': data.get('creador', 'Sistema'),
        'modificacion': now
    })
    
    row = result.fetchone()
    if row is None:
        db.session.rollback()
        return jsonify({'error': 'Failed to create provincia'}), 500
    provincia_id = row[0]
    db.session.commit()

    provincia = db.session.execute(
        db.text("SELECT * FROM provincias WHERE id = :id"),
        {'id': provincia_id}
    ).fetchone()

    if not provincia:
        return jsonify({'error': 'Provincia not found after creation'}), 404

    return jsonify({  # type: ignore
        'id': provincia.id,
        'dpa': provincia.dpa,
        'nombre': provincia.nombre,
        'abreviatura': provincia.abreviatura,
        'activo': provincia.activo,
        'creador': provincia.creador,
        'creacion': provincia.creacion.isoformat() if provincia.creacion else None,
        'modificador': provincia.modificador,
        'modificacion': provincia.modificacion.isoformat() if provincia.modificacion else None
    }), 201

@provincias_bp.route('/api/provincias/<int:id>', methods=['GET'])
def get_provincia(id):
    """Obtener provincia por ID
    ---
    tags:
      - Provincias
    parameters:
      - name: id
        in: path
        type: integer
        required: true
    responses:
      200:
        description: Provincia
      404:
        description: No encontrada
    """
    result = db.session.execute(
        db.text("SELECT * FROM provincias WHERE id = :id"), 
        {'id': id}
    )
    provincia = result.fetchone()
    
    if not provincia:
        return jsonify({'error': 'Provincia no encontrada'}), 404
    
    return jsonify({
        'id': provincia.id,
        'dpa': provincia.dpa,
        'nombre': provincia.nombre,
        'abreviatura': provincia.abreviatura,
        'activo': provincia.activo,
        'creador': provincia.creador,
        'creacion': provincia.creacion.isoformat() if provincia.creacion else None,
        'modificador': provincia.modificador,
        'modificacion': provincia.modificacion.isoformat() if provincia.modificacion else None
    })

@provincias_bp.route('/api/provincias/<int:id>', methods=['PUT'])
def update_provincia(id):
    """Actualizar provincia
    ---
    tags:
      - Provincias
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
            dpa: {type: string}
            nombre: {type: string}
            abreviatura: {type: string}
            activo: {type: boolean}
    responses:
      200:
        description: Provincia actualizada
      404:
        description: No encontrada
    """
    data = request.get_json()
    now = datetime.now(timezone.utc)
    
    query = db.text("""
        UPDATE provincias 
        SET dpa = :dpa, 
            nombre = :nombre, 
            abreviatura = :abreviatura, 
            activo = :activo, 
            modificador = :modificador, 
            modificacion = :modificacion
        WHERE id = :id
    """)
    
    result = db.session.execute(query, {
        'id': id,
        'dpa': data.get('dpa'),
        'nombre': data.get('nombre'),
        'abreviatura': data.get('abreviatura'),
        'activo': data.get('activo'),
        'modificador': data.get('modificador', 'Sistema'),
        'modificacion': now
    })
    
    if getattr(result, 'rowcount', 0) == 0:  # type: ignore
        return jsonify({'error': 'Provincia no encontrada'}), 404

    db.session.commit()

    provincia = db.session.execute(
        db.text("SELECT * FROM provincias WHERE id = :id"),
        {'id': id}
    ).fetchone()

    if not provincia:
        return jsonify({'error': 'Provincia not found after update'}), 404

    return jsonify({  # type: ignore
        'id': provincia.id,
        'dpa': provincia.dpa,
        'nombre': provincia.nombre,
        'abreviatura': provincia.abreviatura,
        'activo': provincia.activo,
        'creador': provincia.creador,
        'creacion': provincia.creacion.isoformat() if provincia.creacion else None,
        'modificador': provincia.modificador,
        'modificacion': provincia.modificacion.isoformat() if provincia.modificacion else None
    })

@provincias_bp.route('/api/provincias/<int:id>', methods=['DELETE'])
def delete_provincia(id):
    """Eliminar provincia
    ---
    tags:
      - Provincias
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
        db.text("DELETE FROM provincias WHERE id = :id"), 
        {'id': id}
    )
    
    if getattr(result, 'rowcount', 0) == 0:  # type: ignore
        return jsonify({'error': 'Provincia no encontrada'}), 404
    
    db.session.commit()
    return jsonify({'mensaje': 'Provincia eliminada correctamente'})

@provincias_bp.route('/api/provincias/emergencia/<int:emergencia_id>', methods=['GET'])
def get_provincias_by_emergencia(emergencia_id):
    """Obtener provincias por emergencia
    ---
    tags:
      - Provincias
    parameters:
      - name: emergencia_id
        in: path
        type: integer
        required: true
    responses:
        200:
          description: Lista de provincias
          schema:
            type: array
            items:
              type: object
              properties:
                id: {type: integer}
                dpa: {type: string}
                nombre: {type: string}
                abreviatura: {type: string}
    """
    query = db.text("""
        SELECT DISTINCT p.id, p.dpa, p.nombre, p.abreviatura
        FROM public.parroquias q
        INNER JOIN public.emergencia_parroquias x ON q.id = x.parroquia_id
        INNER JOIN public.provincias p ON q.provincia_id = p.id
        WHERE x.emergencia_id = :emergencia_id
        ORDER BY p.id ASC
    """)
    result = db.session.execute(query, {'emergencia_id': emergencia_id})
    provincias = []
    for row in result:
        provincias.append({  # type: ignore
            'id': row.id,
            'dpa': row.dpa,
            'nombre': row.nombre,
            'abreviatura': row.abreviatura
        })
    return jsonify(provincias)