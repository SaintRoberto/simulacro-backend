from flask import Blueprint, request, jsonify
from models import db
from datetime import datetime, timezone

evento_categorias_bp = Blueprint('evento_categorias', __name__)

@evento_categorias_bp.route('/api/evento_categorias', methods=['GET'])
def get_evento_categorias():
    """Listar todas las categorías de eventos registradas."""
    query = db.text("SELECT * FROM evento_categorias ORDER BY id")
    result = db.session.execute(query)
    categorias = []
    for row in result:
        categorias.append({
            'id': row.id,
            'nombre': row.nombre,
            'descripcion': row.descripcion,
            'activo': row.activo,
            'creador': row.creador,
            'creacion': row.creacion.isoformat() if getattr(row, 'creacion', None) else None,
            'modificador': row.modificador,
            'modificacion': row.modificacion.isoformat() if getattr(row, 'modificacion', None) else None
        })
    return jsonify(categorias)


@evento_categorias_bp.route('/api/evento_categorias/<int:id>', methods=['GET'])
def get_evento_categoria(id):
    """Obtener una categoría de evento específica por ID."""
    categoria = db.session.execute(db.text("SELECT * FROM evento_categorias WHERE id = :id"), {'id': id}).fetchone()
    if categoria is None:
        return jsonify({'error': 'Categoría de evento no encontrada'}), 404
    return jsonify({
        'id': getattr(categoria, 'id', None),
        'nombre': getattr(categoria, 'nombre', None),
        'descripcion': getattr(categoria, 'descripcion', None),
        'activo': getattr(categoria, 'activo', None),
        'creador': getattr(categoria, 'creador', None),
        'creacion': categoria.creacion.isoformat() if (categoria is not None and getattr(categoria, 'creacion', None) is not None) else None,
        'modificador': getattr(categoria, 'modificador', None),
        'modificacion': categoria.modificacion.isoformat() if (categoria is not None and getattr(categoria, 'modificacion', None) is not None) else None
    })


@evento_categorias_bp.route('/api/evento_categorias', methods=['POST'])
def create_evento_categoria():
    """Crear una nueva categoría de evento."""
    data = request.get_json()
    now = datetime.now(timezone.utc)
    query = db.text("""
        INSERT INTO evento_categorias (nombre, descripcion, activo, creador, creacion, modificador, modificacion)
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
        db.session.rollback()
        return jsonify({'error': 'Fallo la creación de la categoría de evento'}), 500
    categoria_id = row[0]
    db.session.commit()
    categoria = db.session.execute(db.text("SELECT * FROM evento_categorias WHERE id = :id"), {'id': categoria_id}).fetchone()
    return jsonify({
        'id': getattr(categoria, 'id', None),
        'nombre': getattr(categoria, 'nombre', None),
        'descripcion': getattr(categoria, 'descripcion', None),
        'activo': getattr(categoria, 'activo', None),
        'creador': getattr(categoria, 'creador', None),
        'creacion': categoria.creacion.isoformat() if (categoria is not None and getattr(categoria, 'creacion', None) is not None) else None,
        'modificador': getattr(categoria, 'modificador', None),
        'modificacion': categoria.modificacion.isoformat() if (categoria is not None and getattr(categoria, 'modificacion', None) is not None) else None
    }), 201


@evento_categorias_bp.route('/api/evento_categorias/<int:id>', methods=['PUT'])
def update_evento_categoria(id):
    """Actualizar una categoría de evento existente."""
    data = request.get_json()
    now = datetime.now(timezone.utc)
    update_fields = []
    params = {'id': id, 'modificador': data.get('modificador', 'Sistema'), 'modificacion': now}
    fields = ['nombre', 'descripcion', 'activo']
    for field in fields:
        if field in data:
            update_fields.append(f"{field} = :{field}")
            params[field] = data[field]
    update_fields.append('modificador = :modificador')
    update_fields.append('modificacion = :modificacion')
    query = db.text(f"""
        UPDATE evento_categorias
        SET {', '.join(update_fields)}
        WHERE id = :id
    """)
    result = db.session.execute(query, params)
    if getattr(result, 'rowcount', 0) == 0:
        return jsonify({'error': 'Categoría de evento no encontrada'}), 404
    db.session.commit()
    categoria = db.session.execute(db.text("SELECT * FROM evento_categorias WHERE id = :id"), {'id': id}).fetchone()
    return jsonify({
        'id': getattr(categoria, 'id', None),
        'nombre': getattr(categoria, 'nombre', None),
        'descripcion': getattr(categoria, 'descripcion', None),
        'activo': getattr(categoria, 'activo', None),
        'creador': getattr(categoria, 'creador', None),
        'creacion': categoria.creacion.isoformat() if (categoria is not None and getattr(categoria, 'creacion', None) is not None) else None,
        'modificador': getattr(categoria, 'modificador', None),
        'modificacion': categoria.modificacion.isoformat() if (categoria is not None and getattr(categoria, 'modificacion', None) is not None) else None
    })


@evento_categorias_bp.route('/api/evento_categorias/<int:id>', methods=['DELETE'])
def delete_evento_categoria(id):
    """Eliminar una categoría de evento existente."""
    result = db.session.execute(db.text("DELETE FROM evento_categorias WHERE id = :id"), {'id': id})
    if getattr(result, 'rowcount', 0) == 0:
        return jsonify({'error': 'Categoría de evento no encontrada'}), 404
    db.session.commit()
    return jsonify({'mensaje': 'Categoría de evento eliminada correctamente'})
