from django.db import models
from django.utils import timezone

class Usuario(models.Model):
    id_usuario = models.AutoField(primary_key=True)                     #identificador unico del Usuario
    nombre1 = models.CharField(max_length=50)                           #primer nombre del Usuario
    nombre2 = models.CharField(max_length=50, blank=True, null=True)    #Segundo nombre del Usuario
    apellido1 = models.CharField(max_length=50)                         #primer apellido Usuario
    apellido2 = models.CharField(max_length=50, blank=True, null=True)  #Segund apellido Usuario
    correo = models.EmailField(max_length=100, unique=True)             #correo Usuario. debe ser unico
    contrasena = models.CharField(max_length=255)                       #contrasena Usuario
    telefono = models.CharField(max_length=20, blank=True, null=True)   #Numero de telefono Usuario
    fecha_registro = models.DateTimeField(default=timezone.now)         #fecha y hora en que registro el Usuario
    foto_perfil = models.CharField(max_length=255, blank=True, null=True)#Ruta o url de la foto de foto_perfil

    def __str__(self):
        return f"{self.nombre1} {self.apellido1}"

class Categoria(models.Model):
    id_categoria = models.AutoField(primary_key=True) # Identificador único de la categoría[cite: 1].
    nombre = models.CharField(max_length=50) # Nombre de la categoría (ej: Zapatillas, Gorros)[cite: 1].
    descripcion = models.TextField(blank=True, null=True) # Descripción opcional de la categoría[cite: 1].

    def __str__(self):
        return self.nombre

class Articulo(models.Model):
    id_articulo = models.AutoField(primary_key=True) # Identificador único del artículo[cite: 1].
    nombre = models.CharField(max_length=100) # Nombre del artículo[cite: 1].
    descripcion = models.TextField() # Descripción detallada del artículo[cite: 1].
    precio = models.DecimalField(max_digits=10, decimal_places=2) # Precio de venta del artículo[cite: 1].
    stock = models.IntegerField() # Cantidad disponible del artículo[cite: 1].
    talla = models.CharField(max_length=20) # Talla del artículo[cite: 1].
    marca = models.CharField(max_length=50) # Marca del artículo[cite: 1].
    estado_conservacion = models.CharField(max_length=20) # Estado: Nuevo o Usado[cite: 1].
    estado_publicacion = models.CharField(max_length=20) # Estado: Activo, Vendido, Pausado, etc[cite: 1].
    fecha_publicacion = models.DateTimeField(default=timezone.now) # Fecha en que se publicó el artículo[cite: 1].
    
    # Claves foráneas con regla de borrado RESTRICT según el modelo relacional[cite: 1].
    id_usuario = models.ForeignKey(Usuario, on_delete=models.RESTRICT, db_column='id_usuario') # Usuario que publica el artículo[cite: 1].
    id_categoria = models.ForeignKey(Categoria, on_delete=models.RESTRICT, db_column='id_categoria') # Categoría a la que pertenece el artículo[cite: 1].

    def __str__(self):
        return self.nombre
