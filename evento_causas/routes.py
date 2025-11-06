from flask import Blueprint, request, jsonify
from models import db
from datetime import datetime, timezone

evento_causas_bp = Blueprint('evento_causas', __name__)

@evento_causas_bp.route('/api/evento_causas', methods=['GET'])
def get_evento_causas():
    """Listar todas las causas de eventos registradas."""
    query = db.text("SELECT * FROM evento_causas ORDER BY id")
    result = db.session.execute(query)
    causas = []
    for row in result:
        causas.append({
            'id': row.id,
            'nombre': row.nombre,
            'descripcion': row.descripcion,
            'activo': row.activo,
            'creador': row.creador,
            'creacion': row.creacion.isoformat() if getattr(row, 'creacion', None) else None,
            'modificador': row.modificador,
            'modificacion': row.modificacion.isoformat() if getattr(row, 'modificacion', None) else None
        })
    return jsonify(causas)


@evento_causas_bp.route('/api/evento_causas/<int:id>', methods=['GET'])
def get_evento_causa(id):
    """Obtener una causa de evento específica por ID."""
    causa = db.session.execute(db.text("SELECT * FROM evento_causas WHERE id = :id"), {'id': id}).fetchone()
    if causa is None:
        return jsonify({'error': 'Causa de evento no encontrada'}), 404
    return jsonify({
        'id': getattr(causa, 'id', None),
        'nombre': getattr(causa, 'nombre', None),
        'descripcion': getattr(causa, 'descripcion', None),
        'activo': getattr(causa, 'activo', None),
        'creador': getattr(causa, 'creador', None),
        'creacion': causa.creacion.isoformat() if (causa is not None and getattr(causa, 'creacion', None) is not None) else None,
        'modificador': getattr(causa, 'modificador', None),
        'modificacion': causa.modificacion.isoformat() if (causa is not None and getattr(causa, 'modificacion', None) is not None) else None
    })


@evento_causas_bp.route('/api/evento_causas', methods=['POST'])
def create_evento_causa():
    """Crear una nueva causa de evento."""
    data = request.get_json()
    now = datetime.now(timezone.utc)
    query = db.text("""
        INSERT INTO evento_causas (nombre, descripcion, activo, creador, creacion, modificador, modificacion)
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
        return jsonify({'error': 'Fallo la creación de la causa de evento'}), 500
    causa_id = row[0]
    db.session.commit()
    causa = db.session.execute(db.text("SELECT * FROM evento_causas WHERE id = :id"), {'id': causa_id}).fetchone()
    return jsonify({
        'id': getattr(causa, 'id', None),
        'nombre': getattr(causa, 'nombre', None),
        'descripcion': getattr(causa, 'descripcion', None),
        'activo': getattr(causa, 'activo', None),
        'creador': getattr(causa, 'creador', None),
        'creacion': causa.creacion.isoformat() if (causa is not None and getattr(causa, 'creacion', None) is not None) else None,
        'modificador': getattr(causa, 'modificador', None),
        'modificacion': causa.modificacion.isoformat() if (causa is not None and getattr(causa, 'modificacion', None) is not None) else None
    }), 201


@evento_causas_bp.route('/api/evento_causas/<int:id>', methods=['PUT'])
def update_evento_causa(id):
    """Actualizar una causa de evento existente."""
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
        UPDATE evento_causas
        SET {', '.join(update_fields)}
        WHERE id = :id
    """)
    result = db.session.execute(query, params)
    if getattr(result, 'rowcount', 0) == 0:
        return jsonify({'error': 'Causa de evento no encontrada'}), 404
    db.session.commit()
    causa = db.session.execute(db.text("SELECT * FROM evento_causas WHERE id = :id"), {'id': id}).fetchone()
    return jsonify({
        'id': getattr(causa, 'id', None),
        'nombre': getattr(causa, 'nombre', None),
        'descripcion': getattr(causa, 'descripcion', None),
        'activo': getattr(causa, 'activo', None),
        'creador': getattr(causa, 'creador', None),
        'creacion': causa.creacion.isoformat() if (causa is not None and getattr(causa, 'creacion', None) is not None) else None,
        'modificador': getattr(causa, 'modificador', None),
        'modificacion': causa.modificacion.isoformat() if (causa is not None and getattr(causa, 'modificacion', None) is not None) else None
    })


@evento_causas_bp.route('/api/evento_causas/<int:id>', methods=['DELETE'])
def delete_evento_causa(id):
    """Eliminar una causa de evento existente."""
    result = db.session.execute(db.text("DELETE FROM evento_causas WHERE id = :id"), {'id': id})
    if getattr(result, 'rowcount', 0) == 0:
        return jsonify({'error': 'Causa de evento no encontrada'}), 404
    db.session.commit()
    return jsonify({'mensaje': 'Causa de evento eliminada correctamente'})
