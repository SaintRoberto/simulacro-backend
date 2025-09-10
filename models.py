from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timezone

db = SQLAlchemy()

class Categoria(db.Model):
    __tablename__ = 'categorias'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    descripcion = db.Column(db.Text)
    estado = db.Column(db.String(20), default='Activo')
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
            'estado': self.estado,
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
    estado = db.Column(db.String(20), default='Activo')
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
            'estado': self.estado,
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
    estado = db.Column(db.String(20), default='Activo')
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
            'estado': self.estado,
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
    estado = db.Column(db.String(20), default='Activo')
    creador = db.Column(db.String(100))
    creacion = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    modificador = db.Column(db.String(100))
    modificacion = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    
    def to_dict(self):
        return {
            'id': self.id,
            'nombre': self.nombre,
            'descripcion': self.descripcion,
            'estado': self.estado,
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
    estado = db.Column(db.String(20), default='Activo')
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
            'estado': self.estado,
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
    estado = db.Column(db.String(20), default='Activo')
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
            'estado': self.estado,
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
    estado = db.Column(db.String(20), default='Activo')
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
            'estado': self.estado,
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
    estado = db.Column(db.String(20), default='Activo')
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
            'estado': self.estado,
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
    estado = db.Column(db.String(20), default='Activo')
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
            'estado': self.estado,
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
    estado = db.Column(db.String(20), default='Activo')
    creador = db.Column(db.String(100))
    creacion = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    modificador = db.Column(db.String(100))
    modificacion = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    
    def to_dict(self):
        return {
            'id': self.id,
            'usuario_id': self.usuario_id,
            'perfil_id': self.perfil_id,
            'estado': self.estado,
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
    estado = db.Column(db.String(20), default='Activo')
    creador = db.Column(db.String(100))
    creacion = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    modificador = db.Column(db.String(100))
    modificacion = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    
    def to_dict(self):
        return {
            'id': self.id,
            'perfil_id': self.perfil_id,
            'menu_id': self.menu_id,
            'estado': self.estado,
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
    estado = db.Column(db.String(20), default='Activo')
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
            'estado': self.estado,
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
    estado = db.Column(db.String(20), default='Activo')
    creador = db.Column(db.String(100))
    creacion = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    modificador = db.Column(db.String(100))
    modificacion = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    
    def to_dict(self):
        return {
            'id': self.id,
            'mesa_id': self.mesa_id,
            'coe_id': self.coe_id,
            'estado': self.estado,
            'creador': self.creador,
            'creacion': self.creacion.isoformat() if self.creacion else None,
            'modificador': self.modificador,
            'modificacion': self.modificacion.isoformat() if self.modificacion else None
        }
