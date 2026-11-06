from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
from django.views.decorators.http import require_POST, require_GET
from django.views.decorators.csrf import ensure_csrf_cookie
from django.contrib import messages
from .models import Articulo, Usuario, Chat, Venta, Reporte, CategoriaRef, VendedorRef, FotoArticulo, ItemFavorito, ItemCarrito, DetalleVenta, Valoracion
from bson import ObjectId
from bson.errors import InvalidId
from datetime import datetime
import base64
import json
from mongoengine.queryset.visitor import Q
from mongoengine.errors import DoesNotExist

def _precio_a_int(valor):
    try:
        limpio = str(valor).replace('$', '').replace('.', '').replace(',', '').strip()
        return int(float(limpio)) if limpio else 0
    except (ValueError, TypeError):
        return 0


@ensure_csrf_cookie
def catalogo(request):
    articulos = Articulo.objects(estado_publicacion__ne='Vendido')

    productos = []
    for p in articulos:
        vend = p.vendedor
        productos.append({
            'id': str(p.id),
            'brand': p.marca or '',
            'title': p.nombre or '',
            'cat': p.categoria.nombre if p.categoria and p.categoria.nombre else '',
            'size': p.talla or '',
            'cond': p.estado_conservacion or '',
            'price': _precio_a_int(p.precio),
            'stock': _precio_a_int(p.stock),
            'seller': (vend.nombre_usuario or vend.username or 'Vendedor') if vend else 'Vendedor',
            'imgs': [f.url_imagen for f in p.fotos] if p.fotos else [],
        })

    def unicos(clave):
        return sorted({x[clave] for x in productos if x[clave]})

    precio_max = max([x['price'] for x in productos] + [0])
    precio_max = ((precio_max // 5000) + 1) * 5000 if precio_max else 250000

    return render(request, 'core/catalogo.html', {
        'productos': productos,
        'categorias': unicos('cat'),
        'tallas': unicos('size'),
        'marcas': unicos('brand'),
        'estados': unicos('cond'),
        'precio_max': precio_max,
    })


@ensure_csrf_cookie
def producto(request, id):
    try:
        oid = ObjectId(id)
    except InvalidId:
        return HttpResponse("ID inválido", status=400)

    p = Articulo.objects(id=oid).first()
    if not p:
        return HttpResponse("Artículo no encontrado", status=404)

    relacionados = Articulo.objects(estado_publicacion__ne='Vendido', id__ne=oid).limit(4)

    user = _usuario_sesion(request)
    is_fav = bool(user and any(f.id_articulo == str(p.id) for f in user.favoritos))

    return render(request, 'core/producto.html',
                  {'p': p, 'is_fav': is_fav, 'relacionados': relacionados})


@ensure_csrf_cookie
def carrito(request):
    user = _usuario_sesion(request)
    cart, favs = [], []

    if user:
        cantidades = {i.id_articulo: max(1, _to_int(i.cantidad, 1)) for i in user.carrito}
        fav_ids = [f.id_articulo for f in user.favoritos]

        oids = []
        for x in set(cantidades) | set(fav_ids):
            try:
                oids.append(ObjectId(x))
            except InvalidId:
                pass
        arts = {str(a.id): a for a in Articulo.objects(id__in=oids)}

        for art_id, qty in cantidades.items():
            if art_id in arts:
                d = _art_dict(arts[art_id])
                d['qty'] = min(qty, max(1, d['stock']))
                cart.append(d)
        favs = [_art_dict(arts[i]) for i in fav_ids if i in arts]

    return render(request, 'core/carrito.html',
                  {'datos': {'logged': bool(user), 'cart': cart, 'favs': favs}})

# ==============================================================================
# CHAT
# ==============================================================================
def _money(n):
    return '$' + f"{int(n):,}".replace(',', '.')


def _cargar(ref, modelo):
    """Devuelve el documento aunque la referencia venga como DBRef."""
    if ref is None:
        return None
    if isinstance(ref, modelo):
        return ref
    try:
        return modelo.objects(id=getattr(ref, 'id', ref)).first()
    except Exception:
        return None


def _ref_id(ref):
    return str(getattr(ref, 'id', ref)) if ref else ''

def _ref(doc, campo):
    """Lee una referencia; devuelve None si el documento ya fue borrado."""
    try:
        return getattr(doc, campo)
    except DoesNotExist:
        return None


def _raw_id(doc, campo):
    """Id de la referencia sin cargarla, aunque el documento ya no exista."""
    return _ref_id(doc._data.get(campo))


def _chat_o_none(id_chat):
    try:
        return Chat.objects(id=ObjectId(str(id_chat))).first()
    except (InvalidId, TypeError):
        return None


def _es_participante(chat, uid):
    return uid in (_raw_id(chat, 'id_comprador'), _raw_id(chat, 'id_vendedor'))


def _chat_resumen(c, uid):
    art = _ref(c, 'id_articulo')
    comp = _ref(c, 'id_comprador')
    vend = _ref(c, 'id_vendedor')
    es_vendedor = _raw_id(c, 'id_vendedor') == uid
    otro = comp if es_vendedor else vend
    precio = _precio_a_int(art.precio) if art else 0
    return {
        'id': str(c.id),
        'role': 'seller' if es_vendedor else 'buyer',
        'other': (otro.nombre_usuario if otro and otro.nombre_usuario else 'Usuario eliminado'),
        'article': {
            'id': str(art.id) if art else '',
            'title': art.nombre if art else 'Artículo eliminado',
            'brand': art.marca if art else '',
            'price': precio,
            'price_fmt': _money(precio),
            'stock': _to_int(art.stock) if art else 0,
            'img': art.fotos[0].url_imagen if art and art.fotos else '',
        },
    }


def _mensajes_dict(c, uid):
    return [{
        'mine': m.id_usuario == uid,
        'text': m.contenido or '',
        'time': (m.fecha_envio or '')[11:16],
    } for m in c.mensajes]


def _render_chat(request, user, chat_actual):
    uid = str(user.id)
    lista = []
    for c in Chat.objects(Q(id_comprador=user) | Q(id_vendedor=user)).order_by('-fecha_inicio'):
        r = _chat_resumen(c, uid)
        r['active'] = bool(chat_actual and c.id == chat_actual.id)
        lista.append(r)

    chat = None
    if chat_actual:
        chat = _chat_resumen(chat_actual, uid)
        chat['mensajes'] = _mensajes_dict(chat_actual, uid)
        chat['por_valorar'] = _por_valorar(chat_actual)

    return render(request, 'core/chat.html', {'chats': lista, 'chat': chat})


@ensure_csrf_cookie
def chat_view(request):
    user = _usuario_sesion(request)
    if not user:
        return redirect('/login/')
    return _render_chat(request, user, None)


@ensure_csrf_cookie
def chat_detalle(request, id_chat):
    user = _usuario_sesion(request)
    if not user:
        return redirect('/login/')
    chat = _chat_o_none(id_chat)
    if not chat or not _es_participante(chat, str(user.id)):
        return HttpResponse("Chat no encontrado", status=404)
    return _render_chat(request, user, chat)


def iniciar_chat(request, id_articulo):
    """Busca o crea el chat entre el comprador actual y el vendedor del artículo."""
    user = _usuario_sesion(request)
    if not user:
        return redirect('/login/')

    art = _articulo_o_none(id_articulo)
    if not art:
        return HttpResponse("Artículo no encontrado", status=404)
    if not art.vendedor or not art.vendedor.id_usuario:
        return HttpResponse("Este artículo no tiene vendedor asignado", status=400)
    if str(art.vendedor.id_usuario) == str(user.id):
        return redirect('/perfil/')   # no puedes negociar contigo mismo

    try:
        vend = Usuario.objects(id=ObjectId(art.vendedor.id_usuario)).first()
    except InvalidId:
        vend = None
    if not vend:
        return HttpResponse("Vendedor no encontrado", status=404)

    chat = Chat.objects(id_comprador=user, id_articulo=art).first()
    if not chat:
        chat = Chat(fecha_inicio=datetime.now().isoformat(timespec='seconds'),
                    id_comprador=user, id_vendedor=vend, id_articulo=art,
                    mensajes=[]).save()
    return redirect('chat_detalle', id_chat=str(chat.id))


@require_POST
def api_chat_enviar(request, id_chat):
    user = _usuario_sesion(request)
    if not user:
        return _error('Debes iniciar sesión', 401)
    chat = _chat_o_none(id_chat)
    if not chat or not _es_participante(chat, str(user.id)):
        return _error('Chat no encontrado', 404)

    texto = str(_body(request).get('text', '')).strip()[:1000]
    if not texto:
        return _error('Mensaje vacío')

    ahora = datetime.now().isoformat(timespec='seconds')
    Chat._get_collection().update_one(
        {'_id': chat.id},
        {'$push': {'mensajes': {'id_usuario': str(user.id), 'contenido': texto, 'fecha_envio': ahora}}})
    return JsonResponse({'success': True, 'message': {'mine': True, 'text': texto, 'time': ahora[11:16]}})


@require_GET
def api_chat_mensajes(request, id_chat):
    user = _usuario_sesion(request)
    if not user:
        return _error('Debes iniciar sesión', 401)
    chat = _chat_o_none(id_chat)
    if not chat or not _es_participante(chat, str(user.id)):
        return _error('Chat no encontrado', 404)
    return JsonResponse({'success': True, 'mensajes': _mensajes_dict(chat, str(user.id)),
                         'por_valorar': _por_valorar(chat)})


def perfil(request):
    usuario_actual = None
    if hasattr(request, 'session'):
        usuario_actual = request.session.get('id_usuario')
    
    if not usuario_actual:
        return redirect('/login/')
    
    user = Usuario.objects(id=ObjectId(usuario_actual)).first()
    
    # Obtener publicaciones del usuario - usando colección directa de MongoDB
    articulos_coll = Articulo._get_collection()
    publicaciones_docs = articulos_coll.find({'vendedor.id_usuario': str(user.id)}).sort('fecha_publicacion', -1)
    publicaciones = []
    for doc in publicaciones_docs:
        # Mongoengine usa 'id' en lugar de '_id'
        if '_id' in doc:
            doc['id'] = doc.pop('_id')
        publicaciones.append(Articulo(**doc))
    
    # Obtener ventas del usuario - usando colección directa de MongoDB
    ventas_recientes = []
    
    if usuario_actual:
        from .models import Venta, Chat
        
        # Usar colección directamente para evitar el problema de joins
        chats_collection = Chat._get_collection()
        chats_cursor = chats_collection.find({'id_vendedor.id_usuario': str(user.id)})
        
        for chat_doc in chats_cursor:
            chat = Chat.objects(id=chat_doc['_id']).first()
            if chat:
                # Obtener ventas relacionadas a este chat
                ventas = Venta.objects(id_chat=chat.id)
                for v in ventas:
                    for detalle in v.detalles:
                        articulo = Articulo.objects(id=detalle.id_articulo).first()
                        if articulo:
                            ventas_recientes.append({
                                'producto': articulo,
                                'comprador': {'nombre_usuario': 'Cliente', 'id': str(user.id)},  # Placeholder
                                'qty': detalle.cantidad_acordada,
                                'unit': detalle.precio_unitario,
                                'fecha_compra': v.fecha_compra,
                                'estado': 'Entregada'
                            })
        
        # Valoraciones - usar collection de ventas como almacen temporal
        ventas_coll = Venta._get_collection()
        valoraciones_lista = []
        for v_doc in ventas_coll.find({'valoracion.id_receptor': str(user.id)}):
            if v_doc.get('valoracion'):
                val = v_doc['valoracion']
                valoraciones_lista.append({
                    'who': 'Cliente',
                    'stars': val.get('puntuacion', '5'),
                    'text': val.get('comentario', '')
                })
    
    context = {
        'user': user,
        'compras_count': 0,
        'favoritos_count': 0,
        'carritos_count': 0,
        'publicaciones_count': 0,
        'ventas_totales': 0,
        'ventas_total': 0,
        'unidades_stock': 0,
        'pendientes': 0,
        'revisados': 0,
        'descartados': 0,
        'total': 0,
        'publicaciones': publicaciones,
        'ventas_recientes': ventas_recientes,
        'valoraciones': valoraciones_lista
    }
    return render(request, 'core/perfil.html', context)


def _canon(valor, existentes):
    """Normaliza espacios y reutiliza el valor ya existente si solo cambia mayúsculas/minúsculas."""
    v = ' '.join(str(valor).split())[:40]
    for e in existentes:
        if e and str(e).lower() == v.lower():
            return e
    return v


def _extras_publicar():
    """Valores personalizados que ya existen en la BD, para mostrarlos en los desplegables."""
    col = Articulo._get_collection()
    def extra(valores, base):
        return sorted(str(x) for x in valores if x and x not in base)
    return {
        'cats_extra': extra(col.distinct('categoria.nombre'), {'Zapatillas', 'Polerones', 'Gorros'}),
        'tallas_extra': extra(col.distinct('talla'), {'US 8 / S', 'US 9 / M', 'US 10 / L', 'Única'}),
        'estados_extra': extra(col.distinct('estado_conservacion'), {'Nuevo', 'Usado'}),
    }


@ensure_csrf_cookie
def publicar(request):
    user = _usuario_sesion(request)
    if not user:
        return redirect('/login/')

    ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'

    def fallo(msg):
        if ajax:
            return JsonResponse({'success': False, 'error': msg}, status=400)
        return render(request, 'core/publicar.html', {'error': msg, **_extras_publicar()})

    if request.method == 'POST':
        col = Articulo._get_collection()
        P = request.POST

        nombre = P.get('nombre', '').strip()[:100]
        descripcion = P.get('descripcion', '').strip()
        precio = _to_int(P.get('precio'))
        stock = _to_int(P.get('stock'))
        marca = _canon(P.get('marca', ''), col.distinct('marca'))
        talla = _canon(P.get('talla', ''), col.distinct('talla'))
        estado = _canon(P.get('estado_conservacion', ''), col.distinct('estado_conservacion'))
        cat_nombre = _canon(P.get('categoria', ''), col.distinct('categoria.nombre'))

        if not all([nombre, descripcion, marca, talla, estado, cat_nombre]):
            return fallo('Todos los campos son obligatorios')
        if precio < 1:
            return fallo('El precio debe ser mayor a 0')
        if stock < 1:
            return fallo('El stock debe ser un entero mayor o igual a 1')

        # Fotos (la primera es la principal)
        fotos = []
        for archivo in request.FILES.getlist('imagenes')[:10]:
            mime = archivo.content_type or ''
            if archivo.size == 0 or mime not in ('image/jpeg', 'image/png', 'image/webp'):
                continue
            b64 = base64.b64encode(archivo.read()).decode('utf-8')
            fotos.append(FotoArticulo(url_imagen=f"data:{mime};base64,{b64}",
                                      es_principal=(len(fotos) == 0)))
        if not fotos:
            fotos.append(FotoArticulo(url_imagen="https://via.placeholder.com/400x400?text=Sin+Imagen",
                                      es_principal=True))

        # Reutiliza el id de la categoría si ya existe
        ej = col.find_one({'categoria.nombre': cat_nombre}, {'categoria.id_categoria': 1}) or {}
        id_cat = str((ej.get('categoria') or {}).get('id_categoria') or ObjectId())

        try:
            Articulo(
                nombre=nombre, descripcion=descripcion,
                precio=str(precio), stock=str(stock),
                talla=talla, marca=marca, estado_conservacion=estado,
                estado_publicacion='Activo',
                fecha_publicacion=datetime.now().isoformat(timespec='seconds'),
                vendedor=VendedorRef(id_usuario=str(user.id), nombre_usuario=user.nombre_usuario),
                categoria=CategoriaRef(id_categoria=id_cat, nombre=cat_nombre),
                fotos=fotos,
            ).save()
        except Exception as e:
            return fallo(f'Error al guardar: {type(e).__name__}: {e}')

        if ajax:
            return JsonResponse({'success': True, 'redirect': '/perfil/'})
        return redirect('/perfil/')

    return render(request, 'core/publicar.html', _extras_publicar())


def login_view(request):
    has_session = hasattr(request, 'session')
    if has_session and 'id_usuario' in request.session:
        return redirect('/')
    
    user_data = None
    
    if request.method == 'POST':
        email = request.POST.get('email', '').strip().lower()
        password = request.POST.get('password', '')
        
        user = Usuario.objects(email=email, contrasena=password).first()
        
        if user:
            if has_session:
                request.session['id_usuario'] = str(user.id)
                request.session['nombre_usuario'] = user.nombre_usuario
                request.session['email'] = user.email
            request.session.save()
            return redirect('/')
        else:
            error = "Correo o contraseña incorrectos"
            return render(request, 'core/login.html', {'error': error})
    
    return render(request, 'core/login.html', {'user_data': user_data})


def register_view(request):
    if request.method == 'POST':
        email = request.POST.get('email', '').strip().lower()
        nombre_usuario = request.POST.get('nombre_usuario', '').strip()
        
        # Valores del formulario para rellenar si hay error
        form_values = {
            'reg_nombre1': request.POST.get('nombre1', ''),
            'reg_nombre2': request.POST.get('nombre2', ''),
            'reg_apellido1': request.POST.get('apellido1', ''),
            'reg_apellido2': request.POST.get('apellido2', ''),
            'reg_usuario': nombre_usuario,
            'reg_email': email,
        }
        
        # Verificar si el email ya existe
        if Usuario.objects(email=email).first():
            error = "Ese correo ya está registrado"
            return render(request, 'core/login.html', {'error': error, 'show_register': True, **form_values})
        
        # Verificar si el nombre de usuario ya existe
        if Usuario.objects(nombre_usuario=nombre_usuario).first():
            error = "Ese @usuario ya está en uso"
            return render(request, 'core/login.html', {'error': error, 'show_register': True, **form_values})
        
        # Crear usuario
        usuario = Usuario(
            nombre1=request.POST.get('nombre1', ''),
            nombre2=request.POST.get('nombre2', ''),
            apellido1=request.POST.get('apellido1', ''),
            apellido2=request.POST.get('apellido2', ''),
            nombre_usuario=nombre_usuario,
            correo=email,
            email=email,
            contrasena=request.POST.get('password', ''),
            estado_cuenta='Activo'
        )
        usuario.save()
        return render(request, 'core/login.html', {'ok': 'Cuenta creada. Ya puedes iniciar sesión.'})
    return render(request, 'core/login.html')


def admin_view(request):
    user = _usuario_sesion(request)
    if not user:
        return redirect('/login/')
    if user.rol != 'admin':
        return HttpResponse("Acceso restringido", status=403)

    filas = []
    for r in Reporte.objects().order_by('-id'):
        art = _ref(r, 'id_articulo')
        den = _ref(r, 'id_usuario')
        vend = art.vendedor if art and art.vendedor else None
        filas.append({
            'id': str(r.id),
            'fecha': r.fecha or '',
            'estado': r.estado or 'Pendiente',
            'motivo': r.motivo or '',
            'art_id': str(art.id) if art else '',
            'art_nombre': f"{art.marca} {art.nombre}".strip() if art else 'Artículo eliminado',
            'vendedor': (vend.nombre_usuario or vend.username or '') if vend else '',
            'denunciante': (den.nombre_usuario if den and den.nombre_usuario else 'Anónimo'),
        })

    contar = lambda e: sum(1 for f in filas if f['estado'] == e)
    return render(request, 'core/admin.html', {
        'reportes': filas,
        'pendientes': contar('Pendiente'),
        'revisados': contar('Revisado'),
        'descartados': contar('Descartado'),
        'total': len(filas),
    })


@require_POST
def actualizar_reporte(request, id):
    user = _usuario_sesion(request)
    if not user or user.rol != 'admin':
        return HttpResponse("Acceso restringido", status=403)

    estado = request.POST.get('estado', '')
    if estado not in ('Revisado', 'Descartado'):
        return HttpResponse("Estado inválido", status=400)
    try:
        Reporte.objects(id=ObjectId(id)).update_one(set__estado=estado)
    except InvalidId:
        return HttpResponse("ID inválido", status=400)
    return redirect('admin')


def eliminar_articulo(request, id):
    """Eliminar un artículo del vendedor actual"""
    usuario_actual = None
    if hasattr(request, 'session'):
        usuario_actual = request.session.get('id_usuario')
    
    if not usuario_actual:
        return JsonResponse({'error': 'No autenticado'}, status=401)
    
    # Verificar que el artículo pertenece al usuario actual
    try:
        articulo = Articulo.objects(id=ObjectId(id)).first()
        if not articulo:
            return JsonResponse({'error': 'Artículo no encontrado'}, status=404)
        
        # Verificar que el artículo pertenece al usuario actual
        if not articulo.vendedor or str(articulo.vendedor.id_usuario) != str(usuario_actual):
            return JsonResponse({'error': 'No tienes permiso para eliminar este artículo'}, status=403)
        
        # Eliminar el artículo
        Chat._get_collection().delete_many({'id_articulo': articulo.id})
        articulo.delete()
        return JsonResponse({'success': True, 'message': 'Artículo eliminado correctamente'})
    except InvalidId:
        return JsonResponse({'error': 'ID inválido'}, status=400)


def logout_view(request):
    if hasattr(request, 'session') and 'id_usuario' in request.session:
        del request.session['id_usuario']
    return redirect('/')


@require_POST
def actualizar_perfil(request):
    """Actualizar datos de usuario"""
    from django.views.decorators.csrf import csrf_exempt
    import json
    from datetime import datetime
    
    usuario_actual = None
    if hasattr(request, 'session'):
        usuario_actual = request.session.get('id_usuario')
    
    if not usuario_actual:
        return JsonResponse({'error': 'No autenticado'}, status=401)
    
    try:
        if request.content_type == 'application/json':
            data = json.loads(request.body)
        else:
            data = request.POST
        
        user = Usuario.objects(id=ObjectId(usuario_actual)).first()
        if not user:
            return JsonResponse({'error': 'Usuario no encontrado'}, status=404)
        
        # Campos a actualizar - solo los que vienen en el request
        update_fields = {
            'nombre1': data.get('nombre1', ''),
            'nombre2': data.get('nombre2', ''),
            'apellido1': data.get('apellido1', ''),
            'apellido2': data.get('apellido2', ''),
            'nombre_usuario': data.get('nombre_usuario', ''),
            'email': data.get('email', ''),
            'ubicacion': data.get('ubicacion', ''),
            'contacto': data.get('contacto', ''),
            'punto_entrega': data.get('punto_entrega', ''),
            'biografia': data.get('biografia', ''),
        }
        
        # Solo actualizar campos que vienen como strings
        for field, value in update_fields.items():
            if value is not None and not isinstance(value, list):
                setattr(user, field, str(value) if value else '')
        
        if user.fecha_registro and not isinstance(user.fecha_registro, str):
            user.fecha_registro = str(user.fecha_registro)

        user.save()
        
        return JsonResponse({'success': True, 'message': 'Perfil actualizado'})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)


def actualizar_precio_stock(request, id):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            articulo = Articulo.objects(id=id).first()
            
            if articulo:
                articulo.precio = str(data.get('precio', articulo.precio))
                articulo.stock = str(data.get('stock', articulo.stock))
                articulo.save() # Guarda en MongoDB
                return JsonResponse({'success': True})
            else:
                return JsonResponse({'success': False, 'error': 'Artículo no encontrado'})
                
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
            
    return JsonResponse({'success': False, 'error': 'Método no permitido'})

# ==============================================================================
# CARRITO Y FAVORITOS (guardados dentro del documento Usuario)
# ==============================================================================
def _usuario_sesion(request):
    uid = request.session.get('id_usuario') if hasattr(request, 'session') else None
    if not uid:
        return None
    try:
        return Usuario.objects(id=ObjectId(uid)).first()
    except InvalidId:
        return None


def _to_int(v, default=0):
    try:
        return int(float(str(v).replace('.', '').replace(',', '').strip()))
    except (ValueError, TypeError):
        return default


def _body(request):
    try:
        return json.loads(request.body or '{}')
    except ValueError:
        return {}


def _articulo_o_none(art_id):
    try:
        return Articulo.objects(id=ObjectId(str(art_id))).first()
    except (InvalidId, TypeError):
        return None


def _respuesta(uid, **extra):
    """Devuelve los contadores actualizados desde la BD."""
    u = Usuario.objects(id=uid).first()
    total_carrito = sum(_to_int(i.cantidad) for i in u.carrito) if u else 0
    total_favs = len(u.favoritos) if u else 0
    return JsonResponse({'success': True, 'total_carrito': total_carrito,
                         'total_favs': total_favs, **extra})


def _error(msg, status=400):
    return JsonResponse({'success': False, 'error': msg}, status=status)


def _art_dict(a):
    v = a.vendedor
    return {
        'id': str(a.id),
        'brand': a.marca or '',
        'title': a.nombre or '',
        'cat': a.categoria.nombre if a.categoria and a.categoria.nombre else '',
        'size': a.talla or '',
        'cond': a.estado_conservacion or '',
        'price': _precio_a_int(a.precio),
        'stock': _precio_a_int(a.stock),
        'seller': (v.nombre_usuario or v.username or 'Vendedor') if v else 'Vendedor',
        'img': a.fotos[0].url_imagen if a.fotos else '',
    }

# ==============================================================================
# CARRITO Y FAVORITOS (guardados dentro del documento Usuario)
# ==============================================================================
def _usuario_sesion(request):
    uid = request.session.get('id_usuario') if hasattr(request, 'session') else None
    if not uid:
        return None
    try:
        return Usuario.objects(id=ObjectId(uid)).first()
    except InvalidId:
        return None


def _to_int(v, default=0):
    try:
        return int(float(str(v).replace('.', '').replace(',', '').strip()))
    except (ValueError, TypeError):
        return default


def _body(request):
    try:
        return json.loads(request.body or '{}')
    except ValueError:
        return {}


def _articulo_o_none(art_id):
    try:
        return Articulo.objects(id=ObjectId(str(art_id))).first()
    except (InvalidId, TypeError):
        return None


def _respuesta(uid, **extra):
    u = Usuario.objects(id=uid).first()
    total_carrito = sum(_to_int(i.cantidad) for i in u.carrito) if u else 0
    total_favs = len(u.favoritos) if u else 0
    return JsonResponse({'success': True, 'total_carrito': total_carrito,
                         'total_favs': total_favs, **extra})


def _error(msg, status=400):
    return JsonResponse({'success': False, 'error': msg}, status=status)


def _art_dict(a):
    v = a.vendedor
    return {
        'id': str(a.id),
        'brand': a.marca or '',
        'title': a.nombre or '',
        'cat': a.categoria.nombre if a.categoria and a.categoria.nombre else '',
        'size': a.talla or '',
        'cond': a.estado_conservacion or '',
        'price': _precio_a_int(a.precio),
        'stock': _precio_a_int(a.stock),
        'seller': (v.nombre_usuario or v.username or 'Vendedor') if v else 'Vendedor',
        'img': a.fotos[0].url_imagen if a.fotos else '',
    }


@require_GET
def api_estado(request):
    user = _usuario_sesion(request)
    if not user:
        return JsonResponse({'logged': False, 'favs': [], 'total_favs': 0, 'total_carrito': 0})
    return JsonResponse({
        'logged': True,
        'favs': [f.id_articulo for f in user.favoritos],
        'total_favs': len(user.favoritos),
        'total_carrito': sum(_to_int(i.cantidad) for i in user.carrito),
    })


@require_POST
def api_toggle_favorito(request):
    user = _usuario_sesion(request)
    if not user:
        return _error('Debes iniciar sesión', 401)

    art_id = str(_body(request).get('id', ''))
    if not _articulo_o_none(art_id):
        return _error('Artículo no encontrado', 404)

    ya_es_fav = any(f.id_articulo == art_id for f in user.favoritos)
    if ya_es_fav:
        Usuario._get_collection().update_one(
            {'_id': user.id}, {'$pull': {'favoritos': {'id_articulo': art_id}}})
    else:
        Usuario._get_collection().update_one(
            {'_id': user.id},
            {'$push': {'favoritos': {'id_articulo': art_id,
                                     'fecha_agregado': datetime.now().isoformat()}}})
    return _respuesta(user.id, is_fav=not ya_es_fav)


@require_POST
def api_add_carrito(request):
    user = _usuario_sesion(request)
    if not user:
        return _error('Debes iniciar sesión', 401)

    data = _body(request)
    art_id = str(data.get('id', ''))
    cantidad = max(1, _to_int(data.get('qty', 1), 1))

    art = _articulo_o_none(art_id)
    if not art:
        return _error('Artículo no encontrado', 404)
    if art.vendedor and str(art.vendedor.id_usuario) == str(user.id):
        return _error('No puedes comprar tu propio artículo')

    stock = _to_int(art.stock)
    if stock < 1:
        return _error('Artículo sin stock')

    col = Usuario._get_collection()
    item = next((i for i in user.carrito if i.id_articulo == art_id), None)
    if item:
        nueva = min(_to_int(item.cantidad) + cantidad, stock)
        col.update_one({'_id': user.id, 'carrito.id_articulo': art_id},
                       {'$set': {'carrito.$.cantidad': str(nueva)}})
    else:
        nueva = min(cantidad, stock)
        col.update_one({'_id': user.id},
                       {'$push': {'carrito': {'id_articulo': art_id, 'cantidad': str(nueva)}}})
    return _respuesta(user.id, qty=nueva)


@require_POST
def api_set_carrito(request):
    user = _usuario_sesion(request)
    if not user:
        return _error('Debes iniciar sesión', 401)

    data = _body(request)
    art_id = str(data.get('id', ''))
    art = _articulo_o_none(art_id)
    if not art:
        return _error('Artículo no encontrado', 404)

    qty = max(1, min(_to_int(data.get('qty', 1), 1), max(1, _to_int(art.stock))))
    Usuario._get_collection().update_one(
        {'_id': user.id, 'carrito.id_articulo': art_id},
        {'$set': {'carrito.$.cantidad': str(qty)}})
    return _respuesta(user.id, qty=qty)


@require_POST
def api_remove_carrito(request):
    user = _usuario_sesion(request)
    if not user:
        return _error('Debes iniciar sesión', 401)

    data = _body(request)
    art_id = str(data.get('id', ''))
    col = Usuario._get_collection()
    col.update_one({'_id': user.id}, {'$pull': {'carrito': {'id_articulo': art_id}}})

    if data.get('to_fav') and not any(f.id_articulo == art_id for f in user.favoritos):
        col.update_one({'_id': user.id},
                       {'$push': {'favoritos': {'id_articulo': art_id,
                                                'fecha_agregado': datetime.now().isoformat()}}})
    return _respuesta(user.id)


@require_POST
def api_clear_carrito(request):
    user = _usuario_sesion(request)
    if not user:
        return _error('Debes iniciar sesión', 401)

    ids = [str(i) for i in _body(request).get('ids', [])]
    Usuario._get_collection().update_one(
        {'_id': user.id}, {'$pull': {'carrito': {'id_articulo': {'$in': ids}}}})
    return _respuesta(user.id)


@require_POST
def marcar_venta(request, id_chat):
    user = _usuario_sesion(request)
    if not user:
        return _error('Debes iniciar sesión', 401)

    chat = _chat_o_none(id_chat)
    if not chat or not _es_participante(chat, str(user.id)):
        return _error('Chat no encontrado', 404)
    if _raw_id(chat, 'id_vendedor') != str(user.id):
        return _error('Solo el vendedor puede marcar la venta', 403)

    art = _ref(chat, 'id_articulo')
    if not art:
        return _error('El artículo ya no existe', 404)

    data = _body(request)
    qty = _to_int(data.get('qty'))
    unit = _to_int(data.get('unit'))
    if qty < 1 or unit < 1:
        return _error('Cantidad y precio deben ser mayores a 0')

    stock = _to_int(art.stock)
    if qty > stock:
        return _error(f'Stock insuficiente (disponible: {stock})')

    nuevo = stock - qty
    # Descuenta solo si el stock no cambió mientras tanto
    res = Articulo._get_collection().update_one(
        {'_id': art.id, 'stock': art.stock},
        {'$set': {'stock': str(nuevo),
                  'estado_publicacion': 'Vendido' if nuevo == 0 else art.estado_publicacion}})
    if res.matched_count == 0:
        return _error('El stock cambió, intenta de nuevo')

    Venta(
        fecha_compra=datetime.now().isoformat(timespec='seconds'),
        id_chat=chat,
        detalles=[DetalleVenta(id_articulo=str(art.id),
                               cantidad_acordada=str(qty),
                               precio_unitario=str(unit))],
    ).save()
    return JsonResponse({'success': True, 'stock': nuevo})

def _por_valorar(chat):
    return any(not v.valoracion for v in Venta.objects(id_chat=chat))


@require_POST
def api_ratings(request):
    user = _usuario_sesion(request)
    if not user:
        return _error('Debes iniciar sesión', 401)

    data = _body(request)
    chat = _chat_o_none(data.get('chatId'))
    if not chat or _raw_id(chat, 'id_comprador'):
        return _error('Solo el comprador de este chat puede valorar', 403)

    stars = _to_int(data.get('stars'))
    if not 1 <= stars <= 5:
        return _error('La puntuación debe ser de 1 a 5')
    comentario = str(data.get('comment', '')).strip()[:500]

    venta = next((v for v in Venta.objects(id_chat=chat).order_by('-id') if not v.valoracion), None)
    if not venta:
        return _error('No hay ninguna venta pendiente de valorar')

    venta.valoracion = Valoracion(
        puntuacion=str(stars), comentario=comentario,
        fecha=datetime.now().strftime('%d-%m-%Y'),
        id_emisor=str(user.id), id_receptor=_raw_id(chat, 'id_vendedor'))
    venta.save()
    return JsonResponse({'success': True})