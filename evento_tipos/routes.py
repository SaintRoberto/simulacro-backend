from flask import Blueprint, request, jsonify
from models import db
from datetime import datetime, timezone

evento_tipos_bp = Blueprint('evento_tipos', __name__)

@evento_tipos_bp.route('/api/evento_tipos', methods=['GET'])
def get_evento_tipos():
    """
    Listar todos los tipos de eventos registrados.

    ---
    tags:
      - Tipos de Evento
    responses:
      200:
        description: Lista de tipos de eventos obtenida correctamente
    """
    query = db.text("SELECT * FROM evento_tipos ORDER BY id")
    result = db.session.execute(query)
    tipos = []
    for row in result:
        tipos.append({
            'id': row.id,
            'nombre': row.nombre,
            'descripcion': row.descripcion,
            'activo': row.activo,
            'creador': row.creador,
            'creacion': row.creacion.isoformat() if row.creacion else None,
            'modificador': row.modificador,
            'modificacion': row.modificacion.isoformat() if row.modificacion else None,
            'identificador': row.identificador
        })
    return jsonify(tipos)


@evento_tipos_bp.route('/api/evento_tipos/<int:id>', methods=['GET'])
def get_evento_tipo(id):
    """
    Obtener información detallada de un tipo de evento específico.

    ---
    tags:
      - Tipos de Evento
    parameters:
      - name: id
        in: path
        description: ID del tipo de evento
        required: true
        type: integer
    responses:
      200:
        description: Tipo de evento encontrado y devuelto correctamente
      404:
        description: No se encontró el tipo de evento solicitado
    """
    query = db.text("SELECT * FROM evento_tipos WHERE id = :id")
    result = db.session.execute(query, {'id': id}).fetchone()
    if result is None:
        return jsonify({'error': 'Tipo de evento no encontrado'}), 404
    return jsonify({
        'id': result.id,
        'nombre': result.nombre,
        'descripcion': result.descripcion,
        'activo': result.activo,
        'creador': result.creador,
        'creacion': result.creacion.isoformat() if getattr(result, 'creacion', None) else None,
        'modificador': result.modificador,
        'modificacion': result.modificacion.isoformat() if getattr(result, 'modificacion', None) else None,
        'identificador': getattr(result, 'identificador', None)
    })


@evento_tipos_bp.route('/api/evento_tipos', methods=['POST'])
def create_evento_tipo():
    """
    Crear un nuevo tipo de evento.

    Inserta un nuevo registro en la tabla `evento_tipos`.
    Los campos requeridos son `nombre`; los demás son opcionales.

    ---
    tags:
      - Tipos de Evento
    consumes:
      - application/json
    responses:
      201:
        description: Tipo de evento creado correctamente
      400:
        description: Error en los datos enviados
    """
    data = request.get_json()
    now = datetime.now(timezone.utc)
    query = db.text("""
        INSERT INTO evento_tipos (nombre, descripcion, activo, creador, creacion, modificador, modificacion, identificador)
        VALUES (:nombre, :descripcion, :activo, :creador, :creacion, :modificador, :modificacion, :identificador)
        RETURNING id
    """)
    result = db.session.execute(query, {
        'nombre': data['nombre'],
        'descripcion': data.get('descripcion'),
        'activo': data.get('activo', True),
        'creador': data.get('creador', 'Sistema'),
        'creacion': now,
        'modificador': data.get('modificador', data.get('creador', 'Sistema')),
        'modificacion': now,
        'identificador': data.get('identificador')
    })
    row = result.fetchone()
    if row is None:
        db.session.rollback()
        return jsonify({'error': 'Fallo la creación del tipo de evento'}), 500
    tipo_id = row[0]
    db.session.commit()
    tipo = db.session.execute(db.text("SELECT * FROM evento_tipos WHERE id = :id"), {'id': tipo_id}).fetchone()
    return jsonify({
        'id': getattr(tipo, 'id', None),
        'nombre': getattr(tipo, 'nombre', None),
        'descripcion': getattr(tipo, 'descripcion', None),
        'activo': getattr(tipo, 'activo', None),
        'creador': getattr(tipo, 'creador', None),
        'creacion': tipo.creacion.isoformat() if (tipo is not None and getattr(tipo, 'creacion', None)) else None,
        'modificador': getattr(tipo, 'modificador', None),
        'modificacion': tipo.modificacion.isoformat() if (tipo is not None and getattr(tipo, 'modificacion', None) is not None) else None,
        'identificador': getattr(tipo, 'identificador', None)
    }), 201


@evento_tipos_bp.route('/api/evento_tipos/<int:id>', methods=['PUT'])
def update_evento_tipo(id):
    """Actualizar un tipo de evento."""
    data = request.get_json()
    now = datetime.now(timezone.utc)
    update_fields = []
    params = {'id': id, 'modificador': data.get('modificador', 'Sistema'), 'modificacion': now}
    fields = ['nombre', 'descripcion', 'activo', 'identificador']
    for field in fields:
        if field in data:
            update_fields.append(f"{field} = :{field}")
            params[field] = data[field]
    update_fields.append('modificador = :modificador')
    update_fields.append('modificacion = :modificacion')
    query = db.text(f"""
        UPDATE evento_tipos
        SET {', '.join(update_fields)}
        WHERE id = :id
    """)
    result = db.session.execute(query, params)
    if getattr(result, 'rowcount', 0) == 0:
        return jsonify({'error': 'Tipo de evento no encontrado'}), 404
    db.session.commit()
    tipo = db.session.execute(db.text("SELECT * FROM evento_tipos WHERE id = :id"), {'id': id}).fetchone()
    if tipo is None:
        return jsonify({'error': 'Tipo de evento no encontrado después de actualizar'}), 404
    return jsonify({
        'id': getattr(tipo, 'id', None),
        'nombre': getattr(tipo, 'nombre', None),
        'descripcion': getattr(tipo, 'descripcion', None),
        'activo': getattr(tipo, 'activo', None),
        'creador': getattr(tipo, 'creador', None),
        'creacion': tipo.creacion.isoformat() if getattr(tipo, 'creacion', None) else None,
        'modificador': getattr(tipo, 'modificador', None),
        'modificacion': tipo.modificacion.isoformat() if getattr(tipo, 'modificacion', None) else None,
        'identificador': getattr(tipo, 'identificador', None)
    })


@evento_tipos_bp.route('/api/evento_tipos/<int:id>', methods=['DELETE'])
def delete_evento_tipo(id):
    """Eliminar un tipo de evento."""
    result = db.session.execute(db.text("DELETE FROM evento_tipos WHERE id = :id"), {'id': id})
    if getattr(result, 'rowcount', 0) == 0:
        return jsonify({'error': 'Tipo de evento no encontrado'}), 404
    db.session.commit()
    return jsonify({'mensaje': 'Tipo de evento eliminado correctamente'})
