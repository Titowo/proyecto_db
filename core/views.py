from django.shortcuts import get_object_or_404, render
from .models import Articulo, Categoria, Usuario, Chat, UsuarioRef, CategoriaRef, FotoArticulo

def catalogo(request):
    cat_id = request.GET.get('categoria')
    precio_max = request.GET.get('max', 300000)
    busqueda = request.GET.get('q', '')
    
    query = {"estado_publicacion": "Disponible"}
    if cat_id:
        query["categoria__id_categoria"] = cat_id
    if precio_max:
        query["precio__lte"] = float(precio_max)
    if busqueda:
        query["nombre__icontains"] = busqueda
        
    articulos = Articulo.objects(**query)
    categorias = Categoria.objects.all()
    
    return render(request, 'core/catalogo.html', {
        'articulos': articulos,
        'categorias': categorias
    })

def producto_detalle(request, articulo_id):
    p = Articulo.objects(id=articulo_id).first()
    if not p:
        raise Http404("El artículo no existe")
    relacionados = Articulo.objects(id__ne=p.id, vendedor__id_usuario=p.vendedor.id_usuario)[:4]
    return render(request, 'core/producto.html', {'p': p, 'relacionados': relacionados})


def chat(request, chat_id=None):
    # Si no se pasa un id de chat, tomamos el primero de la base de datos como ejemplo
    if chat_id:
        chat_actual = Chat.objects(id=chat_id).first()
    else:
        chat_actual = Chat.objects().first()
        
    # Simulamos el usuario actual logueado (ej. el primer usuario de la BD)
    usuario_actual = Usuario.objects().first()
    
    # Listado de chats donde participa el usuario actual (como comprador o vendedor)
    chats_usuario = []
    if usuario_actual:
        chats_usuario = Chat.objects(
            __raw__={
                "$or": [
                    {"comprador.id_usuario": usuario_actual.id},
                    {"vendedor.id_usuario": usuario_actual.id}
                ]
            }
        )

    return render(request, 'core/chat.html', {
        'chat_actual': chat_actual,
        'chats_usuario': chats_usuario,
        'usuario_actual': usuario_actual
    })

def perfil(request):
    return render(request, 'core/perfil.html')

def publicar(request):
    if request.method == 'POST':
        # Obtenemos los datos del formulario HTML
        nombre = request.POST.get('nombre')
        descripcion = request.POST.get('descripcion')
        precio = request.POST.get('precio')
        stock = request.POST.get('stock', 1)
        talla = request.POST.get('talla')
        marca = request.POST.get('marca')
        estado_conservacion = request.POST.get('estado_conservacion')

        categoria_id = request.POST.get('categoria')
        url_imagen = request.POST.get('url_imagen', 'https://images.unsplash.com/photo-1552346154-21d32810aba3?auto=format&fit=crop&w=600&q=80')
        
        # Obtenemos el usuario actual de prueba
        usuario_actual = Usuario.objects().first()
        categoria_obj = Categoria.objects(id=categoria_id).first()
        
        if usuario_actual and categoria_obj:
            # Creamos las referencias embebidas requeridas por el modelo
            vendedor_ref = UsuarioRef(
                id_usuario=usuario_actual.id,
                username=usuario_actual.username,
                nombre1=usuario_actual.nombre1,
                apellido1=usuario_actual.apellido1,
                reputacion=usuario_actual.reputacion.como_vendedor.promedio if usuario_actual.reputacion and usuario_actual.reputacion.como_vendedor else None
            )
            
            categoria_ref = CategoriaRef(
                id_categoria=categoria_obj.id,
                nombre=categoria_obj.nombre
            )
            
            foto_principal = FotoArticulo(
                id_foto=1,
                url_imagen=url_imagen,
                es_principal=True
            )
            
            # Guardamos el nuevo artículo en MongoDB
            Articulo(
                nombre=nombre,
                descripcion=descripcion,
                precio=float(precio),
                stock=int(stock),
                talla=talla,
                marca=marca,
                estado_conservacion=estado_conservacion,
                estado_publicacion='Disponible',
                categoria=categoria_ref,
                vendedor=vendedor_ref,
                fotos=[foto_principal]
            ).save()
            
            return redirect('catalogo')
            
    # Si es GET, cargamos las categorías disponibles en la BD
    categorias = Categoria.objects.all()
    return render(request, 'core/publicar.html', {'categorias': categorias})


def carrito(request):
    # Simulamos el usuario actual (puedes adaptarlo luego con tu sesión o token)
    # Por ahora tomamos al primer usuario de prueba de la base de datos
    usuario = Usuario.objects().first()
    
    grupos_por_vendedor = {}
    total_general = 0
    
    if usuario and usuario.carrito:
        for item in usuario.carrito:
            # Buscamos el artículo real en la base de datos usando la referencia
            articulo = Articulo.objects(id=item.id_articulo).first()
            if articulo:
                vendedor_nombre = articulo.vendedor.username
                if vendedor_nombre not in grupos_por_vendedor:
                    grupos_por_vendedor[vendedor_nombre] = []
                
                subtotal = float(articulo.precio) * item.cantidad
                total_general += subtotal
                
                grupos_por_vendedor[vendedor_nombre].append({
                    'p': articulo,
                    'qty': item.cantidad,
                    'subtotal': subtotal
                })
                
    return render(request, 'core/carrito.html', {
        'grupos': grupos_por_vendedor,
        'total_general': total_general
    })


def login_view(request):
    return render(request, 'core/login.html')

def admin_view(request):
    return render(request, 'core/admin.html')
