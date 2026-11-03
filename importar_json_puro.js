// (Opcional) Limpiar la BD para que quede exactamente con estos documentos
db.dropDatabase();

print("Insertando documentos JSON puros compatibles con la Entrega 2 en MongoDB...");

// ==========================================
// 1. COLECCIÓN: usuarios
// ==========================================
db.usuarios.insertOne(
  {
    "_id": ObjectId("66fa70000000000000000001"),
    "username": "@JuanComprador",
    "nombre1": "Juan",
    "nombre2": "Andres",
    "apellido1": "Perez",
    "apellido2": "Soto",
    "correo": "juan.perez@email.com",
    "contrasena": "$2b$12$e8YkZl2.oPqLmNxWvTyUu.K8jGhF5sR2tY7uI9oP0qLaBcDeFgHiJ",
    "telefono": "+56912345678",
    "bio": "Coleccionista de zapatillas. Compro y vendo en Santiago.",
    "ubicacion": "Santiago Centro",
    "rol": "usuario",
    "fecha_registro": ISODate("2026-08-15T10:00:00Z"),
    "foto_perfil": "https://streetwear-c2c.cl/media/perfiles/juan.jpg",
    "reputacion": {
      "como_vendedor": { "promedio": null, "cantidad": NumberInt(0) },
      "como_comprador": { "promedio": NumberDecimal("5.0"), "cantidad": NumberInt(1) }
    },
    "numero_ventas": NumberInt(0),
    "numero_compras": NumberInt(1),
    "carrito": [
      {
        "id_articulo": ObjectId("66fa81001111111111111103"),
        "cantidad": NumberInt(1)
      }
    ],
    "favoritos": [
      {
        "id_articulo": ObjectId("66fa81001111111111111101"),
        "fecha_agregado": ISODate("2026-09-19T18:15:00Z")
      }
    ]
  }
);

db.usuarios.insertOne(
  {
    "_id": ObjectId("66fa70000000000000000002"),
    "username": "@DiegoVendedor",
    "nombre1": "Diego",
    "apellido1": "Fuentes",
    "correo": "diego.fuentes@email.com",
    "contrasena": "$2b$12$Qw3rTyUi0pAsDfGhJkLzXuV1bNm4cVbNmQwErTyUi0pAsDfGhJkL",
    "bio": "Coleccionista de sneakers y streetwear. Vendo piezas originales.",
    "ubicacion": "Santiago Centro Entrega en Metro Baquedano",
    "rol": "usuario",
    "fecha_registro": ISODate("2026-07-02T09:00:00Z"),
    "reputacion": {
      "como_vendedor": { "promedio": NumberDecimal("4.9"), "cantidad": NumberInt(37) },
      "como_comprador": { "promedio": NumberDecimal("4.8"), "cantidad": NumberInt(3) }
    },
    "numero_ventas": NumberInt(37),
    "numero_compras": NumberInt(3),
    "carrito": [],
    "favoritos": []
  }
);

// ==========================================
// 2. COLECCIÓN: articulos
// ==========================================
db.articulos.insertOne(
  {
    "_id": ObjectId("66fa81001111111111111101"),
    "nombre": "Nike Dunk Low Panda",
    "descripcion": "Colorway blanco/negro en muy buen estado, usadas 3 veces. Incluye caja original y cordones de repuesto.",
    "precio": NumberDecimal("120000.00"),
    "stock": NumberInt(1),
    "talla": "US 10",
    "marca": "Nike",
    "estado_conservacion": "Usado",
    "estado_publicacion": "Disponible",
    "fecha_publicacion": ISODate("2026-09-20T14:30:00Z"),
    "categoria": {
      "id_categoria": ObjectId("66fa80000000000000000001"),
      "nombre": "Zapatillas"
    },
    "vendedor": {
      "id_usuario": ObjectId("66fa70000000000000000002"),
      "username": "@DiegoVendedor",
      "nombre1": "Diego",
      "apellido1": "Fuentes",
      "reputacion": NumberDecimal("4.9")
    },
    "fotos": [
      {
        "id_foto": NumberInt(1),
        "url_imagen": "https://streetwear-c2c.cl/media/articulos/dunk_panda_front.jpg",
        "es_principal": true
      },
      {
        "id_foto": NumberInt(2),
        "url_imagen": "https://streetwear-c2c.cl/media/articulos/dunk_panda_side.jpg",
        "es_principal": false
      }
    ]
  }
);

// ==========================================
// 3. COLECCIÓN: chats
// ==========================================
db.chats.insertOne(
  {
    "_id": ObjectId("66fa91001111111111111101"),
    "fecha_inicio": ISODate("2026-09-21T11:00:00Z"),
    "estado": "Venta confirmada",
    "oferta_actual": NumberDecimal("110000.00"),
    "id_articulo": ObjectId("66fa81001111111111111101"),
    "articulo_resumen": {
      "nombre": "Nike Dunk Low Panda",
      "precio_publicado": NumberDecimal("120000.00"),
      "url_portada": "https://streetwear-c2c.cl/media/articulos/dunk_panda_front.jpg"
    },
    "comprador": {
      "id_usuario": ObjectId("66fa70000000000000000001"),
      "username": "@JuanComprador",
      "nombre1": "Juan",
      "apellido1": "Perez"
    },
    "vendedor": {
      "id_usuario": ObjectId("66fa70000000000000000002"),
      "username": "@DiegoVendedor",
      "nombre1": "Diego",
      "apellido1": "Fuentes"
    },
    "total_mensajes": NumberInt(3),
    "mensajes": [
      {
        "id_mensaje": NumberInt(1),
        "id_usuario": ObjectId("66fa70000000000000000001"),
        "contenido": "Hola Diego, ¿aceptarías $110.000 si coordinamos entrega en metro Baquedano?",
        "fecha_envio": ISODate("2026-09-21T11:02:15Z")
      },
      {
        "id_mensaje": NumberInt(2),
        "id_usuario": ObjectId("66fa70000000000000000002"),
        "contenido": "Hola Juan. Sí, me sirve cerrar en $110.000. ¿Puedes mañana a las 17:00 hrs?",
        "fecha_envio": ISODate("2026-09-21T11:05:40Z")
      },
      {
        "id_mensaje": NumberInt(3),
        "id_usuario": ObjectId("66fa70000000000000000001"),
        "contenido": "Perfecto, nos vemos mañana a las 17:00 en Baquedano.",
        "fecha_envio": ISODate("2026-09-21T11:08:10Z")
      }
    ]
  }
);

// ==========================================
// 4. COLECCIÓN: ventas
// ==========================================
db.ventas.insertOne(
  {
    "_id": ObjectId("66faa1001111111111111101"),
    "id_chat": ObjectId("66fa91001111111111111101"),
    "fecha_compra": ISODate("2026-09-22T20:30:00Z"),
    "estado_venta": "Entregada",
    "total_acordado": NumberDecimal("110000.00"),
    "comprador": {
      "id_usuario": ObjectId("66fa70000000000000000001"),
      "username": "@JuanComprador",
      "nombre1": "Juan",
      "apellido1": "Perez"
    },
    "vendedor": {
      "id_usuario": ObjectId("66fa70000000000000000002"),
      "username": "@DiegoVendedor",
      "nombre1": "Diego",
      "apellido1": "Fuentes"
    },
    "items": [
      {
        "id_detalle": NumberInt(1),
        "id_articulo": ObjectId("66fa81001111111111111101"),
        "nombre": "Nike Dunk Low Panda",
        "talla": "US 10",
        "cantidad_acordada": NumberInt(1),
        "precio_unitario": NumberDecimal("110000.00")
      }
    ],
    "valoraciones": [
      {
        "id_valoracion": NumberInt(1),
        "id_emisor": ObjectId("66fa70000000000000000001"),
        "id_receptor": ObjectId("66fa70000000000000000002"),
        "puntuacion": NumberInt(5),
        "comentario": "Excelente vendedor, zapatillas originales y entrega puntual.",
        "fecha": ISODate("2026-09-22T22:00:00Z")
      },
      {
        "id_valoracion": NumberInt(2),
        "id_emisor": ObjectId("66fa70000000000000000002"),
        "id_receptor": ObjectId("66fa70000000000000000001"),
        "puntuacion": NumberInt(5),
        "comentario": "Comprador serio y puntual, trato rápido.",
        "fecha": ISODate("2026-09-22T22:40:00Z")
      }
    ]
  }
);

// ==========================================
// 5. COLECCIÓN: reportes
// ==========================================
db.reportes.insertOne(
  {
    "_id": ObjectId("66fab1001111111111111101"),
    "id_articulo": ObjectId("66fa81001111111111111101"),
    "id_usuario": ObjectId("66fa70000000000000000001"),
    "motivo": "Contenido sospechoso o fraude: la etiqueta interior no corresponde a un par original.",
    "fecha": ISODate("2026-09-23T15:20:00Z"),
    "estado": "Pendiente"
  }
);

print("¡Datos de la Entrega 2 inyectados en la base de datos con éxito!");
