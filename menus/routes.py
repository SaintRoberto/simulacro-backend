from flask import request, jsonify
from menus import menus_bp
from models import db
from datetime import datetime, timezone

@menus_bp.route('/api/menus', methods=['GET'])
def get_menus():
    """Listar todos los menús.
    ---
    tags:
      - Menús
    responses:
      200:
        description: Lista de menús
        schema:
          type: array
          items:
            type: object
            properties:
              id: {type: integer}
              padre_id: {type: integer}
              orden: {type: integer}
              nombre: {type: string}
              abreviatura: {type: string}
              ruta: {type: string}
              activo: {type: boolean}
              creador: {type: string}
              creacion: {type: string}
              modificador: {type: string}
              modificacion: {type: string}
    """
    result = db.session.execute(db.text("SELECT * FROM menus"))
    menus = []
    for row in result:
        menus.append({
            'id': row.id,
            'padre_id': row.padre_id,
            'orden': row.orden,
            'nombre': row.nombre,
            'abreviatura': row.abreviatura,
            'ruta': row.ruta,
            'activo': row.activo,
            'creador': row.creador,
            'creacion': row.creacion.isoformat() if row.creacion else None,
            'modificador': row.modificador,
            'modificacion': row.modificacion.isoformat() if row.modificacion else None
        })
    return jsonify(menus)

@menus_bp.route('/api/menus/perfil/<int:perfil_id>/coe/<int:coe_id>/mesa/<int:mesa_id>', methods=['GET'])
def get_menus_by_usuario(perfil_id, coe_id, mesa_id):
    """Obtener menús visibles para un usuario según perfil, COE y mesa.
    ---
    tags:
      - Menús
    parameters:
      - name: perfil_id
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
        description: Lista de menús autorizados para el usuario
        schema:
          type: array
          items:
            type: object
            properties:
              id: {type: integer}
              padre_id: {type: integer}
              orden: {type: integer}
              nombre: {type: string}
              ruta: {type: string}
              icono: {type: string}
    """
    query = db.text("""
        SELECT DISTINCT m.id, m.padre_id, m.orden, m.nombre, m.ruta, m.icono 
        FROM menus m 
        LEFT JOIN perfil_coe_mesa_menu_opcion x ON m.id = x.menu_id
        WHERE ((x.perfil_id = :perfil_id AND x.coe_id = :coe_id AND (x.mesa_id = :mesa_id OR :mesa_id = 0))
           OR m.orden = 0) AND m.activo = true
        ORDER BY m.padre_id, m.orden;
    """)
    result = db.session.execute(query, {
        'perfil_id': perfil_id,
        'coe_id': coe_id,
        'mesa_id': mesa_id,
    })
    menus = []
    for row in result:
        menus.append({
            'id': row.id,
            'padre_id': row.padre_id,
            'orden': row.orden,
            'nombre': row.nombre,
            'ruta': row.ruta,
            'icono': row.icono,
        })
    return jsonify(menus)

@menus_bp.route('/api/menus', methods=['POST'])
def create_menu():
    """Crear un nuevo menú.
    ---
    tags:
      - Menús
    consumes:
      - application/json
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          properties:
            padre_id: {type: integer}
            orden: {type: integer}
            nombre: {type: string}
            abreviatura: {type: string}
            ruta: {type: string}
            activo: {type: boolean}
            creador: {type: string}
    responses:
      201:
        description: Menú creado correctamente
        schema:
          type: object
          properties:
            id: {type: integer}
            padre_id: {type: integer}
            orden: {type: integer}
            nombre: {type: string}
            abreviatura: {type: string}
            ruta: {type: string}
            activo: {type: boolean}
            creador: {type: string}
            creacion: {type: string}
            modificador: {type: string}
            modificacion: {type: string}
      400:
        description: Datos inválidos
    """
    data = request.get_json()
    if not data:
        return jsonify({'error': 'Invalid JSON body'}), 400

    nombre = data.get('nombre')
    if not nombre:
        return jsonify({'error': 'El campo "nombre" es requerido'}), 400

    now = datetime.now(timezone.utc)
    
    query = db.text("""
        INSERT INTO menus (padre_id, orden, nombre, abreviatura, ruta, activo, creador, creacion, modificador, modificacion)
        VALUES (:padre_id, :orden, :nombre, :abreviatura, :ruta, :activo, :creador, :creacion, :modificador, :modificacion)
        RETURNING id
    """)
    
    result = db.session.execute(query, {
        'padre_id': data.get('padre_id'),
        'orden': data.get('orden', 0),
        'nombre': nombre,
        'abreviatura': data.get('abreviatura', ''),
        'ruta': data.get('ruta', ''),
        'activo': data.get('activo', True),
        'creador': data.get('creador', 'Sistema'),
        'creacion': now,
        'modificador': data.get('modificador', data.get('creador', 'Sistema')),
        'modificacion': now
    })
    
    row = result.fetchone()
    if row is None:
        return jsonify({'error': 'Not found'}), 404
    menu_id = row[0]
    db.session.commit()
    
    menu = db.session.execute(
        db.text("SELECT * FROM menus WHERE id = :id"),
        {'id': menu_id}
    ).fetchone()

    if not menu:
        return jsonify({'error': 'Menú no encontrado'}), 404

    return jsonify({
        'id': menu.id,
        'padre_id': menu.padre_id,
        'orden': menu.orden,
        'nombre': menu.nombre,
        'abreviatura': menu.abreviatura,
        'ruta': menu.ruta,
        'activo': menu.activo,
        'creador': menu.creador,
        'creacion': menu.creacion.isoformat() if menu.creacion else None,
        'modificador': menu.modificador,
        'modificacion': menu.modificacion.isoformat() if menu.modificacion else None
    }), 201

@menus_bp.route('/api/menus/<int:id>', methods=['GET'])
def get_menu(id):
    """Obtener un menú por su ID.
    ---
    tags:
      - Menús
    parameters:
      - name: id
        in: path
        type: integer
        required: true
    responses:
      200:
        description: Menú encontrado
        schema:
          type: object
          properties:
            id: {type: integer}
            padre_id: {type: integer}
            orden: {type: integer}
            nombre: {type: string}
            abreviatura: {type: string}
            ruta: {type: string}
            activo: {type: boolean}
            creador: {type: string}
            creacion: {type: string}
            modificador: {type: string}
            modificacion: {type: string}
      404:
        description: Menú no encontrado
    """
    result = db.session.execute(
        db.text("SELECT * FROM menus WHERE id = :id"), 
        {'id': id}
    )
    menu = result.fetchone()
    
    if not menu:
        return jsonify({'error': 'Menú no encontrado'}), 404
    
    return jsonify({
        'id': menu.id,
        'padre_id': menu.padre_id,
        'orden': menu.orden,
        'nombre': menu.nombre,
        'abreviatura': menu.abreviatura,
        'ruta': menu.ruta,
        'activo': menu.activo,
        'creador': menu.creador,
        'creacion': menu.creacion.isoformat() if menu.creacion else None,
        'modificador': menu.modificador,
        'modificacion': menu.modificacion.isoformat() if menu.modificacion else None
    })

@menus_bp.route('/api/menus/<int:id>', methods=['PUT'])
def update_menu(id):
    """Actualizar un menú existente.
    ---
    tags:
      - Menús
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
            padre_id: {type: integer}
            orden: {type: integer}
            nombre: {type: string}
            abreviatura: {type: string}
            ruta: {type: string}
            activo: {type: boolean}
            modificador: {type: string}
    responses:
      200:
        description: Menú actualizado
        schema:
          type: object
          properties:
            id: {type: integer}
            padre_id: {type: integer}
            orden: {type: integer}
            nombre: {type: string}
            abreviatura: {type: string}
            ruta: {type: string}
            activo: {type: boolean}
            creador: {type: string}
            creacion: {type: string}
            modificador: {type: string}
            modificacion: {type: string}
      404:
        description: Menú no encontrado
    """
    data = request.get_json()
    now = datetime.now(timezone.utc)
    
    query = db.text("""
        UPDATE menus 
        SET padre_id = :padre_id, 
            orden = :orden, 
            nombre = :nombre, 
            abreviatura = :abreviatura, 
            ruta = :ruta, 
            activo = :activo, 
            modificador = :modificador, 
            modificacion = :modificacion
        WHERE id = :id
    """)
    
    result = db.session.execute(query, {
        'id': id,
        'padre_id': data.get('padre_id'),
        'orden': data.get('orden'),
        'nombre': data.get('nombre'),
        'abreviatura': data.get('abreviatura'),
        'ruta': data.get('ruta'),
        'activo': data.get('activo'),
        'modificador': data.get('modificador', 'Sistema'),
        'modificacion': now
    })
    
    if getattr(result, 'rowcount', 0) == 0:
        return jsonify({'error': 'Menú no encontrado'}), 404
    
    db.session.commit()
    
    menu = db.session.execute(
        db.text("SELECT * FROM menus WHERE id = :id"),
        {'id': id}
    ).fetchone()

    if not menu:
        return jsonify({'error': 'Menú no encontrado'}), 404

    return jsonify({
        'id': menu.id,
        'padre_id': menu.padre_id,
        'orden': menu.orden,
        'nombre': menu.nombre,
        'abreviatura': menu.abreviatura,
        'ruta': menu.ruta,
        'activo': menu.activo,
        'creador': menu.creador,
        'creacion': menu.creacion.isoformat() if menu.creacion else None,
        'modificador': menu.modificador,
        'modificacion': menu.modificacion.isoformat() if menu.modificacion else None
    })

@menus_bp.route('/api/menus/<int:id>', methods=['DELETE'])
def delete_menu(id):
    """Eliminar un menú por ID.
    ---
    tags:
      - Menús
    parameters:
      - name: id
        in: path
        type: integer
        required: true
    responses:
      200:
        description: Menú eliminado correctamente
      404:
        description: Menú no encontrado
    """
    result = db.session.execute(
        db.text("DELETE FROM menus WHERE id = :id"), 
        {'id': id}
    )
    
    if getattr(result, 'rowcount', 0) == 0:
        return jsonify({'error': 'Menú no encontrado'}), 404
    
    db.session.commit()
    return jsonify({'mensaje': 'Menú eliminado correctamente'})