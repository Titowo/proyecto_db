from django.urls import path
from . import views, api_auth, api_articulos, api_ventas

urlpatterns = [
    path('', views.catalogo, name='catalogo'),
    path('producto/<str:articulo_id>/', views.producto_detalle, name='producto'),
    path('carrito/', views.carrito, name='carrito'),
    path('chat/', views.chat, name='chat'),
    path('chat/<str:chat_id>/', views.chat, name='chat_detalle'),
    path('perfil/', views.perfil, name='perfil'),
    path('publicar/', views.publicar, name='publicar'),
    path('login/', views.login_view, name='login'),
    path('admin-reportes/', views.admin_view, name='admin'),

    path('api/v1/auth/register', api_auth.api_register, name='api_register'),
    path('api/v1/auth/login', api_auth.api_login, name='api_login'),
    path('api/v1/articulos', api_articulos.api_articulos_catalogo, name='api_articulos'),
    path('api/v1/chats/<str:id_chat>/ventas', api_ventas.api_confirmar_venta, name='api_confirmar_venta'), 
]
