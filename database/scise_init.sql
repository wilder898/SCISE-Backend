-- Script base generado desde los modelos actuales de SCISE
-- Revisar antes de ejecutar en produccion.


CREATE TABLE roles (
	id BIGSERIAL NOT NULL, 
	nombre VARCHAR(100) NOT NULL, 
	descripcion TEXT, 
	PRIMARY KEY (id), 
	UNIQUE (nombre)
);

CREATE INDEX ix_roles_id ON roles (id);


CREATE TABLE usuarios (
	id BIGSERIAL NOT NULL, 
	documento VARCHAR(50) NOT NULL, 
	nombre VARCHAR(150) NOT NULL, 
	correo VARCHAR(150), 
	contrasena TEXT NOT NULL, 
	area VARCHAR(100), 
	estado VARCHAR(20) NOT NULL, 
	rol_id BIGINT NOT NULL, 
	PRIMARY KEY (id), 
	UNIQUE (documento), 
	UNIQUE (correo), 
	FOREIGN KEY(rol_id) REFERENCES roles (id)
);

CREATE INDEX ix_usuarios_rol_id ON usuarios (rol_id);

CREATE INDEX ix_usuarios_id ON usuarios (id);


CREATE TABLE estudiantes (
	id BIGSERIAL NOT NULL, 
	codigo_barras VARCHAR(100), 
	documento VARCHAR(50) NOT NULL, 
	nombre VARCHAR(150) NOT NULL, 
	email VARCHAR(150), 
	rol VARCHAR(50) NOT NULL, 
	ficha VARCHAR(100), 
	celular VARCHAR(20), 
	estado VARCHAR(20) NOT NULL, 
	fecha_registro TIMESTAMP WITHOUT TIME ZONE NOT NULL, 
	usuario_crea BIGINT NOT NULL, 
	PRIMARY KEY (id), 
	UNIQUE (codigo_barras), 
	UNIQUE (documento), 
	UNIQUE (email), 
	FOREIGN KEY(usuario_crea) REFERENCES usuarios (id)
);

CREATE INDEX ix_estudiantes_id ON estudiantes (id);

CREATE INDEX ix_estudiantes_usuario_crea ON estudiantes (usuario_crea);


CREATE TABLE auditoria (
	id BIGSERIAL NOT NULL, 
	evento VARCHAR(150) NOT NULL, 
	tipo_auditoria VARCHAR(100), 
	tabla_id BIGINT, 
	valor_anterior TEXT, 
	valor_nuevo TEXT, 
	url TEXT, 
	fecha_novedad TIMESTAMP WITHOUT TIME ZONE NOT NULL, 
	usuario_id BIGINT NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(usuario_id) REFERENCES usuarios (id)
);

CREATE INDEX ix_auditoria_id ON auditoria (id);

CREATE INDEX ix_auditoria_usuario_id ON auditoria (usuario_id);


CREATE TABLE token_blacklist (
	id BIGSERIAL NOT NULL, 
	jti VARCHAR(255) NOT NULL, 
	fecha_revocacion TIMESTAMP WITHOUT TIME ZONE NOT NULL, 
	usuario_id BIGINT NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(usuario_id) REFERENCES usuarios (id)
);

CREATE INDEX ix_token_blacklist_id ON token_blacklist (id);

CREATE UNIQUE INDEX ix_token_blacklist_jti ON token_blacklist (jti);


CREATE TABLE equipos (
	id BIGSERIAL NOT NULL, 
	codigo_barras_equipo VARCHAR(100), 
	serial VARCHAR(150), 
	nombre VARCHAR(150) NOT NULL, 
	descripcion TEXT, 
	tipo_equipo VARCHAR(100), 
	fecha_registro TIMESTAMP WITHOUT TIME ZONE NOT NULL, 
	estado VARCHAR(20) NOT NULL, 
	usuario_registra BIGINT NOT NULL, 
	estudiante_id BIGINT NOT NULL, 
	PRIMARY KEY (id), 
	UNIQUE (codigo_barras_equipo), 
	UNIQUE (serial), 
	FOREIGN KEY(usuario_registra) REFERENCES usuarios (id), 
	FOREIGN KEY(estudiante_id) REFERENCES estudiantes (id)
);

CREATE INDEX ix_equipos_id ON equipos (id);

CREATE INDEX ix_equipos_usuario_registra ON equipos (usuario_registra);

CREATE INDEX ix_equipos_estudiante_id ON equipos (estudiante_id);


CREATE TABLE movimientos (
	id BIGSERIAL NOT NULL, 
	tipo_movimiento VARCHAR(20) NOT NULL, 
	fecha_registro TIMESTAMP WITHOUT TIME ZONE NOT NULL, 
	usuario_id BIGINT NOT NULL, 
	equipo_id BIGINT NOT NULL, 
	estudiante_id BIGINT NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(usuario_id) REFERENCES usuarios (id), 
	FOREIGN KEY(equipo_id) REFERENCES equipos (id), 
	FOREIGN KEY(estudiante_id) REFERENCES estudiantes (id)
);

CREATE INDEX ix_movimientos_estudiante_id ON movimientos (estudiante_id);

CREATE INDEX ix_movimientos_equipo_id ON movimientos (equipo_id);

CREATE INDEX ix_movimientos_usuario_id ON movimientos (usuario_id);

CREATE INDEX ix_movimientos_id ON movimientos (id);

INSERT INTO roles (id, nombre, descripcion) VALUES (1, 'Administrador', 'Acceso completo al sistema') ON CONFLICT (id) DO NOTHING;

INSERT INTO roles (id, nombre, descripcion) VALUES (2, 'Seguridad', 'Registro de movimientos') ON CONFLICT (id) DO NOTHING;

INSERT INTO roles (id, nombre, descripcion) VALUES (3, 'Aprendiz', 'Consulta de equipos propios') ON CONFLICT (id) DO NOTHING;

INSERT INTO roles (id, nombre, descripcion) VALUES (4, 'Instructor', 'Consulta y validacion') ON CONFLICT (id) DO NOTHING;

INSERT INTO usuarios (id, documento, nombre, correo, contrasena, area, estado, rol_id) VALUES (1, '1000000000', 'Administrador SCISE', 'admin@scise.sena.edu.co', '$2b$12$fa2oqoxujwWvAJF4X0NcSuJWg4YODh/wUz/oRYoqJ3PZb9kZBrqo6', NULL, 'ACTIVO', 1) ON CONFLICT (correo) DO NOTHING;
