from mongoengine import Document, EmbeddedDocument, fields
import datetime

# =====================================================================
# REFERENCIAS EXTENDIDAS (Para igualar tu JSON y evitar $lookup)
# =====================================================================
class CategoriaRef(EmbeddedDocument):
    id_categoria = fields.ObjectIdField(required=True)
    nombre = fields.StringField(required=True)

class VendedorRef(EmbeddedDocument):
    id_usuario = fields.ObjectIdField(required=True)
    nombre_usuario = fields.StringField(required=True)

# =====================================================================
# SUBDOCUMENTOS EMBEBIDOS
# =====================================================================
class FotoArticulo(EmbeddedDocument):
    meta = {'strict': False}
    url_imagen = fields.StringField(required=True)
    es_principal = fields.BooleanField(default=False)

class ItemCarrito(EmbeddedDocument):
    id_articulo = fields.ObjectIdField(required=True)
    cantidad = fields.IntField(min_value=1, default=1)

class ItemFavorito(EmbeddedDocument):
    id_articulo = fields.ObjectIdField(required=True)
    fecha_agregado = fields.DateTimeField(default=datetime.datetime.utcnow)

class Mensaje(EmbeddedDocument):
    id_usuario = fields.ObjectIdField(required=True)
    contenido = fields.StringField(required=True)
    fecha_envio = fields.DateTimeField(default=datetime.datetime.utcnow)

class DetalleVenta(EmbeddedDocument):
    id_articulo = fields.ObjectIdField(required=True)
    cantidad_acordada = fields.IntField(min_value=1)
    precio_unitario = fields.DecimalField(precision=2)

class Valoracion(EmbeddedDocument):
    puntuacion = fields.IntField(min_value=1, max_value=5)
    comentario = fields.StringField()
    fecha = fields.DateTimeField(default=datetime.datetime.utcnow)
    id_emisor = fields.ObjectIdField()
    id_receptor = fields.ObjectIdField()

# =====================================================================
# COLECCIONES RAÍZ
# =====================================================================
class Usuario(Document):
    nombre1 = fields.StringField(max_length=50)
    apellido1 = fields.StringField(max_length=50)
    nombre_usuario = fields.StringField(max_length=50) 
    correo = fields.EmailField()
    email = fields.EmailField() 
    contrasena = fields.StringField()
    password_hash = fields.StringField() 
    telefono = fields.StringField(max_length=20)
    estado_cuenta = fields.StringField() 
    fecha_registro = fields.DateTimeField(default=datetime.datetime.utcnow)
    
    carrito = fields.EmbeddedDocumentListField(ItemCarrito)
    favoritos = fields.EmbeddedDocumentListField(ItemFavorito)
    meta = {'collection': 'usuarios'}

class Articulo(Document):
    nombre = fields.StringField(max_length=100, required=True)
    descripcion = fields.StringField(required=True)
    precio = fields.DecimalField(precision=2, min_value=0)
    stock = fields.IntField(min_value=0)
    talla = fields.StringField(max_length=20)
    marca = fields.StringField(max_length=50)
    estado_conservacion = fields.StringField(max_length=20)
    estado_publicacion = fields.StringField(max_length=20, default='Activo')
    fecha_publicacion = fields.DateTimeField(default=datetime.datetime.utcnow)
    
    # Referencias extendidas para leerse en la misma consulta
    vendedor = fields.EmbeddedDocumentField(VendedorRef)
    categoria = fields.EmbeddedDocumentField(CategoriaRef) 
    
    fotos = fields.EmbeddedDocumentListField(FotoArticulo)
    meta = {'collection': 'articulos'}

class Chat(Document):
    fecha_inicio = fields.DateTimeField(default=datetime.datetime.utcnow)
    id_comprador = fields.ReferenceField(Usuario)
    id_vendedor = fields.ReferenceField(Usuario)
    id_articulo = fields.ReferenceField(Articulo)
    mensajes = fields.EmbeddedDocumentListField(Mensaje)
    meta = {'collection': 'chats'}

class Venta(Document):
    fecha_compra = fields.DateTimeField(default=datetime.datetime.utcnow)
    id_chat = fields.ReferenceField(Chat)
    detalles = fields.EmbeddedDocumentListField(DetalleVenta)
    valoracion = fields.EmbeddedDocumentField(Valoracion)
    meta = {'collection': 'ventas'}

class Reporte(Document):
    motivo = fields.StringField(required=True)
    fecha = fields.DateTimeField(default=datetime.datetime.utcnow)
    estado = fields.StringField(default='Pendiente')
    id_usuario = fields.ReferenceField(Usuario)
    id_articulo = fields.ReferenceField(Articulo)
    meta = {'collection': 'reportes'}
