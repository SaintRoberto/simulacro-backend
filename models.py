from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timezone

db = SQLAlchemy()

class Categoria(db.Model):
    __tablename__ = 'categorias'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    descripcion = db.Column(db.Text)
    activo = db.Column(db.Boolean, default=True)
    creador = db.Column(db.String(100))
    creacion = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    modificador = db.Column(db.String(100))
    modificacion = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    
    # Relaciones
    instituciones = db.relationship('Institucion', backref='categoria', lazy=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'nombre': self.nombre,
            'descripcion': self.descripcion,
            'activo': self.activo,
            'creador': self.creador,
            'creacion': self.creacion.isoformat() if self.creacion else None,
            'modificador': self.modificador,
            'modificacion': self.modificacion.isoformat() if self.modificacion else None
        }

class Institucion(db.Model):
    __tablename__ = 'instituciones'
    id = db.Column(db.Integer, primary_key=True)
    categoria_id = db.Column(db.Integer, db.ForeignKey('categorias.id'), nullable=False)
    nombre = db.Column(db.String(200), nullable=False)
    siglas = db.Column(db.String(50))
    activo = db.Column(db.Boolean, default=True)
    creador = db.Column(db.String(100))
    creacion = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    modificador = db.Column(db.String(100))
    modificacion = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    
    # Relaciones
    usuarios = db.relationship('Usuario', backref='institucion', lazy=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'categoria_id': self.categoria_id,
            'nombre': self.nombre,
            'siglas': self.siglas,
            'activo': self.activo,
            'creador': self.creador,
            'creacion': self.creacion.isoformat() if self.creacion else None,
            'modificador': self.modificador,
            'modificacion': self.modificacion.isoformat() if self.modificacion else None
        }

class Usuario(db.Model):
    __tablename__ = 'usuarios'
    id = db.Column(db.Integer, primary_key=True)
    institucion_id = db.Column(db.Integer, db.ForeignKey('instituciones.id'), nullable=False)
    usuario = db.Column(db.String(100), unique=True, nullable=False)
    contrasena = db.Column(db.String(255), nullable=False)
    correo = db.Column(db.String(150), unique=True, nullable=False)
    nombres = db.Column(db.String(100), nullable=False)
    apellidos = db.Column(db.String(100), nullable=False)
    cedula = db.Column(db.String(20), unique=True, nullable=False)
    celular = db.Column(db.String(20))
    activo = db.Column(db.Boolean, default=True)
    aprobado = db.Column(db.Boolean, default=False)
    creador = db.Column(db.String(100))
    creacion = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    modificador = db.Column(db.String(100))
    modificacion = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    
    def to_dict(self):
        return {
            'id': self.id,
            'institucion_id': self.institucion_id,
            'usuario': self.usuario,
            'correo': self.correo,
            'nombres': self.nombres,
            'apellidos': self.apellidos,
            'cedula': self.cedula,
            'celular': self.celular,
            'activo': self.activo,
            'aprobado': self.aprobado,
            'creador': self.creador,
            'creacion': self.creacion.isoformat() if self.creacion else None,
            'modificador': self.modificador,
            'modificacion': self.modificacion.isoformat() if self.modificacion else None
        }

class Perfil(db.Model):
    __tablename__ = 'perfiles'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    descripcion = db.Column(db.Text)
    activo = db.Column(db.Boolean, default=True)
    creador = db.Column(db.String(100))
    creacion = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    modificador = db.Column(db.String(100))
    modificacion = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    
    def to_dict(self):
        return {
            'id': self.id,
            'nombre': self.nombre,
            'descripcion': self.descripcion,
            'activo': self.activo,
            'creador': self.creador,
            'creacion': self.creacion.isoformat() if self.creacion else None,
            'modificador': self.modificador,
            'modificacion': self.modificacion.isoformat() if self.modificacion else None
        }

class Menu(db.Model):
    __tablename__ = 'menus'
    id = db.Column(db.Integer, primary_key=True)
    padre_id = db.Column(db.Integer, db.ForeignKey('menus.id'))
    orden = db.Column(db.Integer, default=0)
    nombre = db.Column(db.String(100), nullable=False)
    abreviatura = db.Column(db.String(50))
    ruta = db.Column(db.String(200))
    activo = db.Column(db.Boolean, default=True)
    creador = db.Column(db.String(100))
    creacion = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    modificador = db.Column(db.String(100))
    modificacion = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    
    # Relación recursiva
    hijos = db.relationship('Menu', backref=db.backref('padre', remote_side=[id]))
    
    def to_dict(self):
        return {
            'id': self.id,
            'padre_id': self.padre_id,
            'orden': self.orden,
            'nombre': self.nombre,
            'abreviatura': self.abreviatura,
            'ruta': self.ruta,
            'activo': self.activo,
            'creador': self.creador,
            'creacion': self.creacion.isoformat() if self.creacion else None,
            'modificador': self.modificador,
            'modificacion': self.modificacion.isoformat() if self.modificacion else None
        }

class Provincia(db.Model):
    __tablename__ = 'provincias'
    id = db.Column(db.Integer, primary_key=True)
    dpa = db.Column(db.String(10), unique=True, nullable=False)
    nombre = db.Column(db.String(100), nullable=False)
    abreviatura = db.Column(db.String(10))
    activo = db.Column(db.Boolean, default=True)
    creador = db.Column(db.String(100))
    creacion = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    modificador = db.Column(db.String(100))
    modificacion = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    
    # Relaciones
    cantones = db.relationship('Canton', backref='provincia', lazy=True)
    parroquias = db.relationship('Parroquia', backref='provincia', lazy=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'dpa': self.dpa,
            'nombre': self.nombre,
            'abreviatura': self.abreviatura,
            'activo': self.activo,
            'creador': self.creador,
            'creacion': self.creacion.isoformat() if self.creacion else None,
            'modificador': self.modificador,
            'modificacion': self.modificacion.isoformat() if self.modificacion else None
        }

class Canton(db.Model):
    __tablename__ = 'cantones'
    id = db.Column(db.Integer, primary_key=True)
    provincia_id = db.Column(db.Integer, db.ForeignKey('provincias.id'), nullable=False)
    dpa = db.Column(db.String(10), unique=True, nullable=False)
    nombre = db.Column(db.String(100), nullable=False)
    abreviatura = db.Column(db.String(10))
    activo = db.Column(db.Boolean, default=True)
    creador = db.Column(db.String(100))
    creacion = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    modificador = db.Column(db.String(100))
    modificacion = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    
    # Relaciones
    parroquias = db.relationship('Parroquia', backref='canton', lazy=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'provincia_id': self.provincia_id,
            'dpa': self.dpa,
            'nombre': self.nombre,
            'abreviatura': self.abreviatura,
            'activo': self.activo,
            'creador': self.creador,
            'creacion': self.creacion.isoformat() if self.creacion else None,
            'modificador': self.modificador,
            'modificacion': self.modificacion.isoformat() if self.modificacion else None
        }

class Parroquia(db.Model):
    __tablename__ = 'parroquias'
    id = db.Column(db.Integer, primary_key=True)
    provincia_id = db.Column(db.Integer, db.ForeignKey('provincias.id'), nullable=False)
    canton_id = db.Column(db.Integer, db.ForeignKey('cantones.id'), nullable=False)
    dpa = db.Column(db.String(10), unique=True, nullable=False)
    nombre = db.Column(db.String(100), nullable=False)
    abreviatura = db.Column(db.String(10))
    activo = db.Column(db.Boolean, default=True)
    creador = db.Column(db.String(100))
    creacion = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    modificador = db.Column(db.String(100))
    modificacion = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    
    def to_dict(self):
        return {
            'id': self.id,
            'provincia_id': self.provincia_id,
            'canton_id': self.canton_id,
            'dpa': self.dpa,
            'nombre': self.nombre,
            'abreviatura': self.abreviatura,
            'activo': self.activo,
            'creador': self.creador,
            'creacion': self.creacion.isoformat() if self.creacion else None,
            'modificador': self.modificador,
            'modificacion': self.modificacion.isoformat() if self.modificacion else None
        }

class Infraestructura(db.Model):
    __tablename__ = 'infraestructuras'
    id = db.Column(db.Integer, primary_key=True)
    infraestructura_tipo_id = db.Column(db.Integer, nullable=False)
    nombre = db.Column(db.Text)
    direccion = db.Column(db.Text)
    provincia_id = db.Column(db.Integer, db.ForeignKey('provincias.id'), nullable=False)
    canton_id = db.Column(db.Integer, db.ForeignKey('cantones.id'), nullable=False)
    parroquia_id = db.Column(db.Integer, db.ForeignKey('parroquias.id'), nullable=False)
    tipologia = db.Column(db.Text)
    institucion = db.Column(db.Text)
    longitud = db.Column(db.Numeric(15, 12), nullable=False, default=0)
    latitud = db.Column(db.Numeric(15, 12), nullable=False, default=0)
    activo = db.Column(db.Boolean, default=True)
    creador = db.Column(db.Text)
    creacion = db.Column(db.DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))
    modificador = db.Column(db.Text)
    modificacion = db.Column(db.DateTime(timezone=True))

    # Relaciones
    provincia = db.relationship('Provincia', backref='infraestructuras')
    canton = db.relationship('Canton', backref='infraestructuras')
    parroquia = db.relationship('Parroquia', backref='infraestructuras')

    def to_dict(self):
        return {
            'id': self.id,
            'infraestructura_tipo_id': self.infraestructura_tipo_id,
            'nombre': self.nombre,
            'direccion': self.direccion,
            'provincia_id': self.provincia_id,
            'canton_id': self.canton_id,
            'parroquia_id': self.parroquia_id,
            'tipologia': self.tipologia,
            'institucion': self.institucion,
            'longitud': float(self.longitud) if self.longitud else None,
            'latitud': float(self.latitud) if self.latitud else None,
            'activo': self.activo,
            'creador': self.creador,
            'creacion': self.creacion.isoformat() if self.creacion else None,
            'modificador': self.modificador,
            'modificacion': self.modificacion.isoformat() if self.modificacion else None
        }

class Coe(db.Model):
    __tablename__ = 'coes'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(200), nullable=False)
    siglas = db.Column(db.String(50))
    descripcion = db.Column(db.Text)
    activo = db.Column(db.Boolean, default=True)
    creador = db.Column(db.String(100))
    creacion = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    modificador = db.Column(db.String(100))
    modificacion = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    
    def to_dict(self):
        return {
            'id': self.id,
            'nombre': self.nombre,
            'siglas': self.siglas,
            'descripcion': self.descripcion,
            'activo': self.activo,
            'creador': self.creador,
            'creacion': self.creacion.isoformat() if self.creacion else None,
            'modificador': self.modificador,
            'modificacion': self.modificacion.isoformat() if self.modificacion else None
        }

class Mesa(db.Model):
    __tablename__ = 'mesas'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(200), nullable=False)
    siglas = db.Column(db.String(50))
    tipo_id = db.Column(db.Integer)
    activo = db.Column(db.Boolean, default=True)
    creador = db.Column(db.String(100))
    creacion = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    modificador = db.Column(db.String(100))
    modificacion = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    
    def to_dict(self):
        return {
            'id': self.id,
            'nombre': self.nombre,
            'siglas': self.siglas,
            'tipo_id': self.tipo_id,
            'activo': self.activo,
            'creador': self.creador,
            'creacion': self.creacion.isoformat() if self.creacion else None,
            'modificador': self.modificador,
            'modificacion': self.modificacion.isoformat() if self.modificacion else None
        }

# Tablas de relación
class UsuarioPerfil(db.Model):
    __tablename__ = 'usuario_perfil'
    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
    perfil_id = db.Column(db.Integer, db.ForeignKey('perfiles.id'), nullable=False)
    activo = db.Column(db.Boolean, default=True)
    creador = db.Column(db.String(100))
    creacion = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    modificador = db.Column(db.String(100))
    modificacion = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    
    def to_dict(self):
        return {
            'id': self.id,
            'usuario_id': self.usuario_id,
            'perfil_id': self.perfil_id,
            'activo': self.activo,
            'creador': self.creador,
            'creacion': self.creacion.isoformat() if self.creacion else None,
            'modificador': self.modificador,
            'modificacion': self.modificacion.isoformat() if self.modificacion else None
        }

class PerfilMenu(db.Model):
    __tablename__ = 'perfil_menu'
    id = db.Column(db.Integer, primary_key=True)
    perfil_id = db.Column(db.Integer, db.ForeignKey('perfiles.id'), nullable=False)
    menu_id = db.Column(db.Integer, db.ForeignKey('menus.id'), nullable=False)
    activo = db.Column(db.Boolean, default=True)
    creador = db.Column(db.String(100))
    creacion = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    modificador = db.Column(db.String(100))
    modificacion = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    
    def to_dict(self):
        return {
            'id': self.id,
            'perfil_id': self.perfil_id,
            'menu_id': self.menu_id,
            'activo': self.activo,
            'creador': self.creador,
            'creacion': self.creacion.isoformat() if self.creacion else None,
            'modificador': self.modificador,
            'modificacion': self.modificacion.isoformat() if self.modificacion else None
        }

class UsuarioCoe(db.Model):
    __tablename__ = 'usuario_coe'
    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
    coe_id = db.Column(db.Integer, db.ForeignKey('coes.id'), nullable=False)
    provincia_id = db.Column(db.Integer, db.ForeignKey('provincias.id'))
    canton_id = db.Column(db.Integer, db.ForeignKey('cantones.id'))
    parroquia_id = db.Column(db.Integer, db.ForeignKey('parroquias.id'))
    mesa_id = db.Column(db.Integer)
    activo = db.Column(db.Boolean, default=True)
    creador = db.Column(db.String(100))
    creacion = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    modificador = db.Column(db.String(100))
    modificacion = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    
    def to_dict(self):
        return {
            'id': self.id,
            'usuario_id': self.usuario_id,
            'coe_id': self.coe_id,
            'provincia_id': self.provincia_id,
            'canton_id': self.canton_id,
            'parroquia_id': self.parroquia_id,
            'mesa_id': self.mesa_id,
            'activo': self.activo,
            'creador': self.creador,
            'creacion': self.creacion.isoformat() if self.creacion else None,
            'modificador': self.modificador,
            'modificacion': self.modificacion.isoformat() if self.modificacion else None
        }

class MesaCoe(db.Model):
    __tablename__ = 'mesa_coe'
    id = db.Column(db.Integer, primary_key=True)
    mesa_id = db.Column(db.Integer, db.ForeignKey('mesas.id'), nullable=False)
    coe_id = db.Column(db.Integer, db.ForeignKey('coes.id'), nullable=False)
    activo = db.Column(db.Boolean, default=True)
    creador = db.Column(db.String(100))
    creacion = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    modificador = db.Column(db.String(100))
    modificacion = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    
    def to_dict(self):
        return {
            'id': self.id,
            'mesa_id': self.mesa_id,
            'coe_id': self.coe_id,
            'activo': self.activo,
            'creador': self.creador,
            'creacion': self.creacion.isoformat() if self.creacion else None,
            'modificador': self.modificador,
            'modificacion': self.modificacion.isoformat() if self.modificacion else None
        }

class CoeActa(db.Model):
    __tablename__ = 'coe_actas'
    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
    emergencia_id = db.Column(db.Integer, db.ForeignKey('emergencias.id'), nullable=False)
    fecha_sesion = db.Column(db.DateTime)
    hora_sesion = db.Column(db.Text)
    activo = db.Column(db.Boolean, default=True)
    creador = db.Column(db.String(100))
    creacion = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    modificador = db.Column(db.String(100))
    modificacion = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    # Relaciones
    usuario = db.relationship('Usuario', backref='coe_actas')
    emergencia = db.relationship('Emergencia', backref='coe_actas')

    def to_dict(self):
        return {
            'id': self.id,
            'usuario_id': self.usuario_id,
            'emergencia_id': self.emergencia_id,
            'fecha_sesion': self.fecha_sesion.isoformat() if self.fecha_sesion else None,
            'hora_sesion': self.hora_sesion,
            'activo': self.activo,
            'creador': self.creador,
            'creacion': self.creacion.isoformat() if self.creacion else None,
            'modificador': self.modificador,
            'modificacion': self.modificacion.isoformat() if self.modificacion else None
        }

class ResolucionEstado(db.Model):
    __tablename__ = 'resolucion_estados'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.Text, nullable=False)
    descripcion = db.Column(db.Text)
    activo = db.Column(db.Boolean, default=True)
    creador = db.Column(db.Text)
    creacion = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    modificador = db.Column(db.Text)
    modificacion = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    def to_dict(self):
        return {
            'id': self.id,
            'nombre': self.nombre,
            'descripcion': self.descripcion,
            'activo': self.activo,
            'creador': self.creador,
            'creacion': self.creacion.isoformat() if self.creacion else None,
            'modificador': self.modificador,
            'modificacion': self.modificacion.isoformat() if self.modificacion else None
        }

class CoeActaResolucion(db.Model):
    __tablename__ = 'coe_acta_resoluciones'
    id = db.Column(db.Integer, primary_key=True)
    coe_acta_id = db.Column(db.Integer, db.ForeignKey('coe_actas.id'), nullable=False)
    mesa_id = db.Column(db.Integer, db.ForeignKey('mesas.id'), nullable=False)
    detalle = db.Column(db.Text)
    fecha_cumplimiento = db.Column(db.DateTime)
    responsable = db.Column(db.Text)
    resolucion_estado_id = db.Column(db.Integer, db.ForeignKey('resolucion_estados.id'), nullable=False)
    activo = db.Column(db.Boolean, default=True)
    creador = db.Column(db.String(100))
    creacion = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    modificador = db.Column(db.String(100))
    modificacion = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    # Relaciones
    coe_acta = db.relationship('CoeActa', backref='resoluciones')
    mesa = db.relationship('Mesa', backref='resoluciones')
    resolucion_estado = db.relationship('ResolucionEstado', backref='resoluciones')

    def to_dict(self):
        return {
            'id': self.id,
            'coe_acta_id': self.coe_acta_id,
            'mesa_id': self.mesa_id,
            'detalle': self.detalle,
            'fecha_cumplimiento': self.fecha_cumplimiento.isoformat() if self.fecha_cumplimiento else None,
            'responsable': self.responsable,
            'resolucion_estado_id': self.resolucion_estado_id,
            'activo': self.activo,
            'creador': self.creador,
            'creacion': self.creacion.isoformat() if self.creacion else None,
            'modificador': self.modificador,
            'modificacion': self.modificacion.isoformat() if self.modificacion else None
        }

class AfectacionVariableRegistroDetalle(db.Model):
    __tablename__ = 'afectacion_variable_registro_detalles'
    id = db.Column(db.Integer, primary_key=True)
    afectacion_variable_registro_id = db.Column(db.Integer, db.ForeignKey('afectacion_variable_registros.id'), nullable=False)
    infraestructura_id = db.Column(db.Integer, db.ForeignKey('infraestructuras.id'), nullable=False)
    costo = db.Column(db.Integer, nullable=False)
    activo = db.Column(db.Boolean, default=True)
    creador = db.Column(db.Text)
    creacion = db.Column(db.DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))
    modificador = db.Column(db.Text)
    modificacion = db.Column(db.DateTime(timezone=True))

    # Relaciones
    afectacion_variable_registro = db.relationship('AfectacionVariableRegistro', backref='detalles')
    infraestructura = db.relationship('Infraestructura', backref='afectacion_detalles')

    def to_dict(self):
        return {
            'id': self.id,
            'afectacion_variable_registro_id': self.afectacion_variable_registro_id,
            'infraestructura_id': self.infraestructura_id,
            'costo': self.costo,
            'activo': self.activo,
            'creador': self.creador,
            'creacion': self.creacion.isoformat() if self.creacion else None,
            'modificador': self.modificador,
            'modificacion': self.modificacion.isoformat() if self.modificacion else None
        }
