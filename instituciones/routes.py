from flask import request, jsonify
from instituciones import instituciones_bp
from models import db
from datetime import datetime, timezone

from utils.db_helpers import check_row_or_abort
@instituciones_bp.route('/api/instituciones', methods=['GET'])
def get_instituciones():
    result = db.session.execute(db.text("SELECT * FROM instituciones"))
    instituciones = []
    for row in result:
        instituciones.append({
            'id': row.id,
            'institucion_categoria_id': row.institucion_categoria_id,
            'nombre': row.nombre,
            'siglas': row.siglas,
            'observaciones': row.observaciones,
            'activo': row.activo,
            'creador': row.creador,
            'creacion': row.creacion.isoformat() if row.creacion else None,
            'modificador': row.modificador,
            'modificacion': row.modificacion.isoformat() if row.modificacion else None
        })
    return jsonify(instituciones)

@instituciones_bp.route('/api/instituciones', methods=['POST'])
def create_institucion():
    data = request.get_json()
    now = datetime.now(timezone.utc)
    
    query = db.text("""
        INSERT INTO instituciones (
            institucion_categoria_id, nombre, siglas, observaciones, activo,
            creador, creacion, modificador, modificacion
        )
        VALUES (
            :institucion_categoria_id, :nombre, :siglas, :observaciones, :activo,
            :creador, :creacion, :modificador, :modificacion
        )
        RETURNING id
    """)
    
    result = db.session.execute(query, {
        'institucion_categoria_id': data['institucion_categoria_id'],
        'nombre': data['nombre'],
        'siglas': data.get('siglas'),
        'observaciones': data.get('observaciones'),
        'activo': data.get('activo', True),
        'creador': data.get('creador', 'Sistema'),
        'creacion': now,
        'modificador': data.get('creador', 'Sistema'),
        'modificacion': now
    })
    
    row = result.fetchone()
    if row is None:
        # Something went wrong with the INSERT returning no row
        db.session.rollback()
        return jsonify({'error': 'Failed to create institución'}), 500
    institucion_id = row[0]
    db.session.commit()
    
    institucion = db.session.execute(
        db.text("SELECT * FROM instituciones WHERE id = :id"),
        {'id': institucion_id}
    ).fetchone()
    
    if institucion is None:
        # The row should exist after a successful insert; handle gracefully
        return jsonify({'error': 'Institución creada pero no encontrada'}), 500

    return jsonify({
        'id': institucion.id,
        'institucion_categoria_id': institucion.institucion_categoria_id,
        'nombre': institucion.nombre,
        'siglas': institucion.siglas,
        'observaciones': institucion.observaciones,
        'activo': institucion.activo,
        'creador': institucion.creador,
        'creacion': institucion.creacion.isoformat() if institucion.creacion else None,
        'modificador': institucion.modificador,
        'modificacion': institucion.modificacion.isoformat() if institucion.modificacion else None
    }), 201

@instituciones_bp.route('/api/instituciones/<int:id>', methods=['GET'])
def get_institucion(id):
    result = db.session.execute(
        db.text("SELECT * FROM instituciones WHERE id = :id"), 
        {'id': id}
    )
    institucion = result.fetchone()
    
    if not institucion:
        return jsonify({'error': 'Institución no encontrada'}), 404
    
    return jsonify({
        'id': institucion.id,
        'institucion_categoria_id': institucion.institucion_categoria_id,
        'nombre': institucion.nombre,
        'siglas': institucion.siglas,
        'observaciones': institucion.observaciones,
        'activo': institucion.activo,
        'creador': institucion.creador,
        'creacion': institucion.creacion.isoformat() if institucion.creacion else None,
        'modificador': institucion.modificador,
        'modificacion': institucion.modificacion.isoformat() if institucion.modificacion else None
    })

@instituciones_bp.route('/api/instituciones/<int:id>', methods=['PUT'])
def update_institucion(id):
    data = request.get_json()
    now = datetime.now(timezone.utc)
    
    update_fields = []
    params = {'id': id, 'modificador': data.get('modificador', 'Sistema'), 'modificacion': now}
    for field in ['institucion_categoria_id','nombre','siglas','observaciones','activo']:
        if field in data:
            update_fields.append(f"{field} = :{field}")
            params[field] = data[field]
    update_fields.append('modificador = :modificador')
    update_fields.append('modificacion = :modificacion')

    query = db.text(f"""
        UPDATE instituciones 
        SET {', '.join(update_fields)}
        WHERE id = :id
    """)
    
    result = db.session.execute(query, params)
    
    if getattr(result, 'rowcount', 0) == 0:
        return jsonify({'error': 'Institución no encontrada'}), 404
    
    db.session.commit()
    
    institucion = db.session.execute(
        db.text("SELECT * FROM instituciones WHERE id = :id"),
        {'id': id}
    ).fetchone()
    
    if institucion is None:
        # Shouldn't normally happen because we checked rowcount, but guard against race conditions
        return jsonify({'error': 'Institución no encontrada después de actualizar'}), 404

    return jsonify({
        'id': institucion.id,
        'institucion_categoria_id': institucion.institucion_categoria_id,
        'nombre': institucion.nombre,
        'siglas': institucion.siglas,
        'observaciones': institucion.observaciones,
        'activo': institucion.activo,
        'creador': institucion.creador,
        'creacion': institucion.creacion.isoformat() if institucion.creacion else None,
        'modificador': institucion.modificador,
        'modificacion': institucion.modificacion.isoformat() if institucion.modificacion else None
    })

@instituciones_bp.route('/api/instituciones/<int:id>', methods=['DELETE'])
def delete_institucion(id):
    result = db.session.execute(
        db.text("DELETE FROM instituciones WHERE id = :id"), 
        {'id': id}
    )
    
    if getattr(result, 'rowcount', 0) == 0:
        return jsonify({'error': 'Institución no encontrada'}), 404
    
    db.session.commit()
    return jsonify({'mensaje': 'Institución eliminada correctamente'})
