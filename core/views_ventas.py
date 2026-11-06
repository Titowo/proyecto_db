from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from bson import ObjectId
import json

from .models import Chat
from .services import marcar_venta_concretada, StockInsuficiente

@csrf_exempt
@require_POST
def marcar_venta(request, id_chat):
    id_usuario = request.session.get('id_usuario')
    if id_usuario is None:
        return JsonResponse({'error': 'Debes iniciar sesion'}, status=401)

    try:
        chat = Chat.objects(id=ObjectId(id_chat)).first()
    except Exception:
        return JsonResponse({'error': 'ID de chat invalido'}, status=400)

    if chat is None:
        return JsonResponse({'error': 'Chat no encontrado'}, status=404)

    if str(chat.id_vendedor.id_usuario) != str(id_usuario):
        return JsonResponse({'error': 'Solo el vendedor puede marcar la venta'}, status=403)

    # Obtener cantidad y precio del cuerpo JSON o POST
    try:
        if request.content_type == 'application/json':
            data = json.loads(request.body)
            cantidad_acordada = int(data.get('qty', 1))
            precio_unitario = data.get('unit')
        else:
            cantidad_acordada = int(request.POST.get('qty', 1))
            precio_unitario = request.POST.get('price')
        
        if cantidad_acordada < 1:
            raise ValueError
    except (TypeError, ValueError):
        return JsonResponse({'error': 'Cantidad acordada invalida'}, status=400)

    try:
        venta, articulo = marcar_venta_concretada(chat, cantidad_acordada, precio_unitario)
        return JsonResponse({'success': True, 'message': 'Venta registrada', 'stock': int(articulo.stock)}, status=200)
    except StockInsuficiente as e:
        return JsonResponse({'error': str(e)}, status=409)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)