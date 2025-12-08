from datetime import datetime, timezone
from app import db

class ActividadEjecucionFuncion(db.Model):
    __tablename__ = 'actividad_ejecucion_funciones'
    
    id = db.Column(db.Integer, primary_key=True)
    coe_id = db.Column(db.Integer, db.ForeignKey('coes.id'), nullable=False)
    mesa_id = db.Column(db.Integer, db.ForeignKey('mesas.id'), nullable=False)
    linea_accion = db.Column(db.Text)
    descripcion = db.Column(db.Text)
    producto = db.Column(db.Text)
    activo = db.Column(db.Boolean, default=True)
    creador = db.Column(db.Text)
    creacion = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    modificador = db.Column(db.Text)
    modificacion = db.Column(db.DateTime(timezone=True), onupdate=lambda: datetime.now(timezone.utc))
    
    # Relationships
    coe = db.relationship('Coe', backref='actividad_ejecucion_funciones')
    mesa = db.relationship('Mesa', backref='actividad_ejecucion_funciones')
    
    def to_dict(self):
        return {
            'id': self.id,
            'coe_id': self.coe_id,
            'mesa_id': self.mesa_id,
            'linea_accion': self.linea_accion,
            'descripcion': self.descripcion,
            'producto': self.producto,
            'activo': self.activo,
            'creador': self.creador,
            'creacion': self.creacion.isoformat() if self.creacion else None,
            'modificador': self.modificador,
            'modificacion': self.modificacion.isoformat() if self.modificacion else None
        }
