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

@csrf_exempt  
def api_ratings(request):
    """API para calificar vendedores"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            productId = data.get('productId')
            stars = data.get('stars', 5)
            comment = data.get('comment', '')
            
            from .models import Venta, Articulo, Usuario, Valoracion
            from bson import ObjectId
            from datetime import datetime
            
            usuario_actual = None
            if hasattr(request, 'session'):
                usuario_actual = request.session.get('id_usuario')
            
            if not usuario_actual:
                return JsonResponse({'error': 'Usuario no autenticado'}, status=401)
            
            user = Usuario.objects(id=ObjectId(usuario_actual)).first()
            articulo = Articulo.objects(id=ObjectId(productId)).first()
            
            if not articulo:
                return JsonResponse({'error': 'Artículo no encontrado'}, status=404)
            
            # Crear valoracion
            valoracion = Valoracion(
                puntuacion=stars,
                comentario=comment,
                fecha=datetime.now().strftime('%d-%m-%Y'),
                id_emisor=user,
                id_receptor=articulo.vendedor
            )
            
            # Guardar en MongoDB (usando colección de ventas como proxy)
            collection = Venta._get_collection()
            collection.insert_one({
                'tipo': 'valoracion',
                'puntuacion': stars,
                'comentario': comment,
                'fecha': datetime.now().strftime('%d-%m-%Y'),
                'id_emisor': str(user.id),
                'id_receptor': str(articulo.vendedor.id_usuario)
            })
            
            return JsonResponse({'success': True, 'message': 'Valoración enviada'})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
    return JsonResponse({'error': 'Método no permitido'}, status=405)

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
    path('api/reports/', api_reports, name='api_reports'),
    path('api/ratings/', api_ratings, name='api_ratings'),
]