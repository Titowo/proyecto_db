from django.contrib import admin
from .models import Usuario, Categoria, Articulo, Venta, Chat, Carrito

admin.site.register(Usuario)
admin.site.register(Categoria)
admin.site.register(Articulo)
admin.site.register(Venta)
admin.site.register(Chat)
admin.site.register(Carrito)
