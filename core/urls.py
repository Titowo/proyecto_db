from django.urls import path
from . import views, views_ventas

urlpatterns = [
    # Al dejar la ruta vacía '', esta será la página de inicio
    path('', views.catalogo, name='catalogo'),
    path('api/chat/<int:id_chat>/marcar-venta', views_ventas.marcar_venta, name='marcar_venta'),
]
