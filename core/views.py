from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
from django.views.decorators.http import require_POST
from django.contrib import messages
from .models import Articulo, Usuario, Chat, Venta, Reporte, CategoriaRef, VendedorRef, FotoArticulo
from bson import ObjectId
from bson.errors import InvalidId
import base64

def catalogo(request):
    mensaje = None
    
    # =====================================================================
    # 1. OBTENER CATEGORÍAS DIRECTO CON PYMONGO
    # =====================================================================
    pipeline = [
        {"$match": {"estado_publicacion": {"$ne": "Vendido"}}},
        {"$group": {
            "_id": "$categoria.id_categoria", 
            "nombre": {"$first": "$categoria.nombre"}
        }}
    ]
    
    coleccion = Articulo._get_collection()
    categorias_crudas = list(coleccion.aggregate(pipeline))
    
    categorias = []
    for cat in categorias_crudas:
        if cat.get('_id'): 
            categorias.append({
                'id_categoria': str(cat['_id']),
                'id': str(cat['_id']), 
                'nombre': cat.get('nombre', 'Sin Nombre')
            })

    # =====================================================================
    # 2. OBTENER TODOS LOS ARTÍCULOS NO VENDIDOS
    # =====================================================================
    articulos = Articulo.objects(estado_publicacion__ne='Vendido')

    # =====================================================================
    # 3. FILTRADO EN PYTHON (porque precio es StringField)
    # =====================================================================
    if request.GET:
        categoria_id = request.GET.get('categoria')
        precio_min = request.GET.get('precio_min')
        precio_max = request.GET.get('precio_max')

        if categoria_id and precio_min and precio_max:
            try:
                precio_min_float = float(precio_min)
                precio_max_float = float(precio_max)
                
                if precio_min_float > precio_max_float:
                    mensaje = "El precio mínimo no puede ser mayor al máximo."
                else:
                    filtrados = []
                    for p in articulos:
                        if p.categoria and str(p.categoria.id_categoria) != str(categoria_id):
                            continue
                        try:
                            precio = float(p.precio) if p.precio else 0
                            if precio < precio_min_float or precio > precio_max_float:
                                continue
                        except (ValueError, TypeError):
                            continue
                        talla = request.GET.get('talla')
                        if talla and p.talla != talla:
                            continue
                        marca = request.GET.get('marca')
                        if marca and p.marca != marca:
                            continue
                        estado = request.GET.get('estado_conservacion')
                        if estado and p.estado_conservacion != estado:
                            continue
                        filtrados.append(p)
                    
                    articulos = filtrados
                    
                    if not articulos:
                        mensaje = "No encontramos artículos que coincidan con esos filtros."
                        
            except (ValueError, InvalidId):
                articulos = []
        else:
            mensaje = "Debes seleccionar una categoría y el rango de precios para filtrar."

    context = {
        'articulos': articulos,
        'categorias': categorias,
        'mensaje': mensaje
    }
    return render(request, 'core/catalogo.html', context)


def producto(request, id):
    try:
        p = Articulo.objects(id=ObjectId(id)).first()
        if not p:
            return HttpResponse("Artículo no encontrado", status=404)
        
        relacionados = Articulo.objects(
            estado_publicacion__ne='Vendido',
            id__ne=ObjectId(id)
        ).limit(4)
        
        context = {
            'p': p,
            'relacionados': relacionados
        }
        return render(request, 'core/producto.html', context)
    except InvalidId:
        return HttpResponse("ID inválido", status=400)


def carrito(request):
    usuario_actual = None
    if hasattr(request, 'session'):
        usuario_actual = request.session.get('id_usuario')
    
    user = None
    favoritos = []
    grupos = {}
    
    # Obtener artículos del usuario (para mostrar en favoritos)
    articulos_disponibles = []
    if usuario_actual:
        user = Usuario.objects(id=ObjectId(usuario_actual)).first()
        articulos_disponibles = Articulo.objects(estado_publicacion__ne='Vendido').limit(20)
    
    # Obtener IDs de favoritos del localStorage (se pasa desde el JS)
    from django.contrib.sessions.backends.signed_cookies import SessionStore
    favs_ids = request.COOKIES.get('c2c_favs', '[]')
    try:
        import json
        favoritos_ids = json.loads(favs_ids)
        favoritos = Articulo.objects(id__in=[ObjectId(fid) for fid in favoritos_ids if fid])
    except:
        favoritos = []
    
    context = {
        'grupos': grupos,
        'favoritos': favoritos,
        'favoritos_count': len(favoritos),
        'articulos_disponibles': articulos_disponibles,
        'favoritos_ids': favoritos_ids if isinstance(favoritos_ids, list) else []
    }
    return render(request, 'core/carrito.html', context)


def chat_view(request):
    usuario_actual = None
    if hasattr(request, 'session'):
        usuario_actual = request.session.get('id_usuario')
    
    chats_usuario = []
    chat_actual = None
    
    if usuario_actual:
        chats_usuario = Chat.objects(id_comprador=ObjectId(usuario_actual))
        chat_id = request.GET.get('id')
        if chat_id:
            chat_actual = Chat.objects(id=ObjectId(chat_id), id_comprador=ObjectId(usuario_actual)).first()
    
    context = {
        'chats_usuario': chats_usuario,
        'chat_actual': chat_actual,
        'usuario_actual': Usuario(id=ObjectId(usuario_actual)) if usuario_actual else None
    }
    return render(request, 'core/chat.html', context)


def chat_detalle(request, id_chat):
    usuario_actual = None
    if hasattr(request, 'session'):
        usuario_actual = request.session.get('id_usuario')
    
    try:
        chat_actual = Chat.objects(id=ObjectId(id_chat)).first()
        if not chat_actual:
            return HttpResponse("Chat no encontrado", status=404)
        
        context = {
            'chat_actual': chat_actual,
            'usuario_actual': Usuario(id=ObjectId(usuario_actual)) if usuario_actual else None
        }
        return render(request, 'core/chat.html', context)
    except InvalidId:
        return HttpResponse("ID inválido", status=400)


def perfil(request):
    usuario_actual = None
    if hasattr(request, 'session'):
        usuario_actual = request.session.get('id_usuario')
    
    if not usuario_actual:
        return redirect('/login/')
    
    user = Usuario.objects(id=ObjectId(usuario_actual)).first()
    
    # Obtener publicaciones del usuario
    publicaciones = Articulo.objects(vendedor__id_usuario=str(user.id)).order_by('-fecha_publicacion')
    
    # Obtener ventas del usuario
    ventas_recientes = []
    valoraciones_lista = []
    
    if usuario_actual:
        from .models import Venta, Valoracion
        ventas = Venta.objects(id_chat__id_vendedor__id_usuario=str(user.id)).order_by('-fecha_compra')
        
        for v in ventas:
            if v.detalles:
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
        
        valoraciones_lista = list(Valoracion.objects(id_receptor=user.id))
    
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


def publicar(request):
    usuario_actual = None
    if hasattr(request, 'session'):
        usuario_actual = request.session.get('id_usuario')
    
    if not usuario_actual:
        return redirect('/login/')
    
    # Obtener usuario actual
    user = Usuario.objects(id=ObjectId(usuario_actual)).first()
    
    if request.method == 'POST':
        # Obtener datos del formulario
        nombre = request.POST.get('nombre', '').strip()
        descripcion = request.POST.get('descripcion', '').strip()
        precio = request.POST.get('precio', '').strip()
        stock = request.POST.get('stock', '').strip()
        talla = request.POST.get('talla', '').strip()
        marca = request.POST.get('marca', '').strip()
        estado_conservacion = request.POST.get('estado_conservacion', '').strip()
        categoria_nombre = request.POST.get('categoria', '').strip()
        
        # Validaciones básicas
        if not all([nombre, descripcion, precio, stock, talla, marca, estado_conservacion, categoria_nombre]):
            error = "Todos los campos son obligatorios"
            # Re-obtener categorías para el template
            coleccion = Articulo._get_collection()
            pipeline = [{"$group": {"_id": "$categoria.nombre"}}]
            categorias = [cat['_id'] for cat in coleccion.aggregate(pipeline)]
            return render(request, 'core/publicar.html', {'categorias': categorias, 'error': error})
        
        # Procesar imágenes
        fotos = []
        archivos = request.FILES.getlist('fotos')
        for i, archivo in enumerate(archivos):
            if archivo and archivo.size > 0:
                contenido = archivo.read()
                b64 = base64.b64encode(contenido).decode('utf-8')
                mime = archivo.content_type or 'image/jpeg'
                data_url = f"data:{mime};base64,{b64}"
                foto = FotoArticulo(
                    url_imagen=data_url,
                    es_principal=(i == 0)
                )
                fotos.append(foto)
        
        # Si no hay fotos, usar placeholder
        if not fotos:
            foto = FotoArticulo(
                url_imagen="https://via.placeholder.com/400x400?text=Sin+Imagen",
                es_principal=True
            )
            fotos.append(foto)
        
        # Crear categoría reference
        categoria = CategoriaRef(
            id_categoria=str(ObjectId()),
            nombre=categoria_nombre
        )
        
        # Crear vendedor reference
        vendedor = VendedorRef(
            id_usuario=str(user.id),
            nombre_usuario=user.nombre_usuario
        )
        
        # Crear artículo
        articulo = Articulo(
            nombre=nombre,
            descripcion=descripcion,
            precio=precio,
            stock=stock,
            talla=talla,
            marca=marca,
            estado_conservacion=estado_conservacion,
            estado_publicacion='Activo',
            vendedor=vendedor,
            categoria=categoria,
            fotos=fotos
        )
        articulo.save()
        return redirect('/perfil/')
    
    # GET - mostrar formulario
    coleccion = Articulo._get_collection()
    pipeline = [{"$group": {"_id": "$categoria.nombre"}}]
    categorias = [cat['_id'] for cat in coleccion.aggregate(pipeline)]
    
    # Datos de usuario para JS
    user_data = None
    if 'id_usuario' in request.session:
        user_data = {
            'id': str(request.session.get('id_usuario')),
            'nombre_usuario': request.session.get('nombre_usuario'),
            'email': request.session.get('email')
        }
    
    context = {'categorias': categorias, 'user_data': user_data}
    return render(request, 'core/publicar.html', context)


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
        return redirect('/login/')
    return render(request, 'core/login.html')


def admin_view(request):
    usuario_actual = None
    if hasattr(request, 'session'):
        usuario_actual = request.session.get('id_usuario')
    
    if not usuario_actual:
        return redirect('/login/')
    
    user = Usuario.objects(id=ObjectId(usuario_actual)).first()
    
    if user is None or user.email != 'admin@c2c.cl':
        return HttpResponse("Acceso restringido", status=403)
    
    reportes = Reporte.objects().order_by('-fecha')
    context = {
        'reportes': reportes,
        'pendientes': Reporte.objects(estado='Pendiente').count(),
        'revisados': Reporte.objects(estado='Revisado').count(),
        'descartados': Reporte.objects(estado='Descartado').count(),
        'total': reportes.count()
    }
    return render(request, 'core/admin.html', context)


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
        articulo.delete()
        return JsonResponse({'success': True, 'message': 'Artículo eliminado correctamente'})
    except InvalidId:
        return JsonResponse({'error': 'ID inválido'}, status=400)


def logout_view(request):
    if hasattr(request, 'session') and 'id_usuario' in request.session:
        del request.session['id_usuario']
    return redirect('/')