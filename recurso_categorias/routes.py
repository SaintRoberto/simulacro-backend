from flask import request, jsonify
from recurso_categorias import recurso_categorias_bp
from models import db
from datetime import datetime, timezone

@recurso_categorias_bp.route('/api/recurso-categorias', methods=['GET'])
def get_recurso_categorias():
    """Listar categorías de recursos
    ---
    tags:
      - Recurso Categorías
    responses:
      200:
        description: Lista de categorías de recursos
        schema:
          type: array
          items:
            type: object
            properties:
              id: {type: integer}
              nombre: {type: string}
              descripcion: {type: string}
              activo: {type: boolean}
              creador: {type: string}
              creacion: {type: string}
              modificador: {type: string}
              modificacion: {type: string}
    """
    result = db.session.execute(db.text("SELECT * FROM recurso_categorias"))
    categorias = []
    for row in result:
        categorias.append({
            'id': row.id,
            'nombre': row.nombre,
            'descripcion': row.descripcion,
            'activo': row.activo,
            'creador': row.creador,
            'creacion': row.creacion.isoformat() if row.creacion else None,
            'modificador': row.modificador,
            'modificacion': row.modificacion.isoformat() if row.modificacion else None
        })
    return jsonify(categorias)

@recurso_categorias_bp.route('/api/recurso-categorias', methods=['POST'])
def create_recurso_categoria():
    """Crear categoría de recurso
    ---
    tags:
      - Recurso Categorías
    consumes:
      - application/json
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          required: [nombre]
          properties:
            nombre: {type: string}
            descripcion: {type: string}
            activo: {type: boolean}
            creador: {type: string}
    responses:
      201:
        description: Categoría de recurso creada
    """
    data = request.get_json()
    if not data or 'nombre' not in data:
        return jsonify({'error': 'El campo "nombre" es requerido'}), 400

    now = datetime.now(timezone.utc)

    query = db.text("""
        INSERT INTO recurso_categorias (nombre, descripcion, activo, creador, creacion, modificador, modificacion)
        VALUES (:nombre, :descripcion, :activo, :creador, :creacion, :modificador, :modificacion)
        RETURNING id
    """)

    result = db.session.execute(query, {
        'nombre': data.get('nombre'),
        'descripcion': data.get('descripcion'),
        'activo': data.get('activo', True),
        'creador': data.get('creador', 'Sistema'),
        'creacion': now,
        'modificador': data.get('creador', 'Sistema'),
        'modificacion': now
    })
    
    row = result.fetchone()
    if row is None:
        return jsonify({'error': 'Not found'}), 404
    categoria_id = row[0]
    db.session.commit()
    
    categoria = db.session.execute(
        db.text("SELECT * FROM recurso_categorias WHERE id = :id"),
        {'id': categoria_id}
    ).fetchone()
    
    if not categoria:
        # This is unexpected after a successful INSERT RETURNING id, but handle defensively
        return jsonify({'error': 'Categoría no encontrada después de crear'}), 500

    return jsonify({
        'id': categoria.id,
        'nombre': categoria.nombre,
        'descripcion': categoria.descripcion,
        'activo': categoria.activo,
        'creador': categoria.creador,
        'creacion': categoria.creacion.isoformat() if categoria.creacion else None,
        'modificador': categoria.modificador,
        'modificacion': categoria.modificacion.isoformat() if categoria.modificacion else None
    }), 201

@recurso_categorias_bp.route('/api/recurso-categorias/<int:id>', methods=['GET'])
def get_recurso_categoria(id):
    """Obtener categoría de recurso por ID
    ---
    tags:
      - Recurso Categorías
    parameters:
      - name: id
        in: path
        type: integer
        required: true
    responses:
      200:
        description: Categoría de recurso
      404:
        description: No encontrada
    """
    result = db.session.execute(
        db.text("SELECT * FROM recurso_categorias WHERE id = :id"), 
        {'id': id}
    )
    categoria = result.fetchone()
    
    if not categoria:
        return jsonify({'error': 'Categoría no encontrada'}), 404
    
    return jsonify({
        'id': categoria.id,
        'nombre': categoria.nombre,
        'descripcion': categoria.descripcion,
        'activo': categoria.activo,
        'creador': categoria.creador,
        'creacion': categoria.creacion.isoformat() if categoria.creacion else None,
        'modificador': categoria.modificador,
        'modificacion': categoria.modificacion.isoformat() if categoria.modificacion else None
    })

@recurso_categorias_bp.route('/api/recurso-categorias/<int:id>', methods=['PUT'])
def update_recurso_categoria(id):
    """Actualizar categoría de recurso
    ---
    tags:
      - Recurso Categorías
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
            descripcion: {type: string}
            activo: {type: boolean}
            modificador: {type: string}
    responses:
      200:
        description: Categoría de recurso actualizada
      404:
        description: No encontrada
    """
    data = request.get_json()
    now = datetime.now(timezone.utc)
    
    query = db.text("""
        UPDATE recurso_categorias 
        SET nombre = :nombre, 
            descripcion = :descripcion, 
            activo = :activo, 
            modificador = :modificador, 
            modificacion = :modificacion
        WHERE id = :id
    """)
    
    result = db.session.execute(query, {
        'id': id,
        'nombre': data.get('nombre'),
        'descripcion': data.get('descripcion'),
        'activo': data.get('activo'),
        'modificador': data.get('modificador', 'Sistema'),
        'modificacion': now
    })
    
    if getattr(result, 'rowcount', 0) == 0:
        return jsonify({'error': 'Categoría no encontrada'}), 404
    
    db.session.commit()
    
    categoria = db.session.execute(
        db.text("SELECT * FROM recurso_categorias WHERE id = :id"),
        {'id': id}
    ).fetchone()
    
    if not categoria:
        # Should be rare because we checked rowcount earlier, but check defensively
        return jsonify({'error': 'Categoría no encontrada después de actualizar'}), 404

    return jsonify({
        'id': categoria.id,
        'nombre': categoria.nombre,
        'descripcion': categoria.descripcion,
        'activo': categoria.activo,
        'creador': categoria.creador,
        'creacion': categoria.creacion.isoformat() if categoria.creacion else None,
        'modificador': categoria.modificador,
        'modificacion': categoria.modificacion.isoformat() if categoria.modificacion else None
    })

@recurso_categorias_bp.route('/api/recurso-categorias/<int:id>', methods=['DELETE'])
def delete_recurso_categoria(id):
    """Eliminar categoría de recurso
    ---
    tags:
      - Recurso Categorías
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
        db.text("DELETE FROM recurso_categorias WHERE id = :id"), 
        {'id': id}
    )
    
    if getattr(result, 'rowcount', 0) == 0:
        return jsonify({'error': 'Categoría no encontrada'}), 404
    
    db.session.commit()
    return jsonify({'mensaje': 'Categoría eliminada correctamente'})
