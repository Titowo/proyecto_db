# core/models.py
from mongoengine import Document, EmbeddedDocument, fields
import datetime

# =====================================================================
# REFERENCIAS EXTENDIDAS (Snapshot/Subset Pattern para MongoDB)
# =====================================================================
class CategoriaRef(EmbeddedDocument):
    id_categoria = fields.ObjectIdField(required=True)
    nombre = fields.StringField(required=True)

class UsuarioRef(EmbeddedDocument):
    id_usuario = fields.ObjectIdField(required=True)
    username = fields.StringField(required=True)
    nombre1 = fields.StringField()
    apellido1 = fields.StringField()
    reputacion = fields.DecimalField(precision=1)

class ArticuloResumenRef(EmbeddedDocument):
    nombre = fields.StringField(required=True)
    precio_publicado = fields.DecimalField(precision=2)
    url_portada = fields.StringField()

# =====================================================================
# ESTRUCTURAS DE DATOS DERIVADOS (Computed Pattern)
# =====================================================================
class MetricasReputacion(EmbeddedDocument):
    promedio = fields.DecimalField(precision=1, null=True)
    cantidad = fields.IntField(default=0)

class ReputacionGlobal(EmbeddedDocument):
    como_vendedor = fields.EmbeddedDocumentField(MetricasReputacion)
    como_comprador = fields.EmbeddedDocumentField(MetricasReputacion)

# =====================================================================
# SUBDOCUMENTOS EMBEBIDOS
# =====================================================================
class FotoArticulo(EmbeddedDocument):
    id_foto = fields.IntField()
    url_imagen = fields.StringField(required=True)
    es_principal = fields.BooleanField(default=False)

class ItemCarrito(EmbeddedDocument):
    id_articulo = fields.ObjectIdField(required=True)
    cantidad = fields.IntField(min_value=1, default=1)

class ItemFavorito(EmbeddedDocument):
    id_articulo = fields.ObjectIdField(required=True)
    fecha_agregado = fields.DateTimeField(default=datetime.datetime.utcnow)

class Mensaje(EmbeddedDocument):
    id_mensaje = fields.IntField()
    id_usuario = fields.ObjectIdField(required=True)
    contenido = fields.StringField(required=True)
    fecha_envio = fields.DateTimeField(default=datetime.datetime.utcnow)

class DetalleVenta(EmbeddedDocument):
    id_detalle = fields.IntField()
    id_articulo = fields.ObjectIdField(required=True)
    nombre = fields.StringField()
    talla = fields.StringField()
    cantidad_acordada = fields.IntField(min_value=1)
    precio_unitario = fields.DecimalField(precision=2)

class Valoracion(EmbeddedDocument):
    id_valoracion = fields.IntField()
    id_emisor = fields.ObjectIdField(required=True)
    id_receptor = fields.ObjectIdField(required=True)
    puntuacion = fields.IntField(min_value=1, max_value=5)
    comentario = fields.StringField()
    fecha = fields.DateTimeField(default=datetime.datetime.utcnow)

# =====================================================================
# COLECCIONES RAÍZ
# =====================================================================
class Categoria(Document):
    nombre = fields.StringField(max_length=50, required=True)
    descripcion = fields.StringField()
    meta = {'collection': 'categorias'}

class Usuario(Document):
    username = fields.StringField(max_length=30, required=True, unique=True)
    nombre1 = fields.StringField(max_length=50, required=True)
    nombre2 = fields.StringField(max_length=50)
    apellido1 = fields.StringField(max_length=50, required=True)
    apellido2 = fields.StringField(max_length=50)
    correo = fields.EmailField(max_length=100, required=True, unique=True)
    contrasena = fields.StringField(max_length=255, required=True)
    telefono = fields.StringField(max_length=20)
    bio = fields.StringField()
    ubicacion = fields.StringField(max_length=100)
    rol = fields.StringField(max_length=20, default='usuario')
    fecha_registro = fields.DateTimeField(default=datetime.datetime.utcnow)
    foto_perfil = fields.StringField(max_length=255)
    
    # Datos derivados / Computed Pattern
    reputacion = fields.EmbeddedDocumentField(ReputacionGlobal)
    numero_ventas = fields.IntField(default=0)
    numero_compras = fields.IntField(default=0)
    
    carrito = fields.EmbeddedDocumentListField(ItemCarrito)
    favoritos = fields.EmbeddedDocumentListField(ItemFavorito)
    meta = {
        'collection': 'usuarios',
        'indexes': ['correo', 'username']
    }

class Articulo(Document):
    nombre = fields.StringField(max_length=100, required=True)
    descripcion = fields.StringField(required=True)
    precio = fields.DecimalField(precision=2, min_value=0)
    stock = fields.IntField(min_value=0)
    talla = fields.StringField(max_length=20)
    marca = fields.StringField(max_length=50)
    estado_conservacion = fields.StringField(max_length=20)
    estado_publicacion = fields.StringField(max_length=20, default='Disponible')
    fecha_publicacion = fields.DateTimeField(default=datetime.datetime.utcnow)
    
    categoria = fields.EmbeddedDocumentField(CategoriaRef) 
    vendedor = fields.EmbeddedDocumentField(UsuarioRef)
    fotos = fields.EmbeddedDocumentListField(FotoArticulo)
    
    meta = {
        'collection': 'articulos',
        'indexes': [
            ('categoria.id_categoria', 'precio', 'estado_publicacion')
        ]
    }

class Chat(Document):
    fecha_inicio = fields.DateTimeField(default=datetime.datetime.utcnow)
    estado = fields.StringField(max_length=20, default='Negociando')
    oferta_actual = fields.DecimalField(precision=2, null=True)
    
    id_articulo = fields.ObjectIdField(required=True)
    articulo_resumen = fields.EmbeddedDocumentField(ArticuloResumenRef)
    
    comprador = fields.EmbeddedDocumentField(UsuarioRef)
    vendedor = fields.EmbeddedDocumentField(UsuarioRef)
    
    total_mensajes = fields.IntField(default=0)
    mensajes = fields.EmbeddedDocumentListField(Mensaje)
    
    meta = {
        'collection': 'chats',
        'indexes': [('comprador.id_usuario', 'vendedor.id_usuario')]
    }

class MensajeArchivo(Document):
    id_chat = fields.ObjectIdField(required=True)
    id_mensaje = fields.IntField(required=True)
    id_usuario = fields.ObjectIdField(required=True)
    contenido = fields.StringField(required=True)
    fecha_envio = fields.DateTimeField(default=datetime.datetime.utcnow)
    
    meta = {
        'collection': 'mensajes_archivo',
        'indexes': [('id_chat', '-id_mensaje')]
    }

class Venta(Document):
    id_chat = fields.ObjectIdField(required=True)
    fecha_compra = fields.DateTimeField(default=datetime.datetime.utcnow)
    estado_venta = fields.StringField(max_length=20, default='En coordinacion')
    total_acordado = fields.DecimalField(precision=2, required=True)
    
    comprador = fields.EmbeddedDocumentField(UsuarioRef)
    vendedor = fields.EmbeddedDocumentField(UsuarioRef)
    
    items = fields.EmbeddedDocumentListField(DetalleVenta)
    valoraciones = fields.EmbeddedDocumentListField(Valoracion)
    
    meta = {
        'collection': 'ventas',
        'indexes': [
            ('vendedor.id_usuario', '-fecha_compra'),
            ('comprador.id_usuario', '-fecha_compra'),
            'fecha_compra'
        ]
    }

class Reporte(Document):
    id_articulo = fields.ObjectIdField(required=True)
    id_usuario = fields.ObjectIdField(required=True)
    motivo = fields.StringField(required=True)
    fecha = fields.DateTimeField(default=datetime.datetime.utcnow)
    estado = fields.StringField(max_length=20, default='Pendiente')
    
    meta = {
        'collection': 'reportes',
        'indexes': [('estado', 'fecha')]
    }
