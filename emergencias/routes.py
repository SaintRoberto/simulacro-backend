from flask import request, jsonify
from emergencias import emergencias_bp
from models import db
from datetime import datetime, timezone

from utils.db_helpers import check_row_or_abort
@emergencias_bp.route('/api/emergencias', methods=['GET'])
def get_emergencias():
    result = db.session.execute(db.text("SELECT * FROM emergencias"))
    emergencias = []
    for row in result:
        emergencias.append({
            'id': row.id,
            'nombre': row.nombre,
            'antecedentes': row.antecedentes,
            'situacion_actual': row.situacion_actual,
            'nivel_afectacion_id': row.nivel_afectacion_id,
            'nivel_alerta_id': row.nivel_alerta_id,
            'fecha_inicio': row.fecha_inicio.isoformat() if row.fecha_inicio else None,
            'fecha_fin': row.fecha_fin.isoformat() if row.fecha_fin else None,
            'etapa_id': row.etapa_id,
            'provincias_impactadas': row.provincias_impactadas,
            'cantones_impactados': row.cantones_impactados,
            'parroquias_impactadas': row.parroquias_impactadas,
            'eventos_adversos': row.eventos_adversos,
            'declaratorias_emergencia': row.declaratorias_emergencia,
            'declaratorias_desastre': row.declaratorias_desastre,
            'declaratorias_catastrofe': row.declaratorias_catastrofe,
            'costo_estimado_danos': float(row.costo_estimado_danos) if row.costo_estimado_danos else 0,
            'activo': row.activo,
            'creador': row.creador,
            'creacion': row.creacion.isoformat() if row.creacion else None,
            'modificador': row.modificador,
            'modificacion': row.modificacion.isoformat() if row.modificacion else None
        })
    return jsonify(emergencias)

@emergencias_bp.route('/api/emergencias', methods=['POST'])
def create_emergencia():
    data = request.get_json()
    now = datetime.now(timezone.utc)
    
    query = db.text("""
        INSERT INTO emergencias (
            nombre, antecedentes, situacion_actual, nivel_afectacion_id, nivel_alerta_id,
            fecha_inicio, fecha_fin, etapa_id, provincias_impactadas, cantones_impactados,
            parroquias_impactadas, eventos_adversos, declaratorias_emergencia,
            declaratorias_desastre, declaratorias_catastrofe, costo_estimado_danos,
            activo, creador, creacion, modificador, modificacion
        )
        VALUES (
            :nombre, :antecedentes, :situacion_actual, :nivel_afectacion_id, :nivel_alerta_id,
            :fecha_inicio, :fecha_fin, :etapa_id, :provincias_impactadas, :cantones_impactados,
            :parroquias_impactadas, :eventos_adversos, :declaratorias_emergencia,
            :declaratorias_desastre, :declaratorias_catastrofe, :costo_estimado_danos,
            :activo, :creador, :creacion, :modificador, :modificacion
        )
        RETURNING id
    """)
    
    result = db.session.execute(query, {
        'nombre': data['nombre'],
        'antecedentes': data.get('antecedentes'),
        'situacion_actual': data.get('situacion_actual'),
        'nivel_afectacion_id': data['nivel_afectacion_id'],
        'nivel_alerta_id': data['nivel_alerta_id'],
        'fecha_inicio': data.get('fecha_inicio'),
        'fecha_fin': data.get('fecha_fin'),
        'etapa_id': data['etapa_id'],
        'provincias_impactadas': data.get('provincias_impactadas', 0),
        'cantones_impactados': data.get('cantones_impactados', 0),
        'parroquias_impactadas': data.get('parroquias_impactadas', 0),
        'eventos_adversos': data.get('eventos_adversos', 0),
        'declaratorias_emergencia': data.get('declaratorias_emergencia', 0),
        'declaratorias_desastre': data.get('declaratorias_desastre', 0),
        'declaratorias_catastrofe': data.get('declaratorias_catastrofe', 0),
        'costo_estimado_danos': data.get('costo_estimado_danos', 0),
        'activo': data.get('activo', True),
        'creador': data.get('creador', 'Sistema'),
        'creacion': now,
        # set 'modificador' from provided modifier if present, otherwise fallback to 'creador' or 'Sistema'
        'modificador': data.get('modificador', data.get('creador', 'Sistema')),
        'modificacion': now
    })
    
    row = result.fetchone()
    if row is None:
        return jsonify({'error': 'Not found'}), 404
    emergencia_id = row[0]
    db.session.commit()
    
    emergencia = db.session.execute(
        db.text("SELECT * FROM emergencias WHERE id = :id"),
        {'id': emergencia_id}
    ).fetchone()
    
    # defensive check: ensure the inserted row can be retrieved
    if emergencia is None:
        # This is unexpected if INSERT ... RETURNING id succeeded, but handle gracefully
        return jsonify({'error': 'Unable to retrieve created emergencia'}), 500

    return jsonify({
        'id': emergencia.id,
        'nombre': emergencia.nombre,
        'antecedentes': emergencia.antecedentes,
        'situacion_actual': emergencia.situacion_actual,
        'nivel_afectacion_id': emergencia.nivel_afectacion_id,
        'nivel_alerta_id': emergencia.nivel_alerta_id,
        'fecha_inicio': emergencia.fecha_inicio.isoformat() if emergencia.fecha_inicio else None,
        'fecha_fin': emergencia.fecha_fin.isoformat() if emergencia.fecha_fin else None,
        'etapa_id': emergencia.etapa_id,
        'provincias_impactadas': emergencia.provincias_impactadas,
        'cantones_impactados': emergencia.cantones_impactados,
        'parroquias_impactadas': emergencia.parroquias_impactadas,
        'eventos_adversos': emergencia.eventos_adversos,
        'declaratorias_emergencia': emergencia.declaratorias_emergencia,
        'declaratorias_desastre': emergencia.declaratorias_desastre,
        'declaratorias_catastrofe': emergencia.declaratorias_catastrofe,
        'costo_estimado_danos': float(emergencia.costo_estimado_danos) if emergencia.costo_estimado_danos else 0,
        'activo': emergencia.activo,
        'creador': emergencia.creador,
        'creacion': emergencia.creacion.isoformat() if emergencia.creacion else None,
        'modificador': emergencia.modificador,
        'modificacion': emergencia.modificacion.isoformat() if emergencia.modificacion else None
    }), 201

@emergencias_bp.route('/api/emergencias/<int:id>', methods=['GET'])
def get_emergencia(id):
    result = db.session.execute(
        db.text("SELECT * FROM emergencias WHERE id = :id"), 
        {'id': id}
    )
    emergencia = result.fetchone()
    
    if not emergencia:
        return jsonify({'error': 'Emergencia no encontrada'}), 404
    
    return jsonify({
        'id': emergencia.id,
        'nombre': emergencia.nombre,
        'antecedentes': emergencia.antecedentes,
        'situacion_actual': emergencia.situacion_actual,
        'nivel_afectacion_id': emergencia.nivel_afectacion_id,
        'nivel_alerta_id': emergencia.nivel_alerta_id,
        'fecha_inicio': emergencia.fecha_inicio.isoformat() if emergencia.fecha_inicio else None,
        'fecha_fin': emergencia.fecha_fin.isoformat() if emergencia.fecha_fin else None,
        'etapa_id': emergencia.etapa_id,
        'provincias_impactadas': emergencia.provincias_impactadas,
        'cantones_impactados': emergencia.cantones_impactados,
        'parroquias_impactadas': emergencia.parroquias_impactadas,
        'eventos_adversos': emergencia.eventos_adversos,
        'declaratorias_emergencia': emergencia.declaratorias_emergencia,
        'declaratorias_desastre': emergencia.declaratorias_desastre,
        'declaratorias_catastrofe': emergencia.declaratorias_catastrofe,
        'costo_estimado_danos': float(emergencia.costo_estimado_danos) if emergencia.costo_estimado_danos else 0,
        'activo': emergencia.activo,
        'creador': emergencia.creador,
        'creacion': emergencia.creacion.isoformat() if emergencia.creacion else None,
        'modificador': emergencia.modificador,
        'modificacion': emergencia.modificacion.isoformat() if emergencia.modificacion else None
    })

@emergencias_bp.route('/api/emergencias/<int:id>', methods=['PUT'])
def update_emergencia(id):
    data = request.get_json()
    now = datetime.now(timezone.utc)
    
    update_fields = []
    params = {'id': id, 'modificador': data.get('modificador', 'Sistema'), 'modificacion': now}
    
    fields = ['nombre', 'antecedentes', 'situacion_actual', 'nivel_afectacion_id', 'nivel_alerta_id',
              'fecha_inicio', 'fecha_fin', 'etapa_id', 'provincias_impactadas', 'cantones_impactados',
              'parroquias_impactadas', 'eventos_adversos', 'declaratorias_emergencia',
              'declaratorias_desastre', 'declaratorias_catastrofe', 'costo_estimado_danos', 'activo']
    
    for field in fields:
        if field in data:
            update_fields.append(f"{field} = :{field}")
            params[field] = data[field]
    
    update_fields.append('modificador = :modificador')
    update_fields.append('modificacion = :modificacion')
    
    query = db.text(f"""
        UPDATE emergencias 
        SET {', '.join(update_fields)}
        WHERE id = :id
    """)
    
    result = db.session.execute(query, params)
    
    if getattr(result, 'rowcount', 0) == 0:
        return jsonify({'error': 'Emergencia no encontrada'}), 404
    
    db.session.commit()
    
    emergencia = db.session.execute(
        db.text("SELECT * FROM emergencias WHERE id = :id"),
        {'id': id}
    ).fetchone()
    
    if emergencia is None:
        # If rowcount indicated an update, this should not happen, but handle defensively
        return jsonify({'error': 'Emergencia no encontrada después de actualizar'}), 404

    return jsonify({
        'id': emergencia.id,
        'nombre': emergencia.nombre,
        'antecedentes': emergencia.antecedentes,
        'situacion_actual': emergencia.situacion_actual,
        'nivel_afectacion_id': emergencia.nivel_afectacion_id,
        'nivel_alerta_id': emergencia.nivel_alerta_id,
        'fecha_inicio': emergencia.fecha_inicio.isoformat() if emergencia.fecha_inicio else None,
        'fecha_fin': emergencia.fecha_fin.isoformat() if emergencia.fecha_fin else None,
        'etapa_id': emergencia.etapa_id,
        'provincias_impactadas': emergencia.provincias_impactadas,
        'cantones_impactados': emergencia.cantones_impactados,
        'parroquias_impactadas': emergencia.parroquias_impactadas,
        'eventos_adversos': emergencia.eventos_adversos,
        'declaratorias_emergencia': emergencia.declaratorias_emergencia,
        'declaratorias_desastre': emergencia.declaratorias_desastre,
        'declaratorias_catastrofe': emergencia.declaratorias_catastrofe,
        'costo_estimado_danos': float(emergencia.costo_estimado_danos) if emergencia.costo_estimado_danos else 0,
        'activo': emergencia.activo,
        'creador': emergencia.creador,
        'creacion': emergencia.creacion.isoformat() if emergencia.creacion else None,
        'modificador': emergencia.modificador,
        'modificacion': emergencia.modificacion.isoformat() if emergencia.modificacion else None
    })

@emergencias_bp.route('/api/emergencias/<int:id>', methods=['DELETE'])
def delete_emergencia(id):
    result = db.session.execute(
        db.text("DELETE FROM emergencias WHERE id = :id"), 
        {'id': id}
    )
    
    if getattr(result, 'rowcount', 0) == 0:
        return jsonify({'error': 'Emergencia no encontrada'}), 404
    
    db.session.commit()
    return jsonify({'mensaje': 'Emergencia eliminada correctamente'})
