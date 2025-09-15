from flask import request, jsonify
from institucion_categorias import institucion_categorias_bp
from models import db
from datetime import datetime, timezone

@institucion_categorias_bp.route('/api/institucion-categorias', methods=['GET'])
def get_institucion_categorias():
    result = db.session.execute(db.text("SELECT * FROM institucion_categorias"))
    categorias = []
    for row in result:
        categorias.append({
            'id': row.id,
            'nombre': row.nombre,
            'descripcion': row.descripcion,
            'estado': row.estado,
            'creador': row.creador,
            'creacion': row.creacion.isoformat() if row.creacion else None,
            'modificador': row.modificador,
            'modificacion': row.modificacion.isoformat() if row.modificacion else None
        })
    return jsonify(categorias)

@institucion_categorias_bp.route('/api/institucion-categorias', methods=['POST'])
def create_institucion_categoria():
    data = request.get_json()
    now = datetime.now(timezone.utc)
    
    query = db.text("""
        INSERT INTO institucion_categorias (nombre, descripcion, estado, creador, creacion, modificador, modificacion)
        VALUES (:nombre, :descripcion, :estado, :creador, :creacion, :modificador, :modificacion)
        RETURNING id
    """)
    
    result = db.session.execute(query, {
        'nombre': data['nombre'],
        'descripcion': data.get('descripcion'),
        'estado': data.get('estado', True),
        'creador': data.get('creador', 'Sistema'),
        'creacion': now,
        'modificador': data.get('creador', 'Sistema'),
        'modificacion': now
    })
    
    categoria_id = result.fetchone()[0]
    db.session.commit()
    
    categoria = db.session.execute(
        db.text("SELECT * FROM institucion_categorias WHERE id = :id"), 
        {'id': categoria_id}
    ).fetchone()
    
    return jsonify({
        'id': categoria.id,
        'nombre': categoria.nombre,
        'descripcion': categoria.descripcion,
        'estado': categoria.estado,
        'creador': categoria.creador,
        'creacion': categoria.creacion.isoformat() if categoria.creacion else None,
        'modificador': categoria.modificador,
        'modificacion': categoria.modificacion.isoformat() if categoria.modificacion else None
    }), 201

@institucion_categorias_bp.route('/api/institucion-categorias/<int:id>', methods=['GET'])
def get_institucion_categoria(id):
    result = db.session.execute(
        db.text("SELECT * FROM institucion_categorias WHERE id = :id"), 
        {'id': id}
    )
    categoria = result.fetchone()
    
    if not categoria:
        return jsonify({'error': 'Categoría no encontrada'}), 404
    
    return jsonify({
        'id': categoria.id,
        'nombre': categoria.nombre,
        'descripcion': categoria.descripcion,
        'estado': categoria.estado,
        'creador': categoria.creador,
        'creacion': categoria.creacion.isoformat() if categoria.creacion else None,
        'modificador': categoria.modificador,
        'modificacion': categoria.modificacion.isoformat() if categoria.modificacion else None
    })

@institucion_categorias_bp.route('/api/institucion-categorias/<int:id>', methods=['PUT'])
def update_institucion_categoria(id):
    data = request.get_json()
    now = datetime.now(timezone.utc)
    
    query = db.text("""
        UPDATE institucion_categorias 
        SET nombre = :nombre, 
            descripcion = :descripcion, 
            estado = :estado, 
            modificador = :modificador, 
            modificacion = :modificacion
        WHERE id = :id
    """)
    
    result = db.session.execute(query, {
        'id': id,
        'nombre': data.get('nombre'),
        'descripcion': data.get('descripcion'),
        'estado': data.get('estado'),
        'modificador': data.get('modificador', 'Sistema'),
        'modificacion': now
    })
    
    if result.rowcount == 0:
        return jsonify({'error': 'Categoría no encontrada'}), 404
    
    db.session.commit()
    
    categoria = db.session.execute(
        db.text("SELECT * FROM institucion_categorias WHERE id = :id"), 
        {'id': id}
    ).fetchone()
    
    return jsonify({
        'id': categoria.id,
        'nombre': categoria.nombre,
        'descripcion': categoria.descripcion,
        'estado': categoria.estado,
        'creador': categoria.creador,
        'creacion': categoria.creacion.isoformat() if categoria.creacion else None,
        'modificador': categoria.modificador,
        'modificacion': categoria.modificacion.isoformat() if categoria.modificacion else None
    })

@institucion_categorias_bp.route('/api/institucion-categorias/<int:id>', methods=['DELETE'])
def delete_institucion_categoria(id):
    result = db.session.execute(
        db.text("DELETE FROM institucion_categorias WHERE id = :id"), 
        {'id': id}
    )
    
    if result.rowcount == 0:
        return jsonify({'error': 'Categoría no encontrada'}), 404
    
    db.session.commit()
    return jsonify({'mensaje': 'Categoría eliminada correctamente'})
