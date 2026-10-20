ALTER TABLE core_usuario
ADD CONSTRAINT uq_correo_unico UNIQUE (correo);
