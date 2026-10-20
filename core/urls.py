from django.urls import path
from . import views, views_ventas

urlpatterns = [
    path('', views.catalogo, name='catalogo'),
    path('api/chat/<str:id_chat>/marcar-venta', views_ventas.marcar_venta, name='marcar_venta'),
]
