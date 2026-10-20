// Seleccionamos la base de datos
use c2c_streetwear_db;

// (Opcional) Limpiar la BD para que quede exactamente con estos documentos
db.dropDatabase();

print("Insertando documentos JSON puros en MongoDB...");

// ==========================================
// 1. COLECCIÓN: usuarios
// ==========================================
db.usuarios.insertOne(
  {
    "_id": ObjectId("66fa70000000000000000001"),
    "nombre_completo": "Carlos González",
    "nombre_usuario": "carlos_streetwear",
    "email": "carlos.gonzalez@correo.cl",
    "password_hash": "$2b$12$e8YkZl2.oPqLmNxWvTyUu.K8jGhF5sR2tY7uI9oP0qLaBcDeFgHiJ",
    "telefono": "+56912345678",
    "direccion": {
      "calle": "Av. España 1680",
      "comuna": "Valparaíso",
      "region": "Valparaíso"
    },
    "fecha_registro": ISODate("2026-08-15T10:00:00Z"),
    "estado_cuenta": "Activo",
    "carrito": [
      {
        "id_articulo": ObjectId("66fa81001111111111111101"),
        "nombre": "Nike Dunk Low Panda",
        "precio_unitario": NumberDecimal("120000.00"),
        "cantidad": NumberInt(1),
        "talla": "US 10",
        "url_portada": "https://streetwear-c2c.cl/media/articulos/dunk_panda_front.jpg"
      }
    ],
    "favoritos": [
      {
        "id_articulo": ObjectId("66fa81001111111111111102"),
        "nombre": "Polerón Stüssy Basic Logo Black",
        "precio": NumberDecimal("85000.00"),
        "fecha_agregado": ISODate("2026-09-22T18:15:00Z")
      }
    ]
  }
);

// Agregamos un usuario vendedor mínimo para mantener la integridad de los ObjectId en las otras colecciones
db.usuarios.insertOne(
  {
    "_id": ObjectId("66fa70000000000000000002"),
    "nombre_usuario": "DiegoVendedor",
    "email": "diego@correo.cl",
    "estado_cuenta": "Activo"
  }
);

// ==========================================
// 2. COLECCIÓN: articulos
// ==========================================
db.articulos.insertOne(
  {
    "_id": ObjectId("66fa81001111111111111101"),
    "nombre": "Nike Dunk Low Panda",
    "descripcion": "Zapatillas de cuero originales en su caja de fábrica, completamente nuevas y sin uso.",
    "precio": NumberDecimal("120000.00"),
    "stock": NumberInt(2),
    "talla": "US 10",
    "marca": "Nike",
    "estado_conservacion": "Nuevo",
    "estado_publicacion": "Disponible",
    "fecha_publicacion": ISODate("2026-09-20T14:30:00Z"),
    "categoria": {
      "id_categoria": ObjectId("66fa80000000000000000001"),
      "nombre": "Zapatillas"
    },
    "vendedor": {
      "id_usuario": ObjectId("66fa70000000000000000002"),
      "nombre_usuario": "DiegoVendedor"
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
    "id_articulo": ObjectId("66fa81001111111111111101"),
    "articulo_resumen": {
      "nombre": "Nike Dunk Low Panda",
      "precio_publicado": NumberDecimal("120000.00"),
      "url_portada": "https://streetwear-c2c.cl/media/articulos/dunk_panda_front.jpg"
    },
    "comprador": {
      "id_usuario": ObjectId("66fa70000000000000000001"),
      "nombre_usuario": "carlos_streetwear"
    },
    "vendedor": {
      "id_usuario": ObjectId("66fa70000000000000000002"),
      "nombre_usuario": "DiegoVendedor"
    },
    "estado": "Activo",
    "fecha_creacion": ISODate("2026-09-21T11:00:00Z"),
    "mensajes": [
      {
        "id_mensaje": NumberInt(1),
        "emisor_id": ObjectId("66fa70000000000000000001"),
        "texto": "Hola Diego, ¿aceptarías $110.000 si coordinamos entrega en metro Miramar?",
        "fecha_envio": ISODate("2026-09-21T11:02:15Z"),
        "leido": true
      },
      {
        "id_mensaje": NumberInt(2),
        "emisor_id": ObjectId("66fa70000000000000000002"),
        "texto": "Hola Carlos. Sí, me sirve cerrar en $110.000. ¿Puedes mañana a las 17:00 hrs?",
        "fecha_envio": ISODate("2026-09-21T11:05:40Z"),
        "leido": true
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
    "id_chat_origen": ObjectId("66fa91001111111111111101"),
    "fecha_venta": ISODate("2026-09-22T17:30:00Z"),
    "total_acordado": NumberDecimal("110000.00"),
    "metodo_entrega": "Presencial (Metro Miramar)",
    "estado_transaccion": "Completada",
    "comprador": {
      "id_usuario": ObjectId("66fa70000000000000000001"),
      "nombre_usuario": "carlos_streetwear",
      "comuna": "Valparaíso",
      "region": "Valparaíso"
    },
    "vendedor": {
      "id_usuario": ObjectId("66fa70000000000000000002"),
      "nombre_usuario": "DiegoVendedor"
    },
    "items": [
      {
        "id_articulo": ObjectId("66fa81001111111111111101"),
        "nombre_historico": "Nike Dunk Low Panda",
        "talla": "US 10",
        "precio_unitario_pactado": NumberDecimal("110000.00"),
        "cantidad": NumberInt(1),
        "subtotal": NumberDecimal("110000.00")
      }
    ],
    "valoracion": {
      "puntuacion": NumberInt(5),
      "comentario": "Excelente vendedor, zapatillas 100% originales y entrega puntual.",
      "fecha_calificacion": ISODate("2026-09-22T19:00:00Z")
    }
  }
);

// ==========================================
// 5. COLECCIÓN: reportes
// ==========================================
db.reportes.insertOne(
  {
    "_id": ObjectId("66fab1001111111111111101"),
    "id_articulo": ObjectId("66fa81001111111111111101"),
    "id_usuario_denunciante": ObjectId("66fa70000000000000000001"),
    "motivo": "Posible réplica falsificada",
    "descripcion_denuncia": "El vendedor afirma que el par es original comprado en tienda oficial, pero la etiqueta interior y el patrón de costura corresponden a una réplica no autorizada.",
    "estado": "Pendiente",
    "fecha_reporte": ISODate("2026-09-22T20:15:00Z"),
    "resolucion": {
      "revisado_por": null,
      "fecha_resolucion": null,
      "accion_tomada": "En espera de revisión"
    }
  }
);

print("¡JSON inyectados en la base de datos con éxito!");
