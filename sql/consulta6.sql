SELECT v.fecha_compra, a.nombre AS articulo, dv.cantidad_acordada, dv.precio_unitario
FROM core_venta v
JOIN core_detalle_venta dv ON v.id_venta = dv.id_venta
JOIN core_chat ch ON v.id_chat = ch.id_chat
JOIN core_articulo a ON ch.id_articulo = a.id_articulo
WHERE ch.id_vendedor = 1;
