from .models import Articulo, Venta, DetalleVenta, Usuario
from bson import ObjectId

class StockInsuficiente(Exception):
    pass

def marcar_venta_concretada(chat, cantidad_acordada):
    articulo = chat.id_articulo

    if articulo.stock < cantidad_acordada:
        raise StockInsuficiente(
            f"Stock disponible: {articulo.stock}, cantidad acordada: {cantidad_acordada}"
        )

    articulo.stock -= cantidad_acordada
    if articulo.stock == 0:
        articulo.estado_publicacion = 'Vendido'
    articulo.save() 

    venta = Venta(id_chat=chat)
    detalle = DetalleVenta(
        id_articulo=articulo.id,
        cantidad_acordada=cantidad_acordada,
        precio_unitario=articulo.precio
    )
    venta.detalles.append(detalle)
    venta.save() 

    Usuario.objects(id=chat.id_comprador.id).update(
        pull__carrito__id_articulo=articulo.id
    )

    return venta
