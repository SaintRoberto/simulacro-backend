from flask import request, jsonify
from infraestructuras import infraestructuras_bp
from models import db
from datetime import datetime, timezone

@infraestructuras_bp.route('/api/infraestructuras', methods=['GET'])
def get_infraestructuras():
    """Listar infraestructuras
    ---
    tags:
      - Infraestructuras
    responses:
        200:
          description: Lista de infraestructuras
          schema:
            type: array
            items:
              type: object
              properties:
                id: {type: integer}
                infraestructura_tipo_id: {type: integer}
                nombre: {type: string}
                direccion: {type: string}
                provincia_id: {type: integer}
                canton_id: {type: integer}
                parroquia_id: {type: integer}
                tipologia: {type: string}
                institucion: {type: string}
                longitud: {type: number}
                latitud: {type: number}
                activo: {type: boolean}
                creador: {type: string}
                creacion: {type: string}
                modificador: {type: string}
                modificacion: {type: string}
    """
    result = db.session.execute(db.text("SELECT * FROM infraestructuras"))
    infraestructuras = []
    for row in result:
        infraestructuras.append({  # type: ignore
            'id': row.id,
            'infraestructura_tipo_id': row.infraestructura_tipo_id,
            'nombre': row.nombre,
            'direccion': row.direccion,
            'provincia_id': row.provincia_id,
            'canton_id': row.canton_id,
            'parroquia_id': row.parroquia_id,
            'tipologia': row.tipologia,
            'institucion': row.institucion,
            'longitud': float(row.longitud) if row.longitud else None,
            'latitud': float(row.latitud) if row.latitud else None,
            'activo': row.activo,
            'creador': row.creador,
            'creacion': row.creacion.isoformat() if row.creacion else None,
            'modificador': row.modificador,
            'modificacion': row.modificacion.isoformat() if row.modificacion else None
        })
    return jsonify(infraestructuras)

@infraestructuras_bp.route('/api/infraestructuras/parroquia/<int:parroquia_id>/infraestructura_tipo/<int:infraestructura_tipo_id>/emergencia/<int:emergencia_id>', methods=['GET'])
def get_infraestructuras_by_parroquia_by_infraestructura_tipo_by_emergencia(parroquia_id, infraestructura_tipo_id, emergencia_id):
    """Obtener infraestructuras por parroquia, infraestructura tipo y emergencia
    ---
    tags:
      - Infraestructuras
    parameters:
      - name: parroquia_id
        in: path
        type: integer
        required: true
      - name: infraestructura_tipo_id
        in: path
        type: integer
        required: true
      - name: emergencia_id
        in: path
        type: integer
        required: true
    responses:
        200:
          description: Lista de infraestructuras
          schema:
            type: array
            items:
              type: object
              properties:
                id: {type: integer}
                nombre: {type: string}
                direccion: {type: string}
                tipologia: {type: string}
                institucion: {type: string}
                longitud: {type: number}
                latitud: {type: number}
    """
    query = db.text("""
        SELECT id, nombre, direccion, tipologia, institucion, longitud, latitud
        FROM infraestructuras i
        WHERE parroquia_id = :parroquia_id
        AND infraestructura_tipo_id = :infraestructura_tipo_id
        AND id NOT IN (
        SELECT d.infraestructura_id
        FROM afectacion_variable_registro_detalles d
        INNER JOIN afectacion_variable_registros r ON d.afectacion_variable_registro_id = r.id
        WHERE r.emergencia_id = :emergencia_id
        )
    """)
    result = db.session.execute(query, {'parroquia_id': parroquia_id, 'infraestructura_tipo_id': infraestructura_tipo_id, 'emergencia_id': emergencia_id})
    infraestructuras = []
    for row in result:
        infraestructuras.append({  # type: ignore
            'id': row.id,
            'nombre': row.nombre,
            'direccion': row.direccion,
            'tipologia': row.tipologia,
            'institucion': row.institucion,
            'longitud': float(row.longitud) if row.longitud else None,
            'latitud': float(row.latitud) if row.latitud else None
        })
    return jsonify(infraestructuras)

@infraestructuras_bp.route('/api/infraestructuras', methods=['POST'])
def create_infraestructura():
    """Crear infraestructura
    ---
    tags:
      - Infraestructuras
    consumes:
      - application/json
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          required: [infraestructura_tipo_id, nombre, provincia_id, canton_id, parroquia_id, longitud, latitud]
          properties:
            infraestructura_tipo_id: {type: integer}
            nombre: {type: string}
            direccion: {type: string}
            provincia_id: {type: integer}
            canton_id: {type: integer}
            parroquia_id: {type: integer}
            tipologia: {type: string}
            institucion: {type: string}
            longitud: {type: number}
            latitud: {type: number}
            activo: {type: boolean}
            creador: {type: string}
    responses:
      201:
        description: Infraestructura creada
        schema:
          type: object
          properties:
            id: {type: integer}
            infraestructura_tipo_id: {type: integer}
            nombre: {type: string}
            direccion: {type: string}
            provincia_id: {type: integer}
            canton_id: {type: integer}
            parroquia_id: {type: integer}
            tipologia: {type: string}
            institucion: {type: string}
            longitud: {type: number}
            latitud: {type: number}
            activo: {type: boolean}
            creador: {type: string}
            creacion: {type: string}
            modificador: {type: string}
            modificacion: {type: string}
    """
    data = request.get_json()
    now = datetime.now(timezone.utc)

    query = db.text("""
        INSERT INTO infraestructuras (infraestructura_tipo_id, nombre, direccion, provincia_id, canton_id, parroquia_id, tipologia, institucion, longitud, latitud, activo, creador, creacion, modificador, modificacion)
        VALUES (:infraestructura_tipo_id, :nombre, :direccion, :provincia_id, :canton_id, :parroquia_id, :tipologia, :institucion, :longitud, :latitud, :activo, :creador, :creacion, :modificador, :modificacion)
        RETURNING id
    """)

    result = db.session.execute(query, {
        'infraestructura_tipo_id': data['infraestructura_tipo_id'],
        'nombre': data['nombre'],
        'direccion': data.get('direccion'),
        'provincia_id': data['provincia_id'],
        'canton_id': data['canton_id'],
        'parroquia_id': data['parroquia_id'],
        'tipologia': data.get('tipologia'),
        'institucion': data.get('institucion'),
        'longitud': data['longitud'],
        'latitud': data['latitud'],
        'activo': data.get('activo', True),
        'creador': data.get('creador', 'Sistema'),
        'creacion': now,
        'modificador': data.get('creador', 'Sistema'),
        'modificacion': now
    })

    row = result.fetchone()
    if row is None:
        db.session.rollback()
        return jsonify({'error': 'Failed to create infraestructura'}), 500
    infraestructura_id = row[0]
    db.session.commit()

    infraestructura = db.session.execute(
        db.text("SELECT * FROM infraestructuras WHERE id = :id"),
        {'id': infraestructura_id}
    ).fetchone()

    if not infraestructura:
        return jsonify({'error': 'Infraestructura not found after creation'}), 404

    return jsonify({  # type: ignore
        'id': infraestructura.id,
        'infraestructura_tipo_id': infraestructura.infraestructura_tipo_id,
        'nombre': infraestructura.nombre,
        'direccion': infraestructura.direccion,
        'provincia_id': infraestructura.provincia_id,
        'canton_id': infraestructura.canton_id,
        'parroquia_id': infraestructura.parroquia_id,
        'tipologia': infraestructura.tipologia,
        'institucion': infraestructura.institucion,
        'longitud': float(infraestructura.longitud) if infraestructura.longitud else None,
        'latitud': float(infraestructura.latitud) if infraestructura.latitud else None,
        'activo': infraestructura.activo,
        'creador': infraestructura.creador,
        'creacion': infraestructura.creacion.isoformat() if infraestructura.creacion else None,
        'modificador': infraestructura.modificador,
        'modificacion': infraestructura.modificacion.isoformat() if infraestructura.modificacion else None
    }), 201

@infraestructuras_bp.route('/api/infraestructuras/<int:id>', methods=['GET'])
def get_infraestructura(id):
    """Obtener infraestructura por ID
    ---
    tags:
      - Infraestructuras
    parameters:
      - name: id
        in: path
        type: integer
        required: true
    responses:
      200:
        description: Infraestructura
      404:
        description: No encontrada
    """
    result = db.session.execute(
        db.text("SELECT * FROM infraestructuras WHERE id = :id"),
        {'id': id}
    )
    infraestructura = result.fetchone()

    if not infraestructura:
        return jsonify({'error': 'Infraestructura no encontrada'}), 404

    return jsonify({
        'id': infraestructura.id,
        'infraestructura_tipo_id': infraestructura.infraestructura_tipo_id,
        'nombre': infraestructura.nombre,
        'direccion': infraestructura.direccion,
        'provincia_id': infraestructura.provincia_id,
        'canton_id': infraestructura.canton_id,
        'parroquia_id': infraestructura.parroquia_id,
        'tipologia': infraestructura.tipologia,
        'institucion': infraestructura.institucion,
        'longitud': float(infraestructura.longitud) if infraestructura.longitud else None,
        'latitud': float(infraestructura.latitud) if infraestructura.latitud else None,
        'activo': infraestructura.activo,
        'creador': infraestructura.creador,
        'creacion': infraestructura.creacion.isoformat() if infraestructura.creacion else None,
        'modificador': infraestructura.modificador,
        'modificacion': infraestructura.modificacion.isoformat() if infraestructura.modificacion else None
    })

@infraestructuras_bp.route('/api/infraestructuras/<int:id>', methods=['PUT'])
def update_infraestructura(id):
    """Actualizar infraestructura
    ---
    tags:
      - Infraestructuras
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
            infraestructura_tipo_id: {type: integer}
            nombre: {type: string}
            direccion: {type: string}
            provincia_id: {type: integer}
            canton_id: {type: integer}
            parroquia_id: {type: integer}
            tipologia: {type: string}
            institucion: {type: string}
            longitud: {type: number}
            latitud: {type: number}
            activo: {type: boolean}
    responses:
      200:
        description: Infraestructura actualizada
      404:
        description: No encontrada
    """
    data = request.get_json()
    now = datetime.now(timezone.utc)

    query = db.text("""
        UPDATE infraestructuras
        SET infraestructura_tipo_id = :infraestructura_tipo_id,
            nombre = :nombre,
            direccion = :direccion,
            provincia_id = :provincia_id,
            canton_id = :canton_id,
            parroquia_id = :parroquia_id,
            tipologia = :tipologia,
            institucion = :institucion,
            longitud = :longitud,
            latitud = :latitud,
            activo = :activo,
            modificador = :modificador,
            modificacion = :modificacion
        WHERE id = :id
    """)

    result = db.session.execute(query, {
        'id': id,
        'infraestructura_tipo_id': data.get('infraestructura_tipo_id'),
        'nombre': data.get('nombre'),
        'direccion': data.get('direccion'),
        'provincia_id': data.get('provincia_id'),
        'canton_id': data.get('canton_id'),
        'parroquia_id': data.get('parroquia_id'),
        'tipologia': data.get('tipologia'),
        'institucion': data.get('institucion'),
        'longitud': data.get('longitud'),
        'latitud': data.get('latitud'),
        'activo': data.get('activo'),
        'modificador': data.get('modificador', 'Sistema'),
        'modificacion': now
    })

    if result.rowcount == 0:  # type: ignore
        return jsonify({'error': 'Infraestructura no encontrada'}), 404

    db.session.commit()

    infraestructura = db.session.execute(
        db.text("SELECT * FROM infraestructuras WHERE id = :id"),
        {'id': id}
    ).fetchone()

    if not infraestructura:
        return jsonify({'error': 'Infraestructura not found after update'}), 404

    return jsonify({  # type: ignore
        'id': infraestructura.id,
        'infraestructura_tipo_id': infraestructura.infraestructura_tipo_id,
        'nombre': infraestructura.nombre,
        'direccion': infraestructura.direccion,
        'provincia_id': infraestructura.provincia_id,
        'canton_id': infraestructura.canton_id,
        'parroquia_id': infraestructura.parroquia_id,
        'tipologia': infraestructura.tipologia,
        'institucion': infraestructura.institucion,
        'longitud': float(infraestructura.longitud) if infraestructura.longitud else None,
        'latitud': float(infraestructura.latitud) if infraestructura.latitud else None,
        'activo': infraestructura.activo,
        'creador': infraestructura.creador,
        'creacion': infraestructura.creacion.isoformat() if infraestructura.creacion else None,
        'modificador': infraestructura.modificador,
        'modificacion': infraestructura.modificacion.isoformat() if infraestructura.modificacion else None
    })

@infraestructuras_bp.route('/api/infraestructuras/<int:id>', methods=['DELETE'])
def delete_infraestructura(id):
    """Eliminar infraestructura
    ---
    tags:
      - Infraestructuras
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
        db.text("DELETE FROM infraestructuras WHERE id = :id"),
        {'id': id}
    )

    if result.rowcount == 0:  # type: ignore
        return jsonify({'error': 'Infraestructura no encontrada'}), 404

    db.session.commit()
    return jsonify({'mensaje': 'Infraestructura eliminada correctamente'})