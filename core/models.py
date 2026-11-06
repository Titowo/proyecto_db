from mongoengine import Document, EmbeddedDocument, fields, ReferenceField, IntField
import datetime

# ==============================================================================
# REFERENCIAS EXTENDIDAS (Para igualar tu JSON y evitar $lookup)
# ==============================================================================
class CategoriaRef(EmbeddedDocument):
    meta = {'strict': False}
    id_categoria = fields.StringField()
    nombre = fields.StringField()

class VendedorRef(EmbeddedDocument):
    meta = {'strict': False}
    id_usuario = fields.StringField()
    nombre_usuario = fields.StringField()
    username = fields.StringField()
    nombre1 = fields.StringField()
    apellido1 = fields.StringField()
    apellido2 = fields.StringField()
    nombre2 = fields.StringField()
    email = fields.StringField()
    telefono = fields.StringField()
    ubicacion = fields.StringField()
    reputacion = fields.StringField()  # Cambiado de FloatField a StringField
    numero_ventas = fields.StringField()  # Cambiado de IntField a StringField
    punto_entrega = fields.StringField()
    contacto = fields.StringField()
    biografia = fields.StringField()

# ==============================================================================
# SUBDOCUMENTOS EMBEBIDOS
# ==============================================================================
class FotoArticulo(EmbeddedDocument):
    meta = {'strict': False}
    url_imagen = fields.StringField(required=True)
    es_principal = fields.BooleanField(default=False)

class ItemCarrito(EmbeddedDocument):
    id_articulo = fields.StringField()
    cantidad = fields.StringField()

class ItemFavorito(EmbeddedDocument):
    id_articulo = fields.StringField()
    fecha_agregado = fields.StringField()

class Mensaje(EmbeddedDocument):
    id_usuario = fields.StringField()
    contenido = fields.StringField()
    fecha_envio = fields.StringField()

class DetalleVenta(EmbeddedDocument):
    id_articulo = fields.StringField()
    cantidad_acordada = fields.StringField()
    precio_unitario = fields.StringField()

class Valoracion(EmbeddedDocument):
    puntuacion = fields.StringField()
    comentario = fields.StringField()
    fecha = fields.StringField()
    id_emisor = fields.StringField()
    id_receptor = fields.StringField()

# ==============================================================================
# COLECCIONES RAÍZ
# ==============================================================================
class Usuario(Document):
    meta = {'collection': 'usuarios', 'strict': False}
    
    nombre1 = fields.StringField(default='')
    nombre2 = fields.StringField(default='')
    apellido1 = fields.StringField(default='')
    apellido2 = fields.StringField(default='')
    nombre_usuario = fields.StringField(default='@usuario')
    correo = fields.StringField(default='')
    email = fields.StringField(default='')
    contrasena = fields.StringField(default='')
    password_hash = fields.StringField(default='')
    telefono = fields.StringField(default='')
    estado_cuenta = fields.StringField(default='Activo')
    fecha_registro = fields.StringField()
    rol = fields.StringField(default='usuario')
    # Campos adicionales para perfil
    ubicacion = fields.StringField(default='')
    contacto = fields.StringField(default='Solo chat de la plataforma')
    punto_entrega = fields.StringField(default='')
    biografia = fields.StringField(default='')
    
    carrito = fields.EmbeddedDocumentListField(ItemCarrito)
    favoritos = fields.EmbeddedDocumentListField(ItemFavorito)

class Articulo(Document):
    meta = {'collection': 'articulos', 'strict': False}
    
    nombre = fields.StringField(default='')
    descripcion = fields.StringField(default='')
    precio = fields.StringField(default='0')
    stock = fields.StringField(default='0')
    talla = fields.StringField(default='')
    marca = fields.StringField(default='')
    estado_conservacion = fields.StringField(default='')
    estado_publicacion = fields.StringField(default='Activo')
    fecha_publicacion = fields.StringField()
    
    vendedor = fields.EmbeddedDocumentField(VendedorRef)
    categoria = fields.EmbeddedDocumentField(CategoriaRef)
    
    fotos = fields.EmbeddedDocumentListField(FotoArticulo)

class Chat(Document):
    meta = {'collection': 'chats', 'strict': False}
    
    fecha_inicio = fields.StringField()
    id_comprador = fields.ReferenceField(Usuario)
    id_vendedor = fields.ReferenceField(Usuario)
    id_articulo = fields.ReferenceField(Articulo)
    mensajes = fields.EmbeddedDocumentListField(Mensaje)

class Venta(Document):
    meta = {'collection': 'ventas', 'strict': False}
    
    fecha_compra = fields.StringField()
    id_chat = fields.ReferenceField(Chat)
    detalles = fields.EmbeddedDocumentListField(DetalleVenta)
    valoracion = fields.EmbeddedDocumentField(Valoracion)

class Reporte(Document):
    meta = {'collection': 'reportes', 'strict': False}
    
    motivo = fields.StringField()
    fecha = fields.StringField()
    estado = fields.StringField(default='Pendiente')
    id_usuario = fields.ReferenceField(Usuario)
    id_articulo = fields.ReferenceField(Articulo)