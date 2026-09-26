from django.shortcuts import render
from .models import Articulo, Categoria

def catalogo(request):
    categorias = Categoria.objects.all()
    #solo mostrar articulos disponibles
    articulos = Articulo.objects.filter(estado_publicacion='Activo')

    # captura de parametros GET
    categoria_id = request.GET.get('categoria')
    precio_min = request.GET.get('precio_min')
    precio_max = request.GET.get('precio_max')

    #filtros opcionales
    talla = request.GET.get('talla')
    marca = request.GET.get('marca')
    estado = request.GET.get('estado_conservacion')

    # aplicar filtros obligatorios
    if categoria_id and precio_min and precio_max:
        articulos = articulos.filter(
            id_categoria=categoria_id,
            precio__gte=precio_min,
            precio__lte=precio_max
        )

        #sumar filtros alternativos
        if talla: articulos = articulos.filter(talla=tall)
        if marca: articulos = articulos.filter(marca=marca)
        if estado: articulos = articulos.filter(estado_conservacion=estado)

        mensaje = None if articulos.exists() else "Sin resultados, aplia tus filtros"
    else:
        articulos = Articulo.objects.none()
        mensaje = "Define categoria y precio para buscar"

    context = {
        'articulos': articulos,
        'categorias': categorias,
        'mensaje': mensaje
    }
    return render(request, 'core/catalogo.html', context) 

