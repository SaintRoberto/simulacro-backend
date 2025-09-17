from flask import request, jsonify
from mesas import mesas_bp
from models import db
from datetime import datetime, timezone

@mesas_bp.route('/api/mesas', methods=['GET'])
def get_mesas():
    result = db.session.execute(db.text("SELECT * FROM mesas"))
    mesas = []
    for row in result:
        mesas.append({
            'id': row.id,
            'coe_id': row.coe_id,
            'mesa_grupo_id': row.mesa_grupo_id,
            'nombre': row.nombre,
            'siglas': row.siglas,
            'activo': row.activo,
            'creador': row.creador,
            'creacion': row.creacion.isoformat() if row.creacion else None,
            'modificador': row.modificador,
            'modificacion': row.modificacion.isoformat() if row.modificacion else None
        })
    return jsonify(mesas)

@mesas_bp.route('/api/mesas', methods=['POST'])
def create_mesa():
    data = request.get_json()
    now = datetime.now(timezone.utc)
    
    query = db.text("""
        INSERT INTO mesas (coe_id, mesa_grupo_id, nombre, siglas, activo, creador, creacion, modificador, modificacion)
        VALUES (:coe_id, :mesa_grupo_id, :nombre, :siglas, :activo, :creador, :creacion, :modificador, :modificacion)
        RETURNING id
    """)
    
    result = db.session.execute(query, {
        'coe_id': data['coe_id'],
        'mesa_grupo_id': data['mesa_grupo_id'],
        'nombre': data['nombre'],
        'siglas': data['siglas'],
        'activo': data.get('activo', True),
        'creador': data.get('creador', 'Sistema'),
        'creacion': now,
        'modificador': data.get('creador', 'Sistema'),
        'modificacion': now
    })
    
    mesa_id = result.fetchone()[0]
    db.session.commit()
    
    mesa = db.session.execute(
        db.text("SELECT * FROM mesas WHERE id = :id"), 
        {'id': mesa_id}
    ).fetchone()
    
    return jsonify({
        'id': mesa.id,
        'coe_id': mesa.coe_id,
        'mesa_grupo_id': mesa.mesa_grupo_id,
        'nombre': mesa.nombre,
        'siglas': mesa.siglas,
        'activo': mesa.activo,
        'creador': mesa.creador,
        'creacion': mesa.creacion.isoformat() if mesa.creacion else None,
        'modificador': mesa.modificador,
        'modificacion': mesa.modificacion.isoformat() if mesa.modificacion else None
    }), 201

@mesas_bp.route('/api/mesas/<int:id>', methods=['GET'])
def get_mesa(id):
    result = db.session.execute(
        db.text("SELECT * FROM mesas WHERE id = :id"), 
        {'id': id}
    )
    mesa = result.fetchone()
    
    if not mesa:
        return jsonify({'error': 'Mesa no encontrada'}), 404
    
    return jsonify({
        'id': mesa.id,
        'coe_id': mesa.coe_id,
        'mesa_grupo_id': mesa.mesa_grupo_id,
        'nombre': mesa.nombre,
        'siglas': mesa.siglas,
        'activo': mesa.activo,
        'creador': mesa.creador,
        'creacion': mesa.creacion.isoformat() if mesa.creacion else None,
        'modificador': mesa.modificador,
        'modificacion': mesa.modificacion.isoformat() if mesa.modificacion else None
    })

@mesas_bp.route('/api/mesas/<int:coe_id>/<int:mesa_id>/<int:mesa_grupo_id>/<int:provincia_id>/<int:canton_id>', methods=['GET'])
def get_mesa_lista(coe_id, mesa_id, mesa_grupo_id, provincia_id, canton_id):
    """
    Obtener lista de mesas receptoras en función de la mesa actual
    ---
    tags:
      - Mesas
    parameters:
      - name: coe_id
        in: path
        type: integer
        required: true
        description: ID COE
      - name: mesa_id
        in: path
        type: integer
        required: true
        description: ID mesa
      - name: mesa_grupo_id
        in: path
        type: integer
        required: true
        description: ID grupo de mesa
      - name: provincia_id
        in: path
        type: integer
        required: true
        description: ID de la provincia
      - name: canton_id
        in: path
        type: integer
        required: true
        description: ID del canton
    responses:
      200:
        description: Lista de mesas receptoras obtenida exitosamente
        schema:
          type: array
          items:
            type: object
            properties:
              usuario_id:
                type: integer
                description: ID del usuario
              coe_id:
                type: integer
                description: ID del COE
              siglas:
                type: string
                description: Siglas del COE
              mesa_id:
                type: integer
                description: ID de la mesa
              mesa_nombre:
                type: string
                description: Nombre de la mesa
              mesa_siglas:
                type: string
                description: Siglas de la mesa
        examples:
          application/json: [
            {
              "usuario_id": 1,
              "coe_id": 1,
              "siglas": "COE-01",
              "mesa_id": 2,
              "mesa_nombre": "Mesa de Comunicación",
              "mesa_siglas": "COM"
            }
          ]
      404:
        description: Lista de mesa receptoras no encontrada
        examples:
          application/json: {"error": "listado de mesa receptoras no encontrada"}
    """
    params = {'coe_id': coe_id, 'mesa_id': mesa_id, 'mesa_grupo_id': mesa_grupo_id, 'provincia_id': provincia_id, 'canton_id': canton_id}
    query = db.text("""SELECT ux.usuario_id, m.coe_id, c.siglas, m.id mesa_id, m.nombre mesa_nombre, m.siglas mesa_siglas
      FROM public.mesas m
      INNER JOIN public.coes c ON m.coe_id = c.id
      INNER JOIN public.usuario_perfil_coe_dpa_mesa ux ON m.coe_id = ux.coe_id AND m.id = ux.mesa_id 
      AND ux.provincia_id = :provincia_id AND ux.canton_id = :canton_id
      WHERE m.coe_id = :coe_id
      AND m.id <> :mesa_id
      UNION 
      SELECT ux1.usuario_id, m1.coe_id, c1.siglas, m1.id mesa_id, m1.nombre mesa_nombre, m1.siglas mesa_siglas
      FROM public.mesas m1
      INNER JOIN public.coes c1 ON m1.coe_id = c1.id
      INNER JOIN public.usuario_perfil_coe_dpa_mesa ux1 ON m1.coe_id = ux1.coe_id AND m1.id = ux1.mesa_id 
      AND (ux1.provincia_id = :provincia_id OR :provincia_id = 0) AND (ux1.canton_id = :canton_id OR :canton_id = 0)
      WHERE m1.coe_id = (:mesa_id - 1)
      AND m1.mesa_grupo_id = :mesa_grupo_id""")

    # Debug: print the compiled query with substituted parameters
  
    result = db.session.execute(query, params)
    mesas = []
    if not result:
        return jsonify({'error': 'listado de mesa receptoras no encontrada'}), 404
    for row in result:     
        mesas.append({
            'usuario_id': row.usuario_id,
            'coe_id': row.coe_id,
            'siglas': row.siglas,
            'mesa_id': row.mesa_id,
            'mesa_nombre': row.mesa_nombre,
            'mesa_siglas': row.mesa_siglas,
        })
    return jsonify(mesas)
  
@mesas_bp.route('/api/mesas/<int:id>', methods=['PUT'])
def update_mesa(id):
    data = request.get_json()
    now = datetime.now(timezone.utc)
    
    query = db.text("""
        UPDATE mesas 
        SET coe_id = :coe_id, 
            mesa_grupo_id = :mesa_grupo_id, 
            nombre = :nombre, 
            siglas = :siglas, 
            activo = :activo, 
            modificador = :modificador, 
            modificacion = :modificacion
        WHERE id = :id
    """)
    
    result = db.session.execute(query, {
        'id': id,
        'coe_id': data.get('coe_id'),
        'mesa_grupo_id': data.get('mesa_grupo_id'),
        'nombre': data.get('nombre'),
        'siglas': data.get('siglas'),
        'activo': data.get('activo'),
        'modificador': data.get('modificador', 'Sistema'),
        'modificacion': now
    })
    
    if result.rowcount == 0:
        return jsonify({'error': 'Mesa no encontrada'}), 404
    
    db.session.commit()
    
    mesa = db.session.execute(
        db.text("SELECT * FROM mesas WHERE id = :id"), 
        {'id': id}
    ).fetchone()
    
    return jsonify({
        'id': mesa.id,
        'coe_id': mesa.coe_id,
        'mesa_grupo_id': mesa.mesa_grupo_id,
        'nombre': mesa.nombre,
        'siglas': mesa.siglas,
        'activo': mesa.activo,
        'creador': mesa.creador,
        'creacion': mesa.creacion.isoformat() if mesa.creacion else None,
        'modificador': mesa.modificador,
        'modificacion': mesa.modificacion.isoformat() if mesa.modificacion else None
    })

@mesas_bp.route('/api/mesas/<int:id>', methods=['DELETE'])
def delete_mesa(id):
    result = db.session.execute(
        db.text("DELETE FROM mesas WHERE id = :id"), 
        {'id': id}
    )
    
    if result.rowcount == 0:
        return jsonify({'error': 'Mesa no encontrada'}), 404
    
    db.session.commit()
    return jsonify({'mensaje': 'Mesa eliminada correctamente'})