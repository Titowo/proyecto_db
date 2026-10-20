from decimal import Decimal
from unittest.mock import patch
from bson import ObjectId

from django.test import TestCase, Client
from django.urls import reverse

from .models import Usuario, Articulo, Chat, Venta, DetalleVenta, ItemCarrito
from .services import marcar_venta_concretada, StockInsuficiente

def crear_usuario(correo):
    return Usuario(
        nombre1='Test', apellido1='Prueba', correo=correo, contrasena='clave123'
    ).save()

def crear_articulo(vendedor, categoria_nombre, **kwargs):
    datos = dict(
        nombre='Articulo', descripcion='Descripcion', precio=Decimal('50000'),
        stock=5, talla='42', marca='Nike', estado_conservacion='Nuevo',
        id_usuario=vendedor, categoria_id=ObjectId(), categoria_nombre=categoria_nombre,
    )
    datos.update(kwargs)
    return Articulo(**datos).save()

class MarcarVentaTests(TestCase):
    def setUp(self):
        Usuario.drop_collection()
        Articulo.drop_collection()
        Chat.drop_collection()
        Venta.drop_collection()

        self.vendedor = crear_usuario('vendedor@test.cl')
        self.comprador = crear_usuario('comprador@test.cl')
        
        self.articulo = crear_articulo(self.vendedor, 'Zapatillas', stock=5, precio=Decimal('50000'))
        
        self.chat = Chat(id_comprador=self.comprador, id_vendedor=self.vendedor, id_articulo=self.articulo).save()
        
        self.comprador.carrito.append(ItemCarrito(id_articulo=self.articulo.id, cantidad=2))
        self.comprador.save()

        self.url = reverse('marcar_venta', args=[str(self.chat.id)])
        self.iniciar_sesion(self.vendedor)

    def iniciar_sesion(self, usuario):
        sesion = self.client.session
        sesion['id_usuario'] = str(usuario.id)
        sesion.save()

    def marcar(self, cantidad):
        return self.client.post(self.url, {'cantidad_acordada': cantidad})

    def test_venta_exitosa_descuenta_stock_y_registra_venta(self):
        r = self.marcar(2)
        self.assertEqual(r.status_code, 200)

        self.articulo.reload()
        self.assertEqual(self.articulo.stock, 3)

        venta = Venta.objects.first()
        self.assertEqual(venta.id_chat, self.chat)
        
        detalle = venta.detalles[0]
        self.assertEqual(detalle.cantidad_acordada, 2)
        self.assertEqual(detalle.precio_unitario, Decimal('50000'))
