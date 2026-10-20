from django.http import JsonResponse
from django.views.decorators.http import require_POST
from bson import ObjectId

from .models import Chat
from .services import marcar_venta_concretada, StockInsuficiente

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

    if str(chat.id_vendedor.id) != str(id_usuario):
        return JsonResponse({'error': 'Solo el vendedor puede marcar la venta'}, status=403)

    try:
        cantidad_acordada = int(request.POST.get('cantidad_acordada'))
        if cantidad_acordada < 1:
            raise ValueError
    except (TypeError, ValueError):
        return JsonResponse({'error': 'Cantidad acordada invalida'}, status=400)

    try:
        venta = marcar_venta_concretada(chat, cantidad_acordada)
    except StockInsuficiente:
        return JsonResponse({'error': 'Stock insuficiente'}, status=409)

    return JsonResponse(
        {'mensaje': 'Venta registrada con exito', 'id_venta': str(venta.id)},
        status=200,
    )
