from django.http import JsonResponse
from django.views.decorators.http import require_POST

from .models import Chat
from .services import marcar_venta_concretada, StockInsuficiente


@require_POST
def marcar_venta(request, id_chat):
    # el vendedor es el usuario de la sesion (la vista de login debe guardar
    # request.session['id_usuario'] al autenticar, RF2)
    id_usuario = request.session.get('id_usuario')
    if id_usuario is None:
        return JsonResponse({'error': 'Debes iniciar sesion'}, status=401)

    chat = Chat.objects.filter(pk=id_chat).first()
    if chat is None:
        return JsonResponse({'error': 'Chat no encontrado'}, status=404)

    # solo el vendedor del articulo puede marcar la venta desde este chat
    if chat.id_vendedor_id != id_usuario:
        return JsonResponse({'error': 'Solo el vendedor puede marcar la venta'}, status=403)

    # la cantidad acordada debe ser un entero mayor o igual a 1
    try:
        cantidad_acordada = int(request.POST.get('cantidad_acordada'))
        if cantidad_acordada < 1:
            raise ValueError
    except (TypeError, ValueError):
        return JsonResponse({'error': 'Cantidad acordada invalida'}, status=400)

    # comprador y articulo salen del propio chat, no del cuerpo de la solicitud
    try:
        venta = marcar_venta_concretada(chat, cantidad_acordada)
    except StockInsuficiente:
        return JsonResponse({'error': 'Stock insuficiente'}, status=409)

    return JsonResponse(
        {'mensaje': 'Venta registrada con exito', 'id_venta': venta.id_venta},
        status=200,
    )
