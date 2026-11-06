from .models import Articulo, Venta, DetalleVenta, Usuario
from bson import ObjectId
from datetime import datetime

class StockInsuficiente(Exception):
    pass

def marcar_venta_concretada(chat, cantidad_acordada, precio_unitario=None):
    articulo = chat.id_articulo
    
    # Convertir stock a entero si es string
    stock_actual = int(articulo.stock) if articulo.stock else 0
    if stock_actual < cantidad_acordada:
        raise StockInsuficiente(
            f"Stock disponible: {stock_actual}, cantidad acordada: {cantidad_acordada}"
        )

    articulo.stock = str(stock_actual - cantidad_acordada)
    if articulo.stock == '0':
        articulo.estado_publicacion = 'Vendido'
    articulo.save() 

    # Usar precio unitario acordado o el del artículo
    precio = precio_unitario if precio_unitario else articulo.precio
    
    venta = Venta(
        fecha_compra=datetime.now().strftime('%d-%m-%Y'),
        id_chat=chat,
        detalles=[
            DetalleVenta(
                id_articulo=articulo.id,
                cantidad_acordada=cantidad_acordada,
                precio_unitario=precio
            )
        ]
    )
    
    # Agregar valoración default
    from .models import Valoracion
    venta.valoracion = Valoracion(
        puntuacion='5',
        comentario='',
        fecha=datetime.now().strftime('%d-%m-%Y'),
        id_emisor=chat.id_comprador.id,
        id_receptor=chat.id_vendedor.id_usuario
    )
    
    venta.save() 

    Usuario.objects(id=chat.id_comprador.id).update(
        pull__carrito__id_articulo=articulo.id
    )

    return venta, articulo