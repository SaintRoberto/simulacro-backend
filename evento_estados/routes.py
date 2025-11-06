from flask import Blueprint, request, jsonify
from models import db
from datetime import datetime, timezone

evento_estados_bp = Blueprint('evento_estados', __name__)

@evento_estados_bp.route('/api/evento_estados', methods=['GET'])
def get_evento_estados():
    """Listar todos los estados de eventos registrados."""
    query = db.text("SELECT * FROM evento_estados ORDER BY id")
    result = db.session.execute(query)
    estados = []
    for row in result:
        estados.append({
            'id': row.id,
            'nombre': row.nombre,
            'descripcion': row.descripcion,
            'activo': row.activo,
            'creador': row.creador,
            'creacion': row.creacion.isoformat() if getattr(row, 'creacion', None) else None,
            'modificador': row.modificador,
            'modificacion': row.modificacion.isoformat() if getattr(row, 'modificacion', None) else None
        })
    return jsonify(estados)


@evento_estados_bp.route('/api/evento_estados/<int:id>', methods=['GET'])
def get_evento_estado(id):
    """
    Obtener un estado de evento específico por ID.

    Parámetros:
      id (int): ID del estado de evento

    Devuelve el registro correspondiente al ID especificado, incluyendo información
    de creación y modificación.

    ---
    tags:
      - Estados de Evento
    parameters:
      - name: id
        in: path
        description: Identificador del estado de evento
        required: true
        type: integer
    responses:
      200:
        description: Estado de evento encontrado
      404:
        description: Estado de evento no encontrado
    """
    estado = db.session.execute(db.text("SELECT * FROM evento_estados WHERE id = :id"), {'id': id}).fetchone()
    if estado is None:
        return jsonify({'error': 'Estado de evento no encontrado'}), 404
    return jsonify({
        'id': getattr(estado, 'id', None),
        'nombre': getattr(estado, 'nombre', None),
        'descripcion': getattr(estado, 'descripcion', None),
        'activo': getattr(estado, 'activo', None),
        'creador': getattr(estado, 'creador', None),
        'creacion': estado.creacion.isoformat() if (estado is not None and getattr(estado, 'creacion', None) is not None) else None,
        'modificador': getattr(estado, 'modificador', None),
        'modificacion': estado.modificacion.isoformat() if (estado is not None and getattr(estado, 'modificacion', None) is not None) else None
    })


@evento_estados_bp.route('/api/evento_estados', methods=['POST'])
def create_evento_estado():
    """
    Crear un nuevo estado de evento.

    Inserta un registro en `evento_estados`. Campo obligatorio: `nombre`.

    ---
    tags:
      - Estados de Evento
    consumes:
      - application/json
    responses:
      201:
        description: Estado de evento creado correctamente
      400:
        description: Datos inválidos
    """
    data = request.get_json()
    now = datetime.now(timezone.utc)
    query = db.text("""
        INSERT INTO evento_estados (nombre, descripcion, activo, creador, creacion, modificador, modificacion)
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
        return jsonify({'error': 'Fallo la creación del estado de evento'}), 500
    estado_id = row[0]
    db.session.commit()
    estado = db.session.execute(db.text("SELECT * FROM evento_estados WHERE id = :id"), {'id': estado_id}).fetchone()
    return jsonify({
        'id': getattr(estado, 'id', None),
        'nombre': getattr(estado, 'nombre', None),
        'descripcion': getattr(estado, 'descripcion', None),
        'activo': getattr(estado, 'activo', None),
        'creador': getattr(estado, 'creador', None),
        'creacion': estado.creacion.isoformat() if (estado is not None and getattr(estado, 'creacion', None) is not None) else None,
        'modificador': getattr(estado, 'modificador', None),
        'modificacion': estado.modificacion.isoformat() if (estado is not None and getattr(estado, 'modificacion', None) is not None) else None
    }), 201


@evento_estados_bp.route('/api/evento_estados/<int:id>', methods=['PUT'])
def update_evento_estado(id):
    """
    Actualizar un estado de evento existente.

    Actualiza uno o varios campos del registro existente en la tabla `evento_estados`.

    ---
    tags:
      - Estados de Evento
    parameters:
      - name: id
        in: path
        description: Identificador del estado de evento a actualizar
        required: true
        type: integer
    responses:
      200:
        description: Estado de evento actualizado correctamente
      404:
        description: Estado de evento no encontrado
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
        UPDATE evento_estados
        SET {', '.join(update_fields)}
        WHERE id = :id
    """)
    result = db.session.execute(query, params)
    if getattr(result, 'rowcount', 0) == 0:
        return jsonify({'error': 'Estado de evento no encontrado'}), 404
    db.session.commit()
    estado = db.session.execute(db.text("SELECT * FROM evento_estados WHERE id = :id"), {'id': id}).fetchone()
    return jsonify({
        'id': getattr(estado, 'id', None),
        'nombre': getattr(estado, 'nombre', None),
        'descripcion': getattr(estado, 'descripcion', None),
        'activo': getattr(estado, 'activo', None),
        'creador': getattr(estado, 'creador', None),
        'creacion': estado.creacion.isoformat() if (estado is not None and getattr(estado, 'creacion', None) is not None) else None,
        'modificador': getattr(estado, 'modificador', None),
        'modificacion': estado.modificacion.isoformat() if (estado is not None and getattr(estado, 'modificacion', None) is not None) else None
    })


@evento_estados_bp.route('/api/evento_estados/<int:id>', methods=['DELETE'])
def delete_evento_estado(id):
    """
    Eliminar un estado de evento existente.

    Elimina el registro correspondiente al ID especificado.

    ---
    tags:
      - Estados de Evento
    parameters:
      - name: id
        in: path
        description: ID del estado de evento a eliminar
        required: true
        type: integer
    responses:
      200:
        description: Estado de evento eliminado correctamente
      404:
        description: Estado de evento no encontrado
    """
    result = db.session.execute(db.text("DELETE FROM evento_estados WHERE id = :id"), {'id': id})
    if getattr(result, 'rowcount', 0) == 0:
        return jsonify({'error': 'Estado de evento no encontrado'}), 404
    db.session.commit()
    return jsonify({'mensaje': 'Estado de evento eliminado correctamente'})
