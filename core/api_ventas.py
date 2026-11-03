import json
import datetime
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from bson import ObjectId
from bson.errors import InvalidId
from mongoengine import get_connection
from .decorators import requiere_jwt, crear_respuesta_error
from .models import Chat, Articulo, Venta, DetalleVenta, Usuario

@csrf_exempt
@requiere_jwt()
def api_confirmar_venta(request, id_chat):
    if request.method != 'POST':
        return crear_respuesta_error("METODO_NO_PERMITIDO", "Use POST", status=405)
        
    try:
        data = json.loads(request.body)
        id_articulo = data.get('id_articulo')
        cantidad_acordada = data.get('cantidad_acordada')
        precio_unitario = data.get('precio_unitario')
        
        # 1. Validación de formato y datos (HTTP 400)
        if not id_articulo or type(cantidad_acordada) != int or cantidad_acordada < 1 or precio_unitario is None:
            return crear_respuesta_error("DATOS_INVALIDOS", "cantidad_acordada debe ser un entero mayor o igual a 1.", status=400)
            
        try:
            id_chat_obj = ObjectId(id_chat)
            id_articulo_obj = ObjectId(id_articulo)
        except InvalidId:
            return crear_respuesta_error("DATOS_INVALIDOS", "Formato de ID incorrecto.")
            
        # 2. Verificar permisos del usuario y existencia del chat
        id_vendedor_req = ObjectId(request.jwt_payload.get('sub'))
        chat = Chat.objects(id=id_chat_obj).first()
        
        if not chat:
            return crear_respuesta_error("NO_ENCONTRADO", "El chat no existe.", status=404)
        if chat.id_vendedor.id != id_vendedor_req:
            return crear_respuesta_error("SIN_PERMISO", "Solo el vendedor puede confirmar la venta.", status=403)

        # 3. Iniciar Transacción Multidocumento
        cliente = get_connection()
        with cliente.start_session() as session:
            with session.start_transaction():
                articulo = Articulo.objects(id=id_articulo_obj).first()
                if not articulo:
                    raise Exception("Articulo no encontrado")
                
                # 4. Validar Stock (HTTP 409) y hacer rollback automático si falla
                if articulo.stock < cantidad_acordada:
                    return crear_respuesta_error(
                        "STOCK_INSUFICIENTE", 
                        "La cantidad acordada supera el stock disponible.", 
                        {"stock_disponible": articulo.stock, "cantidad_solicitada": cantidad_acordada}, 
                        status=409
                    )
                
                # 5. Descontar stock
                articulo.stock -= cantidad_acordada
                if articulo.stock == 0:
                    articulo.estado_publicacion = 'Vendido'
                articulo.save(session=session)
                
                # 6. Registrar Venta y Detalle
                nueva_venta = Venta(
                    id_chat=chat,
                    fecha_compra=datetime.datetime.utcnow(),
                    # Se asume que agregarás 'estado_venta' y 'total_acordado' a tu modelo Venta según el nuevo esquema
                )
                detalle = DetalleVenta(
                    id_articulo=articulo.id,
                    cantidad_acordada=cantidad_acordada,
                    precio_unitario=precio_unitario
                )
                nueva_venta.detalles.append(detalle)
                nueva_venta.save(session=session)
                
                # 7. Quitar el artículo del carrito del comprador
                comprador = chat.id_comprador
                Usuario.objects(id=comprador.id).update(
                    pull__carrito__id_articulo=articulo.id,
                    session=session
                )
                
                # 8. Actualizar el chat
                # Se asume que agregarás el campo 'estado' al modelo Chat
                Chat.objects(id=chat.id).update(set__estado='Venta confirmada', session=session)
                
                # 9. Formatear la respuesta 201 Created
                return JsonResponse({
                    "success": True,
                    "data": {
                        "id_venta": str(nueva_venta.id),
                        "estado_venta": "En coordinacion",
                        "total_acordado": float(cantidad_acordada * precio_unitario),
                        "stock_restante": articulo.stock
                    }
                }, status=201)

    except Exception as e:
        return crear_respuesta_error("ERROR_INTERNO", str(e), status=500)
