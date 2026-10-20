SELECT c.nombre AS categoria, COUNT(a.id_articulo) AS total_articulos
FROM core_categoria c
LEFT JOIN core_articulo a ON c.id_categoria = a.id_categoria
     AND a.estado_publicacion = 'Disponible'
GROUP BY c.id_categoria, c.nombre;
