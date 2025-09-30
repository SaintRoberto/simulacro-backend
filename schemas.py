from marshmallow import Schema, fields, validate, ValidationError, pre_load
import re

class UsuarioCreateSchema(Schema):
    institucion_id = fields.Int(required=True, validate=validate.Range(min=1))
    usuario = fields.Str(required=True, validate=validate.Length(min=3, max=100))
    clave = fields.Str(required=True, validate=validate.Length(min=8))
    descripcion = fields.Str(validate=validate.Length(max=255), allow_none=True)
    celular = fields.Str(validate=validate.Regexp(r'^\d{10}$', error="Celular debe tener 10 dígitos"), allow_none=True)
    correo = fields.Email(required=True, validate=validate.Length(max=150))
    activo = fields.Bool(missing=True)
    aprobado = fields.Bool(missing=False)
    creador = fields.Str(missing='Sistema', validate=validate.Length(max=100))

    @pre_load
    def clean_data(self, data, **kwargs):
        # Sanitize strings
        for field in ['usuario', 'descripcion', 'creador']:
            if field in data and data[field]:
                data[field] = self.sanitize_string(data[field])
        return data

    def sanitize_string(self, value):
        # Basic sanitization: remove potential script tags and HTML
        return re.sub(r'<[^>]+>', '', str(value)).strip()

class UsuarioUpdateSchema(Schema):
    institucion_id = fields.Int(validate=validate.Range(min=1), allow_none=True)
    usuario = fields.Str(validate=validate.Length(min=3, max=100), allow_none=True)
    clave = fields.Str(validate=validate.Length(min=8), allow_none=True)
    descripcion = fields.Str(validate=validate.Length(max=255), allow_none=True)
    celular = fields.Str(validate=validate.Regexp(r'^\d{10}$', error="Celular debe tener 10 dígitos"), allow_none=True)
    correo = fields.Email(validate=validate.Length(max=150), allow_none=True)
    activo = fields.Bool(allow_none=True)
    aprobado = fields.Bool(allow_none=True)
    modificador = fields.Str(missing='Sistema', validate=validate.Length(max=100))

    @pre_load
    def clean_data(self, data, **kwargs):
        for field in ['usuario', 'descripcion', 'modificador']:
            if field in data and data[field]:
                data[field] = self.sanitize_string(data[field])
        return data

    def sanitize_string(self, value):
        return re.sub(r'<[^>]+>', '', str(value)).strip()

class LoginSchema(Schema):
    usuario = fields.Str(required=True, validate=validate.Length(min=1, max=100))
    clave = fields.Str(required=True, validate=validate.Length(min=1))

    @pre_load
    def clean_data(self, data, **kwargs):
        data['usuario'] = self.sanitize_string(data['usuario'])
        return data

    def sanitize_string(self, value):
        return re.sub(r'<[^>]+>', '', str(value)).strip()

# Output schemas for safe serialization
class UsuarioResponseSchema(Schema):
    id = fields.Int()
    institucion_id = fields.Int()
    usuario = fields.Str()
    correo = fields.Email()
    nombres = fields.Str()  # Note: this field is in models but not in routes
    apellidos = fields.Str()  # Note: this field is in models but not in routes
    cedula = fields.Str()    # Note: this field is in models but not in routes
    celular = fields.Str()
    estado = fields.Str()
    aprobado = fields.Bool()
    creador = fields.Str()
    creacion = fields.DateTime()
    modificador = fields.Str()
    modificacion = fields.DateTime()

    @pre_load
    def encode_output(self, data, **kwargs):
        # Ensure safe output encoding
        for field in ['usuario', 'creador', 'modificador']:
            if field in data and data[field]:
                data[field] = self.html_escape(data[field])
        return data

    def html_escape(self, value):
        import html
        return html.escape(str(value))