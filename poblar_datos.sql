-- =====================================================================
-- POBLAR BASE DE DATOS - Plataforma C2C Streetwear
-- Datos de prueba para ejecutar consultas_rubricas.sql
--
-- Requisitos: tablas ya creadas (python manage.py migrate) y VACIAS.
-- Todos los usuarios tienen la contrasena: clave1234
-- (guardada como hash PBKDF2 de Django, compatible con el futuro login)
--
-- Para volver a ejecutar el script, primero descomenta el bloque
-- "LIMPIEZA" (borra TODOS los datos de las tablas core_*).
-- =====================================================================

-- ---------------------------------------------------------------------
-- LIMPIEZA (opcional, en orden inverso a las dependencias)
-- ---------------------------------------------------------------------
-- DELETE FROM core_valoracion;
-- DELETE FROM core_detalle_venta;
-- DELETE FROM core_venta;
-- DELETE FROM core_mensaje;
-- DELETE FROM core_chat;
-- DELETE FROM core_reporte;
-- DELETE FROM core_favorito;
-- DELETE FROM core_carrito;
-- DELETE FROM core_foto_articulo;
-- DELETE FROM core_articulo;
-- DELETE FROM core_categoria;
-- DELETE FROM core_usuario;

-- ---------------------------------------------------------------------
-- USUARIOS (id 1 = vendedor principal; usuario 1 sin telefono para Q5)
-- ---------------------------------------------------------------------
INSERT INTO core_usuario (id_usuario, nombre1, nombre2, apellido1, apellido2, correo, contrasena, telefono, fecha_registro, foto_perfil) VALUES
(1, 'Matias',    'Ignacio',  'Rojas',   'Soto',   'matias.rojas@email.com',      'pbkdf2_sha256$1500000$5jevMSsl8IJqK94cUkledK$2tcB0Z0aa+KBkxV8jJ+LW/4j0N919eOTB467Bjrh9aE=', NULL,           '2026-08-01 10:00:00', '/media/perfiles/matias.jpg'),
(2, 'Camila',    NULL,       'Fuentes', 'Vega',   'camila.fuentes@email.com',    'pbkdf2_sha256$1500000$5jevMSsl8IJqK94cUkledK$2tcB0Z0aa+KBkxV8jJ+LW/4j0N919eOTB467Bjrh9aE=', '+56922334455', '2026-08-03 12:30:00', NULL),
(3, 'Sebastian', 'Andres',  'Araya',   'Lagos',  'sebastian.araya@email.com',   'pbkdf2_sha256$1500000$5jevMSsl8IJqK94cUkledK$2tcB0Z0aa+KBkxV8jJ+LW/4j0N919eOTB467Bjrh9aE=', '+56933445566', '2026-08-05 09:15:00', '/media/perfiles/sebastian.jpg'),
(4, 'Valentina', NULL,      'Mora',    'Diaz',   'valentina.mora@email.com',    'pbkdf2_sha256$1500000$5jevMSsl8IJqK94cUkledK$2tcB0Z0aa+KBkxV8jJ+LW/4j0N919eOTB467Bjrh9aE=', '+56944556677', '2026-08-10 18:45:00', NULL),
(5, 'Nicolas',   'Felipe',   'Pizarro', 'Bravo',  'nicolas.pizarro@email.com',   'pbkdf2_sha256$1500000$5jevMSsl8IJqK94cUkledK$2tcB0Z0aa+KBkxV8jJ+LW/4j0N919eOTB467Bjrh9aE=', NULL,           '2026-08-15 20:10:00', NULL),
(6, 'Catalina',  NULL,       'Herrera', 'Nunez',  'catalina.herrera@email.com',  'pbkdf2_sha256$1500000$5jevMSsl8IJqK94cUkledK$2tcB0Z0aa+KBkxV8jJ+LW/4j0N919eOTB467Bjrh9aE=', '+56955667788', '2026-08-20 14:00:00', NULL);

-- ---------------------------------------------------------------------
-- CATEGORIAS (1 = ropa con tallas S/M/L para Q2; 2 = zapatillas para Q4;
-- 5 = sin articulos disponibles, para ver el LEFT JOIN de Q8 con 0)
-- ---------------------------------------------------------------------
INSERT INTO core_categoria (id_categoria, nombre, descripcion) VALUES
(1, 'Poleras y Hoodies', 'Poleras, polerones y hoodies de marcas urbanas'),
(2, 'Zapatillas',        'Zapatillas de edicion limitada y de coleccion'),
(3, 'Gorros',            'Gorros, jockeys y beanies de coleccion'),
(4, 'Pantalones',        'Pantalones cargo, jeans y joggers'),
(5, 'Accesorios',        'Relojes, mochilas, cadenas y otros accesorios');

-- ---------------------------------------------------------------------
-- ARTICULOS
-- Disponibles: 1,2,3,4,7,8,11,12,13 | Vendidos: 6,9 | Pausados: 5,10
-- El articulo 1 tiene stock 1 (Q6 lo deja en 0 y lo marca 'Vendido')
-- ---------------------------------------------------------------------
INSERT INTO core_articulo (id_articulo, nombre, descripcion, precio, stock, talla, marca, estado_conservacion, estado_publicacion, fecha_publicacion, id_usuario, id_categoria) VALUES
(1,  'Hoodie Carhartt WIP Chase',      'Hoodie gris, usado un par de veces, sin manchas ni roturas', 45000.00,  1, 'M',      'Carhartt',    'Usado', 'Disponible', '2026-09-01 10:00:00', 2, 1),
(2,  'Polera Stussy Basic Logo',       'Polera negra con logo clasico, sin uso y con etiqueta',      35000.00,  2, 'M',      'Stussy',      'Nuevo', 'Disponible', '2026-09-02 11:00:00', 3, 1),
(3,  'Hoodie Supreme Box Logo',        'Hoodie rojo box logo, edicion limitada, nuevo en bolsa',     250000.00, 1, 'L',      'Supreme',     'Nuevo', 'Disponible', '2026-09-03 12:00:00', 1, 1),
(4,  'Polera Palace Tri-Ferg',         'Polera blanca con logo triferg, buen estado',                60000.00,  3, 'M',      'Palace',      'Usado', 'Disponible', '2026-09-03 15:30:00', 1, 1),
(5,  'Polera Essentials Fear of God',  'Polera beige oversize, nueva',                               55000.00,  1, 'M',      'Fear of God', 'Nuevo', 'Pausado',    '2026-09-04 09:00:00', 4, 1),
(6,  'Nike Air Force 1 Low White',     'Zapatillas blancas clasicas, usadas con cuidado',            75000.00,  0, 'US 9',   'Nike',        'Usado', 'Vendido',    '2026-09-01 16:00:00', 1, 2),
(7,  'New Era 59FIFTY Yankees',        'Jockey negro Yankees, talla ajustada, sin uso',              30000.00,  3, '7 1/4', 'New Era',     'Nuevo', 'Disponible', '2026-09-06 13:00:00', 1, 3),
(8,  'Jordan 1 Retro High Chicago',    'Zapatillas Chicago, con caja original y factura',            180000.00, 1, 'US 10',  'Jordan',      'Nuevo', 'Disponible', '2026-09-08 10:30:00', 2, 2),
(9,  'Gorro Beanie Carhartt',          'Beanie de lana color mostaza',                               18000.00,  0, 'Unica',  'Carhartt',    'Nuevo', 'Vendido',    '2026-09-09 19:00:00', 2, 3),
(10, 'Reloj Casio Vintage F-91W',      'Reloj digital clasico, funciona perfecto',                   40000.00,  1, 'Unica',  'Casio',       'Usado', 'Pausado',    '2026-09-10 08:20:00', 4, 5),
(11, 'Pantalon Cargo Dickies',         'Pantalon cargo verde oliva, sin uso',                        50000.00,  2, '32',     'Dickies',     'Nuevo', 'Disponible', '2026-09-11 17:00:00', 3, 4),
(12, 'Nike Dunk Low Panda',            'Dunk Low blanco y negro, nuevas en caja',                    110000.00, 1, 'US 8',   'Nike',        'Nuevo', 'Disponible', '2026-09-14 12:00:00', 5, 2),
(13, 'Adidas Samba OG',                'Samba blancas con detalles negros, usadas',                  95000.00,  1, 'US 9',   'Adidas',      'Usado', 'Disponible', '2026-09-16 14:00:00', 4, 2);

-- ---------------------------------------------------------------------
-- FOTOS (2 por articulo, la primera es la principal)
-- ---------------------------------------------------------------------
INSERT INTO core_foto_articulo (url_imagen, es_principal, id_articulo) VALUES
('/media/articulos/art01_1.jpg', TRUE,  1),  ('/media/articulos/art01_2.jpg', FALSE, 1),
('/media/articulos/art02_1.jpg', TRUE,  2),  ('/media/articulos/art02_2.jpg', FALSE, 2),
('/media/articulos/art03_1.jpg', TRUE,  3),  ('/media/articulos/art03_2.jpg', FALSE, 3),
('/media/articulos/art04_1.jpg', TRUE,  4),  ('/media/articulos/art04_2.jpg', FALSE, 4),
('/media/articulos/art05_1.jpg', TRUE,  5),  ('/media/articulos/art05_2.jpg', FALSE, 5),
('/media/articulos/art06_1.jpg', TRUE,  6),  ('/media/articulos/art06_2.jpg', FALSE, 6),
('/media/articulos/art07_1.jpg', TRUE,  7),  ('/media/articulos/art07_2.jpg', FALSE, 7),
('/media/articulos/art08_1.jpg', TRUE,  8),  ('/media/articulos/art08_2.jpg', FALSE, 8),
('/media/articulos/art09_1.jpg', TRUE,  9),  ('/media/articulos/art09_2.jpg', FALSE, 9),
('/media/articulos/art10_1.jpg', TRUE,  10), ('/media/articulos/art10_2.jpg', FALSE, 10),
('/media/articulos/art11_1.jpg', TRUE,  11), ('/media/articulos/art11_2.jpg', FALSE, 11),
('/media/articulos/art12_1.jpg', TRUE,  12), ('/media/articulos/art12_2.jpg', FALSE, 12),
('/media/articulos/art13_1.jpg', TRUE,  13), ('/media/articulos/art13_2.jpg', FALSE, 13);

-- ---------------------------------------------------------------------
-- CHATS (comprador, vendedor, articulo)
-- 1,2,4 terminaron en venta | 3,5,6 siguen en negociacion
-- ---------------------------------------------------------------------
INSERT INTO core_chat (id_chat, fecha_inicio, id_comprador, id_vendedor, id_articulo) VALUES
(1, '2026-09-05 10:00:00', 3, 1, 6),
(2, '2026-09-10 16:20:00', 4, 1, 7),
(3, '2026-09-20 12:00:00', 1, 2, 8),
(4, '2026-09-12 09:15:00', 5, 2, 9),
(5, '2026-09-22 18:40:00', 6, 3, 2),
(6, '2026-09-25 11:05:00', 5, 2, 1);

-- ---------------------------------------------------------------------
-- MENSAJES
-- ---------------------------------------------------------------------
INSERT INTO core_mensaje (id_mensaje, contenido, fecha_envio, id_chat, id_usuario) VALUES
(1,  'Hola! Sigue disponible las Air Force 1 en talla 9?',        '2026-09-05 10:00:00', 1, 3),
(2,  'Hola, si, estan disponibles',                                '2026-09-05 10:05:00', 1, 1),
(3,  'Perfecto, te las compro a $75.000',                          '2026-09-05 10:10:00', 1, 3),
(4,  'Trato hecho, las marco como vendidas',                       '2026-09-05 11:25:00', 1, 1),
(5,  'Tienes 2 jockeys? Quiero llevar los dos',                    '2026-09-10 16:20:00', 2, 4),
(6,  'Si, tengo stock. $30.000 cada uno',                          '2026-09-10 16:35:00', 2, 1),
(7,  'Dale, quedamos con 2',                                       '2026-09-10 16:50:00', 2, 4),
(8,  'Las Jordan 1 vienen con la caja original?',                  '2026-09-20 12:00:00', 3, 1),
(9,  'Si, con caja y factura de compra',                           '2026-09-20 12:30:00', 3, 2),
(10, 'Me interesa el gorro beanie',                                '2026-09-12 09:15:00', 4, 5),
(11, 'Perfecto, es tuyo',                                          '2026-09-12 09:40:00', 4, 2),
(12, 'Aun tienes la polera Stussy en talla M?',                    '2026-09-22 18:40:00', 5, 6),
(13, 'Si, sigue disponible',                                       '2026-09-22 19:00:00', 5, 3),
(14, 'Hola, el hoodie Carhartt sigue disponible?',                 '2026-09-25 11:05:00', 6, 5),
(15, 'Si, queda solo una unidad',                                  '2026-09-25 11:30:00', 6, 2);

-- ---------------------------------------------------------------------
-- CARRITO (Q7 elimina la fila usuario 1 / articulo 1)
-- ---------------------------------------------------------------------
INSERT INTO core_carrito (id_usuario, id_articulo, cantidad) VALUES
(1, 1,  1),
(1, 8,  1),
(3, 8,  1),
(4, 2,  2),
(6, 11, 1);

-- ---------------------------------------------------------------------
-- FAVORITOS
-- ---------------------------------------------------------------------
INSERT INTO core_favorito (id_usuario, id_articulo, fecha_agregado) VALUES
(1, 2,  '2026-09-18 10:00:00'),
(1, 12, '2026-09-19 21:15:00'),
(3, 8,  '2026-09-20 08:30:00'),
(4, 8,  '2026-09-21 13:45:00'),
(5, 1,  '2026-09-24 17:00:00');

-- ---------------------------------------------------------------------
-- VENTAS Y DETALLES (Q9: el vendedor 1 tiene 2 ventas, el 2 tiene 1)
-- Stocks ya reflejan las ventas: art. 6 (1 vendido -> 0),
-- art. 7 (5 originales, 2 vendidos -> 3), art. 9 (1 vendido -> 0)
-- ---------------------------------------------------------------------
INSERT INTO core_venta (id_venta, fecha_compra, id_chat) VALUES
(1, '2026-09-05 11:30:00', 1),
(2, '2026-09-10 17:00:00', 2),
(3, '2026-09-12 10:00:00', 4);

INSERT INTO core_detalle_venta (id_detalle, id_venta, cantidad_acordada, precio_unitario) VALUES
(1, 1, 1, 75000.00),
(2, 2, 2, 30000.00),
(3, 3, 1, 18000.00);

-- ---------------------------------------------------------------------
-- VALORACIONES (una por emisor y venta)
-- ---------------------------------------------------------------------
INSERT INTO core_valoracion (id_valoracion, puntuacion, comentario, fecha, id_emisor, id_receptor, id_venta) VALUES
(1, 5, 'Excelente vendedor, las zapatillas estaban tal cual las fotos', '2026-09-06 09:00:00', 3, 1, 1),
(2, 5, 'Comprador muy amable y puntual',                                '2026-09-06 10:30:00', 1, 3, 1),
(3, 4, 'Buen trato, los jockeys llegaron bien',                         '2026-09-11 12:00:00', 4, 1, 2),
(4, 5, 'Todo perfecto',                                                 '2026-09-13 15:20:00', 5, 2, 3);

-- ---------------------------------------------------------------------
-- REPORTES (Q10: 3 pendientes, 1 revisado, 1 descartado)
-- ---------------------------------------------------------------------
INSERT INTO core_reporte (id_reporte, motivo, fecha, estado, id_usuario, id_articulo) VALUES
(1, 'Precio demasiado bajo para una edicion limitada, posible estafa', '2026-09-24 10:00:00', 'Pendiente',  4, 12),
(2, 'Las fotos no coinciden con la descripcion del producto',          '2026-09-25 16:45:00', 'Pendiente',  5, 1),
(3, 'Podria tratarse de una replica no original',                      '2026-09-26 09:20:00', 'Pendiente',  6, 8),
(4, 'Publicacion duplicada',                                           '2026-09-15 11:10:00', 'Revisado',   3, 13),
(5, 'Contenido inapropiado en la descripcion',                         '2026-09-18 20:00:00', 'Descartado', 2, 11);
