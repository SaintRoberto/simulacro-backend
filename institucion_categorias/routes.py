from flask import request, jsonify
from institucion_categorias import institucion_categorias_bp
from models import db
from datetime import datetime, timezone

from utils.db_helpers import check_row_or_abort
@institucion_categorias_bp.route('/api/institucion-categorias', methods=['GET'])
def get_institucion_categorias():
    result = db.session.execute(db.text("SELECT * FROM institucion_categorias"))
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

@institucion_categorias_bp.route('/api/institucion-categorias', methods=['POST'])
def create_institucion_categoria():
    data = request.get_json() or {}
    if not data.get('nombre'):
        return jsonify({'error': 'El campo "nombre" es obligatorio'}), 400
    now = datetime.now(timezone.utc)
    
    query = db.text("""
        INSERT INTO institucion_categorias (nombre, descripcion, activo, creador, creacion, modificador, modificacion)
        VALUES (:nombre, :descripcion, :activo, :creador, :creacion, :modificador, :modificacion)
        RETURNING id
    """)
    
    result = db.session.execute(query, {
        'nombre': data['nombre'],
        'descripcion': data.get('descripcion'),
        'activo': data.get('activo', True),
        'creador': data.get('creador', 'Sistema'),
        'creacion': now,
        'modificador': data.get('modificador', data.get('creador', 'Sistema')),
        'modificacion': now
    })
    
    row = result.fetchone()
    if row is None:
        return jsonify({'error': 'Not found'}), 404
    categoria_id = row[0]
    db.session.commit()
    
    categoria = db.session.execute(
        db.text("SELECT * FROM institucion_categorias WHERE id = :id"),
        {'id': categoria_id}
    ).fetchone()
    
    if categoria is None:
        return jsonify({'error': 'Categoría no encontrada después de creación'}), 404
    
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
        'activo': categoria.activo,
        'creador': categoria.creador,
        'creacion': categoria.creacion.isoformat() if categoria.creacion else None,
        'modificador': categoria.modificador,
        'modificacion': categoria.modificacion.isoformat() if categoria.modificacion else None
    })

@institucion_categorias_bp.route('/api/institucion-categorias/<int:id>', methods=['PUT'])
def update_institucion_categoria(id):
    data = request.get_json() or {}
    now = datetime.now(timezone.utc)
    
    query = db.text("""
        UPDATE institucion_categorias
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
        db.text("SELECT * FROM institucion_categorias WHERE id = :id"),
        {'id': id}
    ).fetchone()
    
    if categoria is None:
        # Defensive: if the row can't be found after update, report 404
        return jsonify({'error': 'Categoría no encontrada'}), 404
    # Inform static type checkers that `categoria` cannot be None beyond this point.
    # This avoids warnings like "attribute 'id' is not known on None".
    assert categoria is not None
    
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

@institucion_categorias_bp.route('/api/institucion-categorias/<int:id>', methods=['DELETE'])
def delete_institucion_categoria(id):
    result = db.session.execute(
        db.text("DELETE FROM institucion_categorias WHERE id = :id"), 
        {'id': id}
    )
    
    if getattr(result, 'rowcount', 0) == 0:
        return jsonify({'error': 'Categoría no encontrada'}), 404
    
    db.session.commit()
    return jsonify({'mensaje': 'Categoría eliminada correctamente'})
