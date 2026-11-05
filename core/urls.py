from django.urls import path
from django.http import JsonResponse
from . import views, views_ventas

def health(request):
    return JsonResponse({'status': 'ok'})

urlpatterns = [
    path('health/', health, name='health'),
    path('', views.catalogo, name='catalogo'),
    path('producto/<str:id>/', views.producto, name='producto'),
    path('carrito/', views.carrito, name='carrito'),
    path('chat/', views.chat_view, name='chat'),
    path('chat/<str:id_chat>/', views.chat_detalle, name='chat_detalle'),
    path('perfil/', views.perfil, name='perfil'),
    path('publicar/', views.publicar, name='publicar'),
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('admin/', views.admin_view, name='admin'),
    path('logout/', views.logout_view, name='logout'),
    path('Eliminar articulo/<str:id>/', views.eliminar_articulo, name='Eliminar articulo'),
    path('api/chat/<str:id_chat>/marcar-venta', views_ventas.marcar_venta, name='marcar_venta'),
]