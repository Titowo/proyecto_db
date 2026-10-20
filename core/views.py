from django.shortcuts import render
from .models import Articulo
from bson import ObjectId
from bson.errors import InvalidId

def catalogo(request):
    query = {'estado_publicacion__ne': 'Vendido'}
    mensaje = None
    articulos = []

    # =====================================================================
    # 1. OBTENER CATEGORÍAS DIRECTO CON PYMONGO (Infalible)
    # =====================================================================
    pipeline = [
        {"$match": {"estado_publicacion": {"$ne": "Vendido"}}},
        {"$group": {
            "_id": "$categoria.id_categoria", 
            "nombre": {"$first": "$categoria.nombre"}
        }}
    ]
    
    # Al usar _get_collection() ignoramos los bugs de MongoEngine y 
    # conectamos directo con el motor C de MongoDB.
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

   
   # print("\n>>> DEBUG CATEGORIAS EXTRAIDAS:", categorias, "\n")

    # =====================================================================
    # 2. LÓGICA DE FILTRADO
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
                    query['categoria__id_categoria'] = ObjectId(categoria_id)
                    query['precio__gte'] = precio_min_float
                    query['precio__lte'] = precio_max_float
                    
                    talla = request.GET.get('talla')
                    marca = request.GET.get('marca')
                    estado_conservacion = request.GET.get('estado_conservacion')
                    
                    if talla:
                        query['talla'] = talla
                    if marca:
                        query['marca'] = marca
                    if estado_conservacion:
                        query['estado_conservacion'] = estado_conservacion
                        
                    articulos = Articulo.objects(**query)
                    
                    if not articulos:
                        mensaje = "No encontramos artículos que coincidan con estos filtros."
                        
            except ValueError:
                mensaje = "Los precios deben ser numéricos."
            except InvalidId:
                articulos = []
        else:
            mensaje = "Debes seleccionar una categoría y el rango de precios para filtrar."
    else:
        articulos = Articulo.objects(**query)

    context = {
        'articulos': articulos,
        'categorias': categorias,
        'mensaje': mensaje
    }
    return render(request, 'core/catalogo.html', context)
