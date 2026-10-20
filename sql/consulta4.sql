SELECT nombre, precio, talla, marca
FROM core_articulo
WHERE id_categoria = 1
  AND precio BETWEEN 30000 AND 80000
  AND talla = 'M'
  AND estado_publicacion = 'Disponible';
