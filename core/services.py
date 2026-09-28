from django.db import transaction
from .models import Articulo, Venta, Detalle_Venta, Carrito


class StockInsuficiente(Exception):
    # se lanza cuando la cantidad acordada supera el stock disponible
    pass


def marcar_venta_concretada(chat, cantidad_acordada):
    # todo el proceso ocurre en una sola transaccion (RNF3): si algo falla
    # o el stock es insuficiente, se revierte todo y no queda nada a medias
    with transaction.atomic():
        # bloquea la fila del articulo hasta el commit (SELECT ... FOR UPDATE)
        # para que dos ventas simultaneas no descuenten el mismo stock
        articulo = Articulo.objects.select_for_update().get(pk=chat.id_articulo_id)

        # CA1: validar stock antes de modificar cualquier cosa
        if articulo.stock < cantidad_acordada:
            raise StockInsuficiente(
                f"Stock disponible: {articulo.stock}, cantidad acordada: {cantidad_acordada}"
            )

        # descontar stock, y si se agota marcar el articulo como vendido
        articulo.stock -= cantidad_acordada
        if articulo.stock == 0:
            articulo.estado_publicacion = 'Vendido'
        articulo.save(update_fields=['stock', 'estado_publicacion'])

        # registrar la venta asociada al chat y su detalle
        venta = Venta.objects.create(id_chat=chat)
        Detalle_Venta.objects.create(
            id_venta=venta,
            cantidad_acordada=cantidad_acordada,
            precio_unitario=articulo.precio,
        )

        # CA3: depuracion selectiva, solo el carrito del comprador de este chat
        Carrito.objects.filter(
            id_usuario=chat.id_comprador_id,
            id_articulo=articulo,
        ).delete()

    return venta
