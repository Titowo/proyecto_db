SELECT a.nombre, a.precio, c.nombre AS categoria
FROM core_articulo a
JOIN core_categoria c ON a.id_categoria = c.id_categoria
WHERE a.estado_publicacion = 'Disponible';
