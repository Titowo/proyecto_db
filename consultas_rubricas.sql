-- 1. Select con JOIN (Catálogo Básico)
-- Obtiene el nombre, precio y nombre de la categoría de todos los artículos activos.
SELECT a.nombre, a.precio, c.nombre AS categoria 
FROM core_articulo a
JOIN core_categoria c ON a.id_categoria = c.id_categoria
WHERE a.estado_publicacion = 'Disponible';

-- 2. Filtros Dinámicos (Búsqueda)
-- Simula la consulta de tu view: Filtra por categoría, rango de precio y talla.
SELECT nombre, precio, talla, marca 
FROM core_articulo 
WHERE id_categoria = 1 
  AND precio BETWEEN 30000 AND 80000 
  AND talla = 'M' 
  AND estado_publicacion = 'Disponible';

-- 3. Insert (Registro de Usuario)
-- Crea un nuevo usuario en la plataforma (ignora si el correo ya existe para evitar errores).
INSERT INTO core_usuario (nombre1, apellido1, correo, contrasena, fecha_registro) 
VALUES ('Juan', 'Perez', 'juan.perez@email.com', 'hash_contrasena', CURRENT_TIMESTAMP)
ON CONFLICT (correo) DO NOTHING;


-- 4. Insert (Publicación de Artículo)
-- El usuario (id=1) publica unas zapatillas en la categoría (id=2).
INSERT INTO core_articulo (nombre, descripcion, precio, stock, talla, marca, estado_conservacion, estado_publicacion, fecha_publicacion, id_usuario, id_categoria) 
VALUES ('Nike Dunk Low', 'Zapatillas sin uso', 120000, 1, 'US 10', 'Nike', 'Nuevo', 'Disponible', CURRENT_TIMESTAMP, 1, 2);

-- 5. Update (Gestión de Perfil)
-- Un usuario actualiza su número de teléfono.
UPDATE core_usuario 
SET telefono = '+56912345678' 
WHERE id_usuario = 1;

-- 6. Update (Transacción de Venta)
-- Descuenta el stock de un artículo tras confirmarse una venta desde el chat.
UPDATE core_articulo 
SET stock = stock - 1, 
    estado_publicacion = CASE WHEN (stock - 1) = 0 THEN 'Vendido' ELSE estado_publicacion END
WHERE id_articulo = 1 AND stock >= 1;

-- 7. Delete (Gestión de Carrito)
-- Elimina un artículo específico del carrito de un usuario.
DELETE FROM core_carrito 
WHERE id_usuario = 1 AND id_articulo = 1;

-- 8. Agrupación (Métricas del Catálogo)
-- Cuenta cuántos artículos disponibles hay por cada categoría.
SELECT c.nombre AS categoria, COUNT(a.id_articulo) AS total_articulos
FROM core_categoria c
LEFT JOIN core_articulo a ON c.id_categoria = a.id_categoria AND a.estado_publicacion = 'Disponible'
GROUP BY c.id_categoria, c.nombre;

-- 9. Historial de Ventas (Multi-JOIN)
-- Muestra el historial de ventas concretadas de un vendedor específico.
SELECT v.fecha_compra, a.nombre AS articulo, dv.cantidad_acordada, dv.precio_unitario
FROM core_venta v
JOIN core_detalle_venta dv ON v.id_venta = dv.id_venta
JOIN core_chat ch ON v.id_chat = ch.id_chat
JOIN core_articulo a ON ch.id_articulo = a.id_articulo
WHERE ch.id_vendedor = 1;

-- 10. Select de Reportes Pendientes
-- Lista los artículos que tienen reportes no gestionados, incluyendo el motivo.
SELECT r.id_reporte, a.nombre AS articulo_sospechoso, r.motivo, r.fecha 
FROM core_reporte r
JOIN core_articulo a ON r.id_articulo = a.id_articulo
WHERE r.estado = 'Pendiente';
