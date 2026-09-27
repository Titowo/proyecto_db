from django.db import models
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator

class Usuario(models.Model):
    id_usuario = models.AutoField(primary_key=True)                     #identificador unico del Usuario
    nombre1 = models.CharField(max_length=50)                           #primer nombre del Usuario
    nombre2 = models.CharField(max_length=50, blank=True, null=True)    #Segundo nombre del Usuario
    apellido1 = models.CharField(max_length=50)                         #primer apellido Usuario
    apellido2 = models.CharField(max_length=50, blank=True, null=True)  #Segund apellido Usuario
    correo = models.EmailField(max_length=100, unique=True)             #correo Usuario debe ser unico
    contrasena = models.CharField(max_length=255)                       #contrasena Usuario
    telefono = models.CharField(max_length=20, blank=True, null=True)   #Numero de telefono Usuario
    fecha_registro = models.DateTimeField(default=timezone.now)         #fecha y hora en que registro el Usuario
    foto_perfil = models.CharField(max_length=255, blank=True, null=True)#ruta o url de la foto de foto_perfil

    def __str__(self):
        return f"{self.nombre1} {self.apellido1}"

class Categoria(models.Model):
    id_categoria = models.AutoField(primary_key=True)                   # identificador unico de la categoria
    nombre = models.CharField(max_length=50)                            # nombre de la categor ia
    descripcion = models.TextField(blank=True, null=True)               # descripcion opcional de la categoria

    def __str__(self):
        return self.nombre

class Articulo(models.Model):
    id_articulo = models.AutoField(primary_key=True)                    # identificador unico del articulo
    nombre = models.CharField(max_length=100)                           # nombre del articulo
    descripcion = models.TextField()                                    # descripcion detallada del articulo
    precio = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])       # precio de venta del articulo, no negativo segun supuestos del modelo
    stock = models.IntegerField(validators=[MinValueValidator(0)])                                       # cantidad disponible del articulo, no negativa segun supuestos del modelo
    talla = models.CharField(max_length=20)                             # talla del art iculo
    marca = models.CharField(max_length=50)                             # marca del art iculo
    estado_conservacion = models.CharField(max_length=20)               # estado: Nuevo o Usado
    estado_publicacion = models.CharField(max_length=20)                # estado: Activo, Vendido, Pausado, etc
    fecha_publicacion = models.DateTimeField(default=timezone.now)      # fecha en que se publico el articulo
    
    # Claves foraneas con regla de borrado RESTRICT segun el modelo relacional
    id_usuario = models.ForeignKey(Usuario, on_delete=models.RESTRICT, db_column='id_usuario')          # usuario que publica el articulo
    id_categoria = models.ForeignKey(Categoria, on_delete=models.RESTRICT, db_column='id_categoria')    # categoria a la que pertenece el articulo

    def __str__(self):
        return self.nombre


class Foto_Articulo(models.Model):
    id_foto = models.AutoField(primary_key=True)                        # identificador de la foto 
    id_articulo = models.ForeignKey('Articulo', on_delete=models.CASCADE, db_column='id_articulo') # articulo al que pertenece, borrado en cascada 
    url_imagen = models.CharField(max_length=255)                       # ruta o URL de la imagen 
    es_principal = models.BooleanField(default=False)                   # se inicializa en false por defecto segun los supuestos 

    class Meta:
        # Django no soporta claves primarias compuestas nativamente, por lo que usamos unique_together para emular la PK (id_articulo, id_foto) 
        unique_together = (('id_articulo', 'id_foto'),)

class Chat(models.Model):
    id_chat = models.AutoField(primary_key=True)                        # fdentificador unico del chat 
    fecha_inicio = models.DateTimeField(default=timezone.now)           # fecha y hora de inicio 
    
    # Se requieren related_names porque hay multiples referencias al modelo Usuario
    id_comprador = models.ForeignKey('Usuario', on_delete=models.RESTRICT, db_column='id_comprador', related_name='chats_como_comprador')   # borrado restringido 
    id_vendedor = models.ForeignKey('Usuario', on_delete=models.RESTRICT, db_column='id_vendedor', related_name='chats_como_vendedor')      # borrado restringido 
    id_articulo = models.ForeignKey('Articulo', on_delete=models.CASCADE, db_column='id_articulo')                                          # articulo que motiva la conversacion 

class Mensaje(models.Model):
    id_mensaje = models.AutoField(primary_key=True)                                                 # identificador unico del mensaje 
    contenido = models.TextField()                                                                  # texto del mensaje 
    fecha_envio = models.DateTimeField(default=timezone.now)                                        # fecha y hora en que se envio 
    id_chat = models.ForeignKey('Chat', on_delete=models.CASCADE, db_column='id_chat')              # chat al que pertenece, borrado en cascada 
    id_usuario = models.ForeignKey('Usuario', on_delete=models.RESTRICT, db_column='id_usuario')    # usuario que escribio el mensaje, borrado restringido 

class Carrito(models.Model):
    id_usuario = models.ForeignKey('Usuario', on_delete=models.CASCADE, db_column='id_usuario')     # usuario dueño del carrito 
    id_articulo = models.ForeignKey('Articulo', on_delete=models.CASCADE, db_column='id_articulo')  # articulo agregado 
    cantidad = models.IntegerField(validators=[MinValueValidator(1)])                               # cantidad de unidades 

    class Meta:
        unique_together = (('id_usuario', 'id_articulo'),)                                          # alave primaria compuesta segun modelo relacional 

class Favorito(models.Model):
    id_usuario = models.ForeignKey('Usuario', on_delete=models.CASCADE, db_column='id_usuario')     # usuario que marco el favorito 
    id_articulo = models.ForeignKey('Articulo', on_delete=models.CASCADE, db_column='id_articulo')  # articulo marcado 
    fecha_agregado = models.DateTimeField(default=timezone.now)                                     # fecha de agregado 

    class Meta:
        unique_together = (('id_usuario', 'id_articulo'),)                                          # clave primaria compuesta segun modelo relacional 

class Venta(models.Model):
    id_venta = models.AutoField(primary_key=True)                                                   # fdentificador unico de la venta 
    fecha_compra = models.DateTimeField(default=timezone.now)                                       # fecha en que se concreto 
    id_chat = models.ForeignKey('Chat', on_delete=models.SET_NULL, null=True, blank=True, db_column='id_chat') # chat asociado, borrado SET NULL 

class Detalle_Venta(models.Model):
    id_detalle = models.AutoField(primary_key=True)                                                 # identificador del detalle 
    id_venta = models.ForeignKey('Venta', on_delete=models.CASCADE, db_column='id_venta')           # venta a la que pertenece, borrado en cascada 
    cantidad_acordada = models.IntegerField(validators=[MinValueValidator(1)])                      # cantidad vendida, no negativa 
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])                          # precio unitario, no negativo segun supuestos del modelo

    class Meta:
        unique_together = (('id_venta', 'id_detalle'),)                                             # entidad debil con dependencia identificadora 

class Valoracion(models.Model):
    id_valoracion = models.AutoField(primary_key=True)                                              # identificador unico 
    puntuacion = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])       # acotada a un rango fijo de 1 a 5 
    comentario = models.TextField(blank=True, null=True)                                            # comentario opcional 
    fecha = models.DateTimeField(default=timezone.now)                                              # fecha de valoracion 
    id_emisor = models.ForeignKey('Usuario', on_delete=models.RESTRICT, db_column='id_emisor', related_name='valoraciones_emitidas') # borrado restringido 
    id_receptor = models.ForeignKey('Usuario', on_delete=models.RESTRICT, db_column='id_receptor', related_name='valoraciones_recibidas') # borrado restringido 
    id_venta = models.ForeignKey('Venta', on_delete=models.CASCADE, db_column='id_venta')           # Bborrado en cascada 

    class Meta:
        unique_together = (('id_venta', 'id_emisor'),)                                              # un mismo usuario no puede valorar dos veces una misma venta 

class Reporte(models.Model):
    id_reporte = models.AutoField(primary_key=True)                                                 # identificador unico 
    motivo = models.TextField()                                                                     # motivo del reporte 
    fecha = models.DateTimeField(default=timezone.now)                                              # fecha del reporte 
    estado = models.CharField(max_length=20, default='Pendiente')                                   # se inicializa en Pendiente por defecto 
    id_usuario = models.ForeignKey('Usuario', on_delete=models.CASCADE, db_column='id_usuario')     # usuario que reporta 
    id_articulo = models.ForeignKey('Articulo', on_delete=models.CASCADE, db_column='id_articulo')  # articulo reportado