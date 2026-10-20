ALTER TABLE core_articulo
ADD CONSTRAINT chk_precio_positivo CHECK (precio >= 0);
