from django.urls import path
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from . import views, views_ventas
import json

def health(request):
    return JsonResponse({'status': 'ok'})

@csrf_exempt
def api_reports(request):
    """API para reportar artículos"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            articleId = data.get('articleId')
            reason = data.get('reason', '')
            
            from .models import Reporte, Articulo, Usuario
            from bson import ObjectId
            from datetime import datetime
            
            usuario_actual = None
            if hasattr(request, 'session'):
                usuario_actual = request.session.get('id_usuario')
            
            if not usuario_actual:
                return JsonResponse({'error': 'Usuario no autenticado'}, status=401)
            
            user = Usuario.objects(id=ObjectId(usuario_actual)).first()
            articulo = Articulo.objects(id=ObjectId(articleId)).first()
            
            if not articulo:
                return JsonResponse({'error': 'Artículo no encontrado'}, status=404)
            
            reporte = Reporte(
                motivo=reason,
                fecha=datetime.now().strftime('%d-%m-%Y'),
                estado='Pendiente',
                id_usuario=user,
                id_articulo=articulo
            )
            reporte.save()
            
            return JsonResponse({'success': True, 'message': 'Reporte enviado'})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
    return JsonResponse({'error': 'Método no permitido'}, status=405)


urlpatterns = [
    path('health/', health, name='health'),
    path('', views.catalogo, name='catalogo'),
    path('producto/<str:id>/', views.producto, name='producto'),
    path('perfil/', views.perfil, name='perfil'),
    
    path('publicar/', views.publicar, name='publicar'),
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('admin/', views.admin_view, name='admin'),
    path('admin/reporte/<str:id>/', views.actualizar_reporte, name='actualizar_reporte'),
    path('logout/', views.logout_view, name='logout'),

    path('Eliminar articulo/<str:id>/', views.eliminar_articulo, name='Eliminar articulo'),
    
    path('api/reports/', api_reports, name='api_reports'),
    path('api/ratings/', views.api_ratings, name='api_ratings'),
    
    path('api/perfil/actualizar/', views.actualizar_perfil, name='actualizar_perfil'),
    path('api/articulos/actualizar/<str:id>/', views.actualizar_precio_stock, name='actualizar_precio_stock'),
    path('api/estado/', views.api_estado, name='api_estado'),

    path('carrito/', views.carrito, name='carrito'),
    path('api/favoritos/toggle/', views.api_toggle_favorito, name='api_toggle_favorito'),
    path('api/carrito/add/', views.api_add_carrito, name='api_add_carrito'),
    path('api/carrito/set/', views.api_set_carrito, name='api_set_carrito'),
    path('api/carrito/remove/', views.api_remove_carrito, name='api_remove_carrito'),
    path('api/carrito/clear/', views.api_clear_carrito, name='api_clear_carrito'),

    path('chat/', views.chat_view, name='chat'),
    path('chat/nuevo/<str:id_articulo>/', views.iniciar_chat, name='chat_iniciar'),
    path('chat/<str:id_chat>/', views.chat_detalle, name='chat_detalle'),
    path('api/chat/<str:id_chat>/enviar', views.api_chat_enviar, name='api_chat_enviar'),
    path('api/chat/<str:id_chat>/mensajes', views.api_chat_mensajes, name='api_chat_mensajes'),
    path('api/chat/<str:id_chat>/marcar-venta', views.marcar_venta, name='marcar_venta'),
]