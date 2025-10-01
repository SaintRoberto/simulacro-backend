from flask import request, jsonify
from coes import coes_bp
from models import db
from datetime import datetime, timezone
@coes_bp.route('/api/coes', methods=['GET'])
def get_coes():
    result = db.session.execute(db.text("SELECT * FROM coes"))
    coes = []
    for row in result:
        coes.append({
            'id': row.id,
            'nombre': row.nombre,
            'siglas': row.siglas,
            'descripcion': row.descripcion,
            'activo': row.activo,
            'creador': row.creador,
            'creacion': row.creacion.isoformat() if row.creacion else None,
            'modificador': row.modificador,
            'modificacion': row.modificacion.isoformat() if row.modificacion else None
        })
    return jsonify(coes)

@coes_bp.route('/api/coes', methods=['POST'])
def create_coe():
    data = request.get_json()
    # Validate required fields to avoid KeyError and provide clearer errors to clients
    if not data or 'nombre' not in data or 'siglas' not in data:
        return jsonify({'error': 'Campos requeridos: nombre y siglas'}), 400

    now = datetime.now(timezone.utc)
    
    query = db.text("""
        INSERT INTO coes (nombre, siglas, descripcion, activo, creador, creacion, modificador, modificacion)
        VALUES (:nombre, :siglas, :descripcion, :activo, :creador, :creacion, :modificador, :modificacion)
        RETURNING id
    """)
    
    result = db.session.execute(query, {
        'nombre': data['nombre'],
        'siglas': data['siglas'],
        'descripcion': data.get('descripcion'),
        'activo': data.get('activo', True),
        'creador': data.get('creador', 'Sistema'),
        'creacion': now,
        'modificador': data.get('creador', 'Sistema'),
        'modificacion': now
    })
    
    row = result.fetchone()
    if row is None:
        # If INSERT didn't return an id, rollback and return 500
        db.session.rollback()
        return jsonify({'error': 'Inserción fallida'}), 500

    coe_id = row[0]
    db.session.commit()
    
    coe = db.session.execute(
        db.text("SELECT * FROM coes WHERE id = :id"),
        {'id': coe_id}
    ).fetchone()
    
    # Defensive check: ensure coe is not None before accessing attributes
    if not coe:
        # Fallback: return the created id and the supplied data (useful if the SELECT failed)
        return jsonify({
            'id': coe_id,
            'nombre': data.get('nombre'),
            'siglas': data.get('siglas'),
            'descripcion': data.get('descripcion'),
            'activo': data.get('activo', True),
            'creador': data.get('creador', 'Sistema'),
            'creacion': now.isoformat(),
            'modificador': data.get('creador', 'Sistema'),
            'modificacion': now.isoformat()
        }), 201

    return jsonify({
        'id': coe.id,
        'nombre': coe.nombre,
        'siglas': coe.siglas,
        'descripcion': coe.descripcion,
        'activo': coe.activo,
        'creador': coe.creador,
        'creacion': coe.creacion.isoformat() if coe.creacion else None,
        'modificador': coe.modificador,
        'modificacion': coe.modificacion.isoformat() if coe.modificacion else None
    }), 201

@coes_bp.route('/api/coes/<int:id>', methods=['GET'])
def get_coe(id):
    result = db.session.execute(
        db.text("SELECT * FROM coes WHERE id = :id"), 
        {'id': id}
    )
    coe = result.fetchone()
    
    if not coe:
        return jsonify({'error': 'COE no encontrado'}), 404
    
    return jsonify({
        'id': coe.id,
        'nombre': coe.nombre,
        'siglas': coe.siglas,
        'descripcion': coe.descripcion,
        'activo': coe.activo,
        'creador': coe.creador,
        'creacion': coe.creacion.isoformat() if coe.creacion else None,
        'modificador': coe.modificador,
        'modificacion': coe.modificacion.isoformat() if coe.modificacion else None
    })

@coes_bp.route('/api/coes/<int:id>', methods=['PUT'])
def update_coe(id):
    # Parse and validate input
    data = request.get_json()
    if not data or not isinstance(data, dict):
        return jsonify({'error': 'No input data provided'}), 400

    now = datetime.now(timezone.utc)

    query = db.text("""
        UPDATE coes
        SET nombre = :nombre,
            siglas = :siglas,
            descripcion = :descripcion,
            activo = :activo,
            modificador = :modificador,
            modificacion = :modificacion
        WHERE id = :id
    """)

    params = {
        'id': id,
        'nombre': data.get('nombre'),
        'siglas': data.get('siglas'),
        'descripcion': data.get('descripcion'),
        'activo': data.get('activo'),
        'modificador': data.get('modificador', 'Sistema'),
        'modificacion': now
    }

    result = db.session.execute(query, params)

    # Some DB drivers may not provide rowcount reliably; treat 0 as not found
    rowcount = getattr(result, 'rowcount', None)
    if rowcount == 0:
        db.session.rollback()
        return jsonify({'error': 'COE no encontrado'}), 404

    db.session.commit()

    coe = db.session.execute(
        db.text("SELECT * FROM coes WHERE id = :id"),
        {'id': id}
    ).fetchone()

    # Ensure coe exists before accessing attributes
    if not coe:
        return jsonify({'error': 'COE no encontrado después de actualizar'}), 404

    return jsonify({
        'id': coe.id,
        'nombre': coe.nombre,
        'siglas': coe.siglas,
        'descripcion': coe.descripcion,
        'activo': coe.activo,
        'creador': coe.creador,
        'creacion': coe.creacion.isoformat() if coe.creacion else None,
        'modificador': coe.modificador,
        'modificacion': coe.modificacion.isoformat() if coe.modificacion else None
    }), 200

@coes_bp.route('/api/coes/<int:id>', methods=['DELETE'])
def delete_coe(id):
    result = db.session.execute(
        db.text("DELETE FROM coes WHERE id = :id"), 
        {'id': id}
    )
    
    if getattr(result, 'rowcount', 0) == 0:
        return jsonify({'error': 'COE no encontrado'}), 404
    
    db.session.commit()
    return jsonify({'mensaje': 'COE eliminado correctamente'})