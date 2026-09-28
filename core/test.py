from decimal import Decimal
from unittest.mock import patch

from django.test import TestCase, Client
from django.urls import reverse

from .models import Usuario, Categoria, Articulo, Chat, Carrito, Venta, Detalle_Venta
from .services import marcar_venta_concretada, StockInsuficiente


def crear_usuario(correo):
    return Usuario.objects.create(
        nombre1='Test', apellido1='Prueba', correo=correo, contrasena='clave123'
    )


def crear_articulo(vendedor, categoria, **kwargs):
    datos = dict(
        nombre='Articulo', descripcion='Descripcion', precio=Decimal('50000'),
        stock=5, talla='42', marca='Nike', estado_conservacion='Nuevo',
        id_usuario=vendedor, id_categoria=categoria,
    )
    datos.update(kwargs)
    return Articulo.objects.create(**datos)


# ---------------------------------------------------------------------------
# CU-01: Busqueda y Filtrado de Catalogo (RF5, CA1, CA2)
# ---------------------------------------------------------------------------
class CatalogoTests(TestCase):

    def setUp(self):
        vendedor = crear_usuario('vendedor@test.cl')
        self.zapatillas = Categoria.objects.create(nombre='Zapatillas')
        self.gorros = Categoria.objects.create(nombre='Gorros')

        crear_articulo(vendedor, self.zapatillas, nombre='A1', precio=Decimal('50000'),
                       talla='42', marca='Nike', estado_conservacion='Nuevo')
        crear_articulo(vendedor, self.zapatillas, nombre='A2', precio=Decimal('80000'),
                       talla='40', marca='Adidas', estado_conservacion='Usado')
        crear_articulo(vendedor, self.zapatillas, nombre='A3', precio=Decimal('150000'),
                       talla='42', marca='Nike', estado_conservacion='Usado')
        crear_articulo(vendedor, self.gorros, nombre='A4', precio=Decimal('20000'))
        crear_articulo(vendedor, self.zapatillas, nombre='A5', precio=Decimal('60000'),
                       estado_publicacion='Vendido')

    def buscar(self, **params):
        return self.client.get(reverse('catalogo'), params)

    def nombres(self, response):
        return {a.nombre for a in response.context['articulos']}

    # --- CA1: filtros obligatorios ---
    def test_sin_filtros_no_devuelve_articulos(self):
        r = self.buscar()
        self.assertEqual(r.status_code, 200)
        self.assertEqual(self.nombres(r), set())
        self.assertIsNotNone(r.context['mensaje'])

    def test_falta_precio_maximo(self):
        r = self.buscar(categoria=self.zapatillas.id_categoria, precio_min=0)
        self.assertEqual(self.nombres(r), set())
        self.assertIsNotNone(r.context['mensaje'])

    def test_falta_categoria(self):
        r = self.buscar(precio_min=0, precio_max=100000)
        self.assertEqual(self.nombres(r), set())

    def test_precio_no_numerico_no_rompe_la_vista(self):
        r = self.buscar(categoria=self.zapatillas.id_categoria,
                        precio_min='abc', precio_max=100000)
        self.assertEqual(r.status_code, 200)
        self.assertEqual(self.nombres(r), set())
        self.assertIsNotNone(r.context['mensaje'])

    def test_categoria_no_numerica_no_rompe_la_vista(self):
        r = self.buscar(categoria='xyz', precio_min=0, precio_max=100000)
        self.assertEqual(r.status_code, 200)
        self.assertEqual(self.nombres(r), set())

    def test_rango_de_precio_invertido(self):
        r = self.buscar(categoria=self.zapatillas.id_categoria,
                        precio_min=100000, precio_max=0)
        self.assertEqual(self.nombres(r), set())
        self.assertIsNotNone(r.context['mensaje'])

    def test_filtros_obligatorios_devuelven_solo_coincidencias(self):
        r = self.buscar(categoria=self.zapatillas.id_categoria,
                        precio_min=0, precio_max=100000)
        self.assertEqual(self.nombres(r), {'A1', 'A2'})
        self.assertIsNone(r.context['mensaje'])

    def test_filtra_por_categoria(self):
        r = self.buscar(categoria=self.gorros.id_categoria,
                        precio_min=0, precio_max=100000)
        self.assertEqual(self.nombres(r), {'A4'})

    def test_rango_de_precio_incluye_los_extremos(self):
        r = self.buscar(categoria=self.zapatillas.id_categoria,
                        precio_min=50000, precio_max=50000)
        self.assertEqual(self.nombres(r), {'A1'})

    def test_no_muestra_articulos_no_disponibles(self):
        r = self.buscar(categoria=self.zapatillas.id_categoria,
                        precio_min=0, precio_max=100000)
        self.assertNotIn('A5', self.nombres(r))

    # --- CA2: filtros opcionales acumulativos ---
    def test_filtro_opcional_talla(self):
        r = self.buscar(categoria=self.zapatillas.id_categoria,
                        precio_min=0, precio_max=200000, talla='40')
        self.assertEqual(self.nombres(r), {'A2'})

    def test_filtro_opcional_marca(self):
        r = self.buscar(categoria=self.zapatillas.id_categoria,
                        precio_min=0, precio_max=200000, marca='Adidas')
        self.assertEqual(self.nombres(r), {'A2'})

    def test_filtro_opcional_estado(self):
        r = self.buscar(categoria=self.zapatillas.id_categoria,
                        precio_min=0, precio_max=200000, estado_conservacion='Nuevo')
        self.assertEqual(self.nombres(r), {'A1'})

    def test_filtros_opcionales_se_suman(self):
        base = dict(categoria=self.zapatillas.id_categoria, precio_min=0, precio_max=200000)
        r1 = self.buscar(talla='42', marca='Nike', **base)
        self.assertEqual(self.nombres(r1), {'A1', 'A3'})
        r2 = self.buscar(talla='42', marca='Nike', estado_conservacion='Nuevo', **base)
        self.assertEqual(self.nombres(r2), {'A1'})

    def test_sin_resultados_informa_al_usuario(self):
        r = self.buscar(categoria=self.gorros.id_categoria,
                        precio_min=30000, precio_max=40000)
        self.assertEqual(self.nombres(r), set())
        self.assertIsNotNone(r.context['mensaje'])


# ---------------------------------------------------------------------------
# CU-06: Marcar Venta Concretada (RF10, RNF3, CA1, CA2, CA3)
# ---------------------------------------------------------------------------
class MarcarVentaTests(TestCase):

    def setUp(self):
        self.vendedor = crear_usuario('vendedor@test.cl')
        self.comprador = crear_usuario('comprador@test.cl')
        self.tercero = crear_usuario('tercero@test.cl')
        categoria = Categoria.objects.create(nombre='Zapatillas')
        self.articulo = crear_articulo(self.vendedor, categoria, stock=5,
                                       precio=Decimal('50000'))
        self.chat = Chat.objects.create(id_comprador=self.comprador,
                                        id_vendedor=self.vendedor,
                                        id_articulo=self.articulo)
        self.carrito_comprador = Carrito.objects.create(
            id_usuario=self.comprador, id_articulo=self.articulo, cantidad=2)
        self.carrito_tercero = Carrito.objects.create(
            id_usuario=self.tercero, id_articulo=self.articulo, cantidad=1)
        self.url = reverse('marcar_venta', args=[self.chat.id_chat])
        self.iniciar_sesion(self.vendedor)

    def iniciar_sesion(self, usuario):
        sesion = self.client.session
        sesion['id_usuario'] = usuario.id_usuario
        sesion.save()

    def marcar(self, cantidad):
        return self.client.post(self.url, {'cantidad_acordada': cantidad})

    def assert_nada_cambio(self):
        self.articulo.refresh_from_db()
        self.assertEqual(self.articulo.stock, 5)
        self.assertEqual(self.articulo.estado_publicacion, 'Disponible')
        self.assertEqual(Venta.objects.count(), 0)
        self.assertEqual(Detalle_Venta.objects.count(), 0)
        self.assertTrue(Carrito.objects.filter(pk=self.carrito_comprador.pk).exists())

    # --- caso de exito ---
    def test_venta_exitosa_descuenta_stock_y_registra_venta(self):
        r = self.marcar(2)
        self.assertEqual(r.status_code, 200)

        self.articulo.refresh_from_db()
        self.assertEqual(self.articulo.stock, 3)
        self.assertEqual(self.articulo.estado_publicacion, 'Disponible')

        venta = Venta.objects.get()
        self.assertEqual(venta.id_chat, self.chat)
        self.assertEqual(r.json()['id_venta'], venta.id_venta)

        detalle = Detalle_Venta.objects.get(id_venta=venta)
        self.assertEqual(detalle.cantidad_acordada, 2)
        self.assertEqual(detalle.precio_unitario, Decimal('50000'))

    def test_vender_todo_el_stock_marca_articulo_como_vendido(self):
        r = self.marcar(5)
        self.assertEqual(r.status_code, 200)
        self.articulo.refresh_from_db()
        self.assertEqual(self.articulo.stock, 0)
        self.assertEqual(self.articulo.estado_publicacion, 'Vendido')

    # --- CA1: validacion de stock ---
    def test_stock_insuficiente_devuelve_409_y_no_cambia_nada(self):
        r = self.marcar(6)
        self.assertEqual(r.status_code, 409)
        self.assert_nada_cambio()

    # --- CA3: depuracion selectiva ---
    def test_elimina_del_carrito_solo_al_comprador_del_chat(self):
        self.marcar(2)
        self.assertFalse(Carrito.objects.filter(pk=self.carrito_comprador.pk).exists())
        self.assertTrue(Carrito.objects.filter(pk=self.carrito_tercero.pk).exists())

    # --- CA2 / RNF3: transaccionalidad ---
    def test_si_falla_a_mitad_de_proceso_no_se_aplica_ningun_cambio(self):
        with patch('core.services.Detalle_Venta') as detalle_falso:
            detalle_falso.objects.create.side_effect = RuntimeError('fallo simulado')
            with self.assertRaises(RuntimeError):
                marcar_venta_concretada(self.chat, 2)
        self.assert_nada_cambio()

    def test_servicio_lanza_stock_insuficiente(self):
        with self.assertRaises(StockInsuficiente):
            marcar_venta_concretada(self.chat, 99)
        self.assert_nada_cambio()

    # --- validaciones de entrada y permisos ---
    def test_cantidad_invalida_devuelve_400(self):
        for cantidad in ['0', '-1', 'abc', '2.5', '']:
            with self.subTest(cantidad=cantidad):
                self.assertEqual(self.marcar(cantidad).status_code, 400)
        self.assertEqual(self.client.post(self.url).status_code, 400)
        self.assert_nada_cambio()

    def test_sin_sesion_devuelve_401(self):
        r = Client().post(self.url, {'cantidad_acordada': 1})
        self.assertEqual(r.status_code, 401)
        self.assert_nada_cambio()

    def test_solo_el_vendedor_puede_marcar_la_venta(self):
        self.iniciar_sesion(self.comprador)
        self.assertEqual(self.marcar(1).status_code, 403)
        self.iniciar_sesion(self.tercero)
        self.assertEqual(self.marcar(1).status_code, 403)
        self.assert_nada_cambio()

    def test_chat_inexistente_devuelve_404(self):
        url = reverse('marcar_venta', args=[99999])
        r = self.client.post(url, {'cantidad_acordada': 1})
        self.assertEqual(r.status_code, 404)

    def test_solo_acepta_post(self):
        self.assertEqual(self.client.get(self.url).status_code, 405)
