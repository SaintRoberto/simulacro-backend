from flask import Blueprint, request, jsonify
from models import db
from datetime import datetime, timezone

evento_origenes_bp = Blueprint('evento_origenes', __name__)

@evento_origenes_bp.route('/api/evento_origenes', methods=['GET'])
def get_evento_origenes():
    """
    Listar todos los orígenes de eventos registrados.
    ---
    tags:
      - Orígenes de Evento
    responses:
      200:
        description: Lista de orígenes de eventos obtenida correctamente
    """
    query = db.text("SELECT * FROM evento_origenes ORDER BY id")
    result = db.session.execute(query)
    origenes = []
    for row in result:
        origenes.append({
            'id': row.id,
            'nombre': row.nombre,
            'descripcion': row.descripcion,
            'activo': row.activo,
            'creador': row.creador,
            'creacion': row.creacion.isoformat() if row.creacion else None,
            'modificador': row.modificador,
            'modificacion': row.modificacion.isoformat() if row.modificacion else None
        })
    return jsonify(origenes)


@evento_origenes_bp.route('/api/evento_origenes/<int:id>', methods=['GET'])
def get_evento_origen(id):
    """
    Obtener información detallada de un origen de evento específico.
    ---
    tags:
      - Orígenes de Evento
    parameters:
      - name: id
        in: path
        description: ID del origen de evento
        required: true
        type: integer
    responses:
      200:
        description: Origen de evento encontrado
      404:
        description: No se encontró el origen de evento solicitado
    """
    query = db.text("SELECT * FROM evento_origenes WHERE id = :id")
    result = db.session.execute(query, {'id': id}).fetchone()
    if result is None:
        return jsonify({'error': 'Origen de evento no encontrado'}), 404
    return jsonify({
        'id': result.id,
        'nombre': result.nombre,
        'descripcion': result.descripcion,
        'activo': result.activo,
        'creador': result.creador,
        'creacion': result.creacion.isoformat() if result.creacion else None,
        'modificador': result.modificador,
        'modificacion': result.modificacion.isoformat() if result.modificacion else None
    })


@evento_origenes_bp.route('/api/evento_origenes', methods=['POST'])
def create_evento_origen():
    """
    Crear un nuevo origen de evento.
    ---
    tags:
      - Orígenes de Evento
    consumes:
      - application/json
    responses:
      201:
        description: Origen de evento creado correctamente
      400:
        description: Datos inválidos
    """
    data = request.get_json()
    now = datetime.now(timezone.utc)
    query = db.text("""
        INSERT INTO evento_origenes (nombre, descripcion, activo, creador, creacion, modificador, modificacion)
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
        return jsonify({'error': 'Fallo la creación del origen de evento'}), 500
    origen_id = row[0]
    db.session.commit()
    origen = db.session.execute(db.text("SELECT * FROM evento_origenes WHERE id = :id"), {'id': origen_id}).fetchone()
    return jsonify({
        'id': getattr(origen, 'id', None),
        'nombre': getattr(origen, 'nombre', None),
        'descripcion': getattr(origen, 'descripcion', None),
        'activo': getattr(origen, 'activo', None),
        'creador': getattr(origen, 'creador', None),
        'creacion': origen.creacion.isoformat() if (origen is not None and getattr(origen, 'creacion', None) is not None) else None,
        'modificador': getattr(origen, 'modificador', None),
        'modificacion': origen.modificacion.isoformat() if (origen is not None and getattr(origen, 'modificacion', None) is not None) else None
    }), 201


@evento_origenes_bp.route('/api/evento_origenes/<int:id>', methods=['PUT'])
def update_evento_origen(id):
    """
    Actualizar un origen de evento existente.
    ---
    tags:
      - Orígenes de Evento
    consumes:
      - application/json
    responses:
      200:
        description: Origen de evento actualizado correctamente
      404:
        description: Origen de evento no encontrado
    """
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
        UPDATE evento_origenes
        SET {', '.join(update_fields)}
        WHERE id = :id
    """)
    result = db.session.execute(query, params)
    if getattr(result, 'rowcount', 0) == 0:
        return jsonify({'error': 'Origen de evento no encontrado'}), 404
    db.session.commit()
    origen = db.session.execute(db.text("SELECT * FROM evento_origenes WHERE id = :id"), {'id': id}).fetchone()
    return jsonify({
        'id': getattr(origen, 'id', None),
        'nombre': getattr(origen, 'nombre', None),
        'descripcion': getattr(origen, 'descripcion', None),
        'activo': getattr(origen, 'activo', None),
        'creador': getattr(origen, 'creador', None),
        'creacion': origen.creacion.isoformat() if (origen is not None and getattr(origen, 'creacion', None) is not None) else None,
        'modificador': getattr(origen, 'modificador', None),
        'modificacion': origen.modificacion.isoformat() if (origen is not None and getattr(origen, 'modificacion', None) is not None) else None
    })


@evento_origenes_bp.route('/api/evento_origenes/<int:id>', methods=['DELETE'])
def delete_evento_origen(id):
    """
    Eliminar un origen de evento.
    ---
    tags:
      - Orígenes de Evento
    responses:
      200:
        description: Origen de evento eliminado correctamente
      404:
        description: Origen de evento no encontrado
    """
    result = db.session.execute(db.text("DELETE FROM evento_origenes WHERE id = :id"), {'id': id})
    if getattr(result, 'rowcount', 0) == 0:
        return jsonify({'error': 'Origen de evento no encontrado'}), 404
    db.session.commit()
    return jsonify({'mensaje': 'Origen de evento eliminado correctamente'})
