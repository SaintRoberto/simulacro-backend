-- Database Schema for Simulacros Backend
-- Generated from entity structures and routes
-- Compatible with PostgreSQL

-- Table: institucion_categorias
CREATE TABLE institucion_categorias (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    descripcion TEXT,
    activo BOOLEAN DEFAULT TRUE,
    creador VARCHAR(100),
    creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    modificador VARCHAR(100),
    modificacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Table: categorias
CREATE TABLE categorias (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    descripcion TEXT,
    activo BOOLEAN DEFAULT TRUE,
    creador VARCHAR(100),
    creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    modificador VARCHAR(100),
    modificacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Table: instituciones
CREATE TABLE instituciones (
    id SERIAL PRIMARY KEY,
    institucion_categoria_id INTEGER,
    nombre VARCHAR(200) NOT NULL,
    siglas VARCHAR(50),
    observaciones TEXT,
    activo BOOLEAN DEFAULT TRUE,
    creador VARCHAR(100),
    creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    modificador VARCHAR(100),
    modificacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (institucion_categoria_id) REFERENCES institucion_categorias(id)
);

-- Table: usuarios
CREATE TABLE usuarios (
    id SERIAL PRIMARY KEY,
    institucion_id INTEGER NOT NULL,
    usuario VARCHAR(100) UNIQUE NOT NULL,
    clave VARCHAR(255),
    descripcion TEXT,
    celular VARCHAR(20),
    correo VARCHAR(150) UNIQUE NOT NULL,
    nombres VARCHAR(100),
    apellidos VARCHAR(100),
    cedula VARCHAR(20) UNIQUE,
    aprobado BOOLEAN DEFAULT FALSE,
    activo BOOLEAN DEFAULT TRUE,
    creador VARCHAR(100),
    creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    modificador VARCHAR(100),
    modificacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (institucion_id) REFERENCES instituciones(id)
);

-- Table: perfiles
CREATE TABLE perfiles (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    descripcion TEXT,
    activo BOOLEAN DEFAULT TRUE,
    creador VARCHAR(100),
    creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    modificador VARCHAR(100),
    modificacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Table: menus
CREATE TABLE menus (
    id SERIAL PRIMARY KEY,
    padre_id INTEGER,
    orden INTEGER DEFAULT 0,
    nombre VARCHAR(100) NOT NULL,
    abreviatura VARCHAR(50),
    ruta VARCHAR(200),
    activo BOOLEAN DEFAULT TRUE,
    creador VARCHAR(100),
    creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    modificador VARCHAR(100),
    modificacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (padre_id) REFERENCES menus(id)
);

-- Table: provincias
CREATE TABLE provincias (
    id SERIAL PRIMARY KEY,
    dpa VARCHAR(10) UNIQUE NOT NULL,
    nombre VARCHAR(100) NOT NULL,
    abreviatura VARCHAR(10),
    activo BOOLEAN DEFAULT TRUE,
    creador VARCHAR(100),
    creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    modificador VARCHAR(100),
    modificacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Table: cantones
CREATE TABLE cantones (
    id SERIAL PRIMARY KEY,
    provincia_id INTEGER NOT NULL,
    dpa VARCHAR(10) UNIQUE NOT NULL,
    nombre VARCHAR(100) NOT NULL,
    abreviatura VARCHAR(10),
    activo BOOLEAN DEFAULT TRUE,
    creador VARCHAR(100),
    creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    modificador VARCHAR(100),
    modificacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (provincia_id) REFERENCES provincias(id)
);

-- Table: parroquias
CREATE TABLE parroquias (
    id SERIAL PRIMARY KEY,
    provincia_id INTEGER NOT NULL,
    canton_id INTEGER NOT NULL,
    dpa VARCHAR(10) UNIQUE NOT NULL,
    nombre VARCHAR(100) NOT NULL,
    abreviatura VARCHAR(10),
    activo BOOLEAN DEFAULT TRUE,
    creador VARCHAR(100),
    creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    modificador VARCHAR(100),
    modificacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (provincia_id) REFERENCES provincias(id),
    FOREIGN KEY (canton_id) REFERENCES cantones(id)
);

-- Table: infraestructuras
CREATE TABLE infraestructuras (
    id SERIAL PRIMARY KEY,
    infraestructura_tipo_id INTEGER,
    nombre TEXT,
    direccion TEXT,
    provincia_id INTEGER NOT NULL,
    canton_id INTEGER NOT NULL,
    parroquia_id INTEGER NOT NULL,
    tipologia TEXT,
    institucion TEXT,
    longitud DECIMAL(15,12) DEFAULT 0,
    latitud DECIMAL(15,12) DEFAULT 0,
    activo BOOLEAN DEFAULT TRUE,
    creador TEXT,
    creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    modificador TEXT,
    modificacion TIMESTAMP,
    FOREIGN KEY (provincia_id) REFERENCES provincias(id),
    FOREIGN KEY (canton_id) REFERENCES cantones(id),
    FOREIGN KEY (parroquia_id) REFERENCES parroquias(id)
);

-- Table: coes
CREATE TABLE coes (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(200) NOT NULL,
    siglas VARCHAR(50),
    descripcion TEXT,
    activo BOOLEAN DEFAULT TRUE,
    creador VARCHAR(100),
    creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    modificador VARCHAR(100),
    modificacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Table: mesa_grupos
CREATE TABLE mesa_grupos (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(200) NOT NULL,
    abreviatura VARCHAR(50),
    descripcion TEXT,
    activo BOOLEAN DEFAULT TRUE,
    creador VARCHAR(100),
    creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    modificador VARCHAR(100),
    modificacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Table: mesas
CREATE TABLE mesas (
    id SERIAL PRIMARY KEY,
    coe_id INTEGER,
    mesa_grupo_id INTEGER,
    nombre VARCHAR(200) NOT NULL,
    siglas VARCHAR(50),
    activo BOOLEAN DEFAULT TRUE,
    creador VARCHAR(100),
    creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    modificador VARCHAR(100),
    modificacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (coe_id) REFERENCES coes(id),
    FOREIGN KEY (mesa_grupo_id) REFERENCES mesa_grupos(id)
);

-- Table: usuario_perfil
CREATE TABLE usuario_perfil (
    id SERIAL PRIMARY KEY,
    usuario_id INTEGER NOT NULL,
    perfil_id INTEGER NOT NULL,
    activo BOOLEAN DEFAULT TRUE,
    creador VARCHAR(100),
    creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    modificador VARCHAR(100),
    modificacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (usuario_id) REFERENCES usuarios(id),
    FOREIGN KEY (perfil_id) REFERENCES perfiles(id)
);

-- Table: perfil_menu
CREATE TABLE perfil_menu (
    id SERIAL PRIMARY KEY,
    perfil_id INTEGER NOT NULL,
    menu_id INTEGER NOT NULL,
    activo BOOLEAN DEFAULT TRUE,
    creador VARCHAR(100),
    creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    modificador VARCHAR(100),
    modificacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (perfil_id) REFERENCES perfiles(id),
    FOREIGN KEY (menu_id) REFERENCES menus(id)
);

-- Table: usuario_coe
CREATE TABLE usuario_coe (
    id SERIAL PRIMARY KEY,
    usuario_id INTEGER NOT NULL,
    coe_id INTEGER NOT NULL,
    provincia_id INTEGER,
    canton_id INTEGER,
    parroquia_id INTEGER,
    mesa_id INTEGER,
    activo BOOLEAN DEFAULT TRUE,
    creador VARCHAR(100),
    creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    modificador VARCHAR(100),
    modificacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (usuario_id) REFERENCES usuarios(id),
    FOREIGN KEY (coe_id) REFERENCES coes(id),
    FOREIGN KEY (provincia_id) REFERENCES provincias(id),
    FOREIGN KEY (canton_id) REFERENCES cantones(id),
    FOREIGN KEY (parroquia_id) REFERENCES parroquias(id)
);

-- Table: mesa_coe
CREATE TABLE mesa_coe (
    id SERIAL PRIMARY KEY,
    mesa_id INTEGER NOT NULL,
    coe_id INTEGER NOT NULL,
    activo BOOLEAN DEFAULT TRUE,
    creador VARCHAR(100),
    creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    modificador VARCHAR(100),
    modificacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (mesa_id) REFERENCES mesas(id),
    FOREIGN KEY (coe_id) REFERENCES coes(id)
);

-- Table: niveles_alerta
CREATE TABLE niveles_alerta (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    descripcion TEXT,
    activo BOOLEAN DEFAULT TRUE,
    creador VARCHAR(100),
    creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    modificador VARCHAR(100),
    modificacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Table: niveles_afectacion
CREATE TABLE niveles_afectacion (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    descripcion TEXT,
    activo BOOLEAN DEFAULT TRUE,
    creador VARCHAR(100),
    creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    modificador VARCHAR(100),
    modificacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Table: emergencias
CREATE TABLE emergencias (
    id SERIAL PRIMARY KEY,
    nombre TEXT NOT NULL,
    antecedentes TEXT,
    situacion_actual TEXT,
    nivel_afectacion_id INTEGER,
    nivel_alerta_id INTEGER,
    fecha_inicio TIMESTAMP,
    fecha_fin TIMESTAMP,
    activo BOOLEAN DEFAULT TRUE,
    creador VARCHAR(100),
    creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    modificador VARCHAR(100),
    modificacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (nivel_afectacion_id) REFERENCES niveles_afectacion(id),
    FOREIGN KEY (nivel_alerta_id) REFERENCES niveles_alerta(id)
);

-- Table: coe_actas
CREATE TABLE coe_actas (
    id SERIAL PRIMARY KEY,
    usuario_id INTEGER NOT NULL,
    emergencia_id INTEGER NOT NULL,
    fecha_sesion TIMESTAMP,
    hora_sesion TEXT,
    activo BOOLEAN DEFAULT TRUE,
    creador VARCHAR(100),
    creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    modificador VARCHAR(100),
    modificacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (usuario_id) REFERENCES usuarios(id),
    FOREIGN KEY (emergencia_id) REFERENCES emergencias(id)
);

-- Table: resolucion_estados
CREATE TABLE resolucion_estados (
    id SERIAL PRIMARY KEY,
    nombre TEXT NOT NULL,
    descripcion TEXT,
    activo BOOLEAN DEFAULT TRUE,
    creador TEXT,
    creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    modificador TEXT,
    modificacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Table: coe_acta_resoluciones
CREATE TABLE coe_acta_resoluciones (
    id SERIAL PRIMARY KEY,
    coe_acta_id INTEGER NOT NULL,
    mesa_id INTEGER NOT NULL,
    detalle TEXT,
    fecha_cumplimiento TIMESTAMP,
    responsable TEXT,
    resolucion_estado_id INTEGER NOT NULL,
    activo BOOLEAN DEFAULT TRUE,
    creador VARCHAR(100),
    creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    modificador VARCHAR(100),
    modificacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (coe_acta_id) REFERENCES coe_actas(id),
    FOREIGN KEY (mesa_id) REFERENCES mesas(id),
    FOREIGN KEY (resolucion_estado_id) REFERENCES resolucion_estados(id)
);

-- Table: afectacion_variables
CREATE TABLE afectacion_variables (
    id SERIAL PRIMARY KEY,
    coe_id INTEGER,
    mesa_grupo_id INTEGER,
    nombre TEXT NOT NULL,
    dato_tipo_id INTEGER,
    requiere_costo BOOLEAN DEFAULT FALSE,
    requiere_gis BOOLEAN DEFAULT FALSE,
    activo BOOLEAN DEFAULT TRUE,
    creador VARCHAR(100),
    creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    modificador VARCHAR(100),
    modificacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (coe_id) REFERENCES coes(id),
    FOREIGN KEY (mesa_grupo_id) REFERENCES mesa_grupos(id)
);

-- Table: afectacion_variable_registros
CREATE TABLE afectacion_variable_registros (
    id SERIAL PRIMARY KEY,
    emergencia_id INTEGER NOT NULL,
    provincia_id INTEGER NOT NULL,
    canton_id INTEGER NOT NULL,
    parroquia_id INTEGER NOT NULL,
    afectacion_variable_id INTEGER NOT NULL,
    cantidad INTEGER,
    costo INTEGER,
    activo BOOLEAN DEFAULT TRUE,
    creador TEXT,
    creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    modificador TEXT,
    modificacion TIMESTAMP,
    FOREIGN KEY (emergencia_id) REFERENCES emergencias(id),
    FOREIGN KEY (provincia_id) REFERENCES provincias(id),
    FOREIGN KEY (canton_id) REFERENCES cantones(id),
    FOREIGN KEY (parroquia_id) REFERENCES parroquias(id),
    FOREIGN KEY (afectacion_variable_id) REFERENCES afectacion_variables(id)
);

-- Table: afectacion_variable_registro_detalles
CREATE TABLE afectacion_variable_registro_detalles (
    id SERIAL PRIMARY KEY,
    afectacion_variable_registro_id INTEGER NOT NULL,
    infraestructura_id INTEGER NOT NULL,
    costo INTEGER NOT NULL,
    activo BOOLEAN DEFAULT TRUE,
    creador TEXT,
    creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    modificador TEXT,
    modificacion TIMESTAMP,
    FOREIGN KEY (afectacion_variable_registro_id) REFERENCES afectacion_variable_registros(id),
    FOREIGN KEY (infraestructura_id) REFERENCES infraestructuras(id)
);

-- Table: opciones
CREATE TABLE opciones (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    abreviatura VARCHAR(50),
    ruta VARCHAR(200),
    activo BOOLEAN DEFAULT TRUE,
    creador VARCHAR(100),
    creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    modificador VARCHAR(100),
    modificacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Table: recurso_categorias
CREATE TABLE recurso_categorias (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    descripcion TEXT,
    activo BOOLEAN DEFAULT TRUE,
    creador VARCHAR(100),
    creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    modificador VARCHAR(100),
    modificacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Table: recurso_grupos
CREATE TABLE recurso_grupos (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    descripcion TEXT,
    activo BOOLEAN DEFAULT TRUE,
    creador VARCHAR(100),
    creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    modificador VARCHAR(100),
    modificacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Table: recurso_tipos
CREATE TABLE recurso_tipos (
    id SERIAL PRIMARY KEY,
    recurso_grupo_id INTEGER NOT NULL,
    nombre VARCHAR(100) NOT NULL,
    descripcion TEXT,
    costo DECIMAL(10,2),
    complemento TEXT,
    activo BOOLEAN DEFAULT TRUE,
    creador VARCHAR(100),
    creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    modificador VARCHAR(100),
    modificacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (recurso_grupo_id) REFERENCES recurso_grupos(id)
);

-- Table: requerimiento_estados
CREATE TABLE requerimiento_estados (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    descripcion TEXT,
    activo BOOLEAN DEFAULT TRUE,
    creador VARCHAR(100),
    creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    modificador VARCHAR(100),
    modificacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Table: requerimientos
CREATE TABLE requerimientos (
    id SERIAL PRIMARY KEY,
    emergencia_id INTEGER NOT NULL,
    usuario_emisor_id INTEGER NOT NULL,
    usuario_receptor_id INTEGER NOT NULL,
    fecha_inicio TIMESTAMP,
    fecha_fin TIMESTAMP,
    porcentaje_avance INTEGER DEFAULT 0,
    requerimiento_estado_id INTEGER NOT NULL,
    activo BOOLEAN DEFAULT TRUE,
    creador VARCHAR(100),
    creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    modificador VARCHAR(100),
    modificacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (emergencia_id) REFERENCES emergencias(id),
    FOREIGN KEY (usuario_emisor_id) REFERENCES usuarios(id),
    FOREIGN KEY (usuario_receptor_id) REFERENCES usuarios(id),
    FOREIGN KEY (requerimiento_estado_id) REFERENCES requerimiento_estados(id)
);

-- Table: requerimiento_recursos
CREATE TABLE requerimiento_recursos (
    id SERIAL PRIMARY KEY,
    requerimiento_id INTEGER NOT NULL,
    recurso_grupo_id INTEGER,
    recurso_tipo_id INTEGER,
    cantidad INTEGER,
    costo DECIMAL(10,2),
    activo BOOLEAN DEFAULT TRUE,
    creador VARCHAR(100),
    creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    modificador VARCHAR(100),
    modificacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (requerimiento_id) REFERENCES requerimientos(id),
    FOREIGN KEY (recurso_grupo_id) REFERENCES recurso_grupos(id),
    FOREIGN KEY (recurso_tipo_id) REFERENCES recurso_tipos(id)
);

-- Table: respuesta_estados
CREATE TABLE respuesta_estados (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    descripcion TEXT,
    activo BOOLEAN DEFAULT TRUE,
    creador VARCHAR(100),
    creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    modificador VARCHAR(100),
    modificacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Table: requerimiento_respuestas
CREATE TABLE requerimiento_respuestas (
    id SERIAL PRIMARY KEY,
    requerimiento_id INTEGER NOT NULL,
    porcentaje_avance INTEGER,
    respuesta_estado_id INTEGER NOT NULL,
    respuesta_fecha TIMESTAMP,
    observaciones TEXT,
    activo BOOLEAN DEFAULT TRUE,
    creador VARCHAR(100),
    creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    modificador VARCHAR(100),
    modificacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (requerimiento_id) REFERENCES requerimientos(id),
    FOREIGN KEY (respuesta_estado_id) REFERENCES respuesta_estados(id)
);

-- Table: respuestas_avances
CREATE TABLE respuestas_avances (
    id SERIAL PRIMARY KEY,
    requerimiento_respuesta_id INTEGER NOT NULL,
    porcentaje_avance INTEGER,
    observaciones TEXT,
    activo BOOLEAN DEFAULT TRUE,
    creador VARCHAR(100),
    creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    modificador VARCHAR(100),
    modificacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (requerimiento_respuesta_id) REFERENCES requerimiento_respuestas(id)
);

-- Table: emergencia_parroquias
CREATE TABLE emergencia_parroquias (
    id SERIAL PRIMARY KEY,
    emergencia_id INTEGER NOT NULL,
    parroquia_id INTEGER NOT NULL,
    activo BOOLEAN DEFAULT TRUE,
    creador VARCHAR(100),
    creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    modificador VARCHAR(100),
    modificacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (emergencia_id) REFERENCES emergencias(id),
    FOREIGN KEY (parroquia_id) REFERENCES parroquias(id)
);

-- Table: usuario_perfil_coe_dpa_mesa (inferred from queries)
CREATE TABLE usuario_perfil_coe_dpa_mesa (
    id SERIAL PRIMARY KEY,
    usuario_id INTEGER NOT NULL,
    perfil_id INTEGER,
    coe_id INTEGER,
    provincia_id INTEGER,
    canton_id INTEGER,
    parroquia_id INTEGER,
    mesa_id INTEGER,
    activo BOOLEAN DEFAULT TRUE,
    creador VARCHAR(100),
    creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    modificador VARCHAR(100),
    modificacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (usuario_id) REFERENCES usuarios(id),
    FOREIGN KEY (perfil_id) REFERENCES perfiles(id),
    FOREIGN KEY (coe_id) REFERENCES coes(id),
    FOREIGN KEY (provincia_id) REFERENCES provincias(id),
    FOREIGN KEY (canton_id) REFERENCES cantones(id),
    FOREIGN KEY (parroquia_id) REFERENCES parroquias(id),
    FOREIGN KEY (mesa_id) REFERENCES mesas(id)
);