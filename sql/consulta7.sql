SELECT r.id_reporte, a.nombre AS articulo_sospechoso, r.motivo, r.fecha
FROM core_reporte r
JOIN core_articulo a ON r.id_articulo = a.id_articulo
WHERE r.estado = 'Pendiente';
