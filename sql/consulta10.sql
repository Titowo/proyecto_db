UPDATE core_articulo
SET stock = stock - 1,
    estado_publicacion = CASE WHEN (stock - 1) = 0 THEN 'Vendido' ELSE estado_publicacion END
WHERE id_articulo = 1 AND stock >= 1;
