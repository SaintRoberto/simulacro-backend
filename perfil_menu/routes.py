from flask import request, jsonify
from perfil_menu import perfil_menu_bp
from models import db
from datetime import datetime, timezone

from utils.db_helpers import check_row_or_abort
@perfil_menu_bp.route('/api/perfil-menu', methods=['GET'])
def get_perfil_menu():
    result = db.session.execute(db.text("SELECT * FROM perfil_menu"))
    relaciones = []
    for row in result:
        relaciones.append({
            'id': row.id,
            'perfil_id': row.perfil_id,
            'menu_id': row.menu_id,
            'activo': row.activo,
            'creador': row.creador,
            'creacion': row.creacion.isoformat() if row.creacion else None,
            'modificador': row.modificador,
            'modificacion': row.modificacion.isoformat() if row.modificacion else None
        })
    return jsonify(relaciones)

@perfil_menu_bp.route('/api/perfil-menu', methods=['POST'])
def create_perfil_menu():
    data = request.get_json() or {}
    # Validate required fields
    if 'perfil_id' not in data or 'menu_id' not in data:
        return jsonify({'error': 'perfil_id and menu_id are required'}), 400

    now = datetime.now(timezone.utc)

    query = db.text("""
        INSERT INTO perfil_menu (perfil_id, menu_id, activo, creador, creacion, modificador, modificacion)
        VALUES (:perfil_id, :menu_id, :activo, :creador, :creacion, :modificador, :modificacion)
        RETURNING id
    """)

    try:
        result = db.session.execute(query, {
            'perfil_id': data['perfil_id'],
            'menu_id': data['menu_id'],
            'activo': data.get('activo', True),
            'creador': data.get('creador', 'Sistema'),
            # use provided modificador if any, otherwise fallback to creador or 'Sistema'
            'modificador': data.get('modificador', data.get('creador', 'Sistema')),
            'creacion': now,
            'modificacion': now
        })
        # Use scalar() to directly get the returned id (first column of first row)
        relacion_id = result.scalar()
        if relacion_id is None:
            db.session.rollback()
            return jsonify({'error': 'Failed to create relación'}), 500

        # commit after successful insert
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Database error', 'details': str(e)}), 500

    relacion = db.session.execute(
        db.text("SELECT * FROM perfil_menu WHERE id = :id"),
        {'id': relacion_id}
    ).fetchone()

    if not relacion:
        return jsonify({'error': 'Relación no encontrada después de creación'}), 404

    return jsonify({
        'id': relacion.id,
        'perfil_id': relacion.perfil_id,
        'menu_id': relacion.menu_id,
        'activo': relacion.activo,
        'creador': relacion.creador,
        'creacion': relacion.creacion.isoformat() if relacion.creacion else None,
        'modificador': relacion.modificador,
        'modificacion': relacion.modificacion.isoformat() if relacion.modificacion else None
    }), 201

@perfil_menu_bp.route('/api/perfil-menu/<int:id>', methods=['GET'])
def get_perfil_menu_by_id(id):
    result = db.session.execute(
        db.text("SELECT * FROM perfil_menu WHERE id = :id"), 
        {'id': id}
    )
    relacion = result.fetchone()
    
    if not relacion:
        return jsonify({'error': 'Relación no encontrada'}), 404
    
    return jsonify({
        'id': relacion.id,
        'perfil_id': relacion.perfil_id,
        'menu_id': relacion.menu_id,
        'activo': relacion.activo,
        'creador': relacion.creador,
        'creacion': relacion.creacion.isoformat() if relacion.creacion else None,
        'modificador': relacion.modificador,
        'modificacion': relacion.modificacion.isoformat() if relacion.modificacion else None
    })

@perfil_menu_bp.route('/api/perfil-menu/<int:id>', methods=['PUT'])
def update_perfil_menu(id):
    data = request.get_json() or {}
    now = datetime.now(timezone.utc)

    query = db.text("""
        UPDATE perfil_menu
        SET perfil_id = :perfil_id,
            menu_id = :menu_id,
            activo = :activo,
            modificador = :modificador,
            modificacion = :modificacion
        WHERE id = :id
    """)

    try:
        result = db.session.execute(query, {
            'id': id,
            'perfil_id': data.get('perfil_id'),
            'menu_id': data.get('menu_id'),
            'activo': data.get('activo'),
            'modificador': data.get('modificador', 'Sistema'),
            'modificacion': now
        })

        # If no rows were updated, the resource doesn't exist
        if getattr(result, 'rowcount', 0) == 0:
            db.session.rollback()
            return jsonify({'error': 'Relación no encontrada'}), 404

        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Database error', 'details': str(e)}), 500

    relacion = db.session.execute(
        db.text("SELECT * FROM perfil_menu WHERE id = :id"),
        {'id': id}
    ).fetchone()

    if not relacion:
        return jsonify({'error': 'Relación no encontrada'}), 404

    return jsonify({
        'id': relacion.id,
        'perfil_id': relacion.perfil_id,
        'menu_id': relacion.menu_id,
        'activo': relacion.activo,
        'creador': relacion.creador,
        'creacion': relacion.creacion.isoformat() if relacion.creacion else None,
        'modificador': relacion.modificador,
        'modificacion': relacion.modificacion.isoformat() if relacion.modificacion else None
    })

@perfil_menu_bp.route('/api/perfil-menu/<int:id>', methods=['DELETE'])
def delete_perfil_menu(id):
    result = db.session.execute(
        db.text("DELETE FROM perfil_menu WHERE id = :id"), 
        {'id': id}
    )
    
    if getattr(result, 'rowcount', 0) == 0:
        return jsonify({'error': 'Relación no encontrada'}), 404
    
    db.session.commit()
    return jsonify({'mensaje': 'Relación eliminada correctamente'})
