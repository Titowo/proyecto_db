import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from bson import ObjectId
from bson.errors import InvalidId
from .models import Articulo

def crear_respuesta_error(codigo, mensaje, detalles=None, status=400):
    error_data = {"codigo": codigo, "mensaje": mensaje}
    if detalles:
        error_data["detalles"] = detalles
    return JsonResponse({"success": False, "error": error_data}, status=status)

@csrf_exempt
def api_articulos_catalogo(request):
    if request.method != 'GET':
        return crear_respuesta_error("METODO_NO_PERMITIDO", "Use GET", status=405)
    
    # 1. Extraer parámetros obligatorios
    id_categoria = request.GET.get('id_categoria')
    precio_min = request.GET.get('precio_min')
    precio_max = request.GET.get('precio_max')
    
    faltan = []
    if not id_categoria: faltan.append("id_categoria")
    if not precio_min: faltan.append("precio_min")
    if not precio_max: faltan.append("precio_max")
    
    if faltan:
        return crear_respuesta_error(
            "DATOS_INVALIDOS", 
            "Faltan filtros obligatorios.", 
            {"faltan": faltan}, 
            status=400
        )
        
    try:
        precio_min = float(precio_min)
        precio_max = float(precio_max)
        id_categoria_obj = ObjectId(id_categoria)
    except (ValueError, InvalidId):
        return crear_respuesta_error("DATOS_INVALIDOS", "Formato de parámetros incorrecto (precio o id_categoria).")

    # 2. Construir la consulta base en MongoEngine
    query = {
        "estado_publicacion": "Disponible",
        "categoria__id_categoria": id_categoria_obj,
        "precio__gte": precio_min,
        "precio__lte": precio_max
    }
    
    # 3. Filtros opcionales
    talla = request.GET.get('talla')
    if talla: query["talla"] = talla
        
    marca = request.GET.get('marca')
    if marca: query["marca"] = marca
        
    estado = request.GET.get('estado')
    if estado: query["estado_conservacion"] = estado
        
    # 4. Paginación
    try:
        page = int(request.GET.get('page', 1))
        limit = min(int(request.GET.get('limit', 20)), 50) # Máximo 50 según informe
    except ValueError:
        page, limit = 1, 20
        
    skip = (page - 1) * limit
    
    # 5. Ejecutar consulta
    articulos_qs = Articulo.objects(**query).order_by('precio')
    total = articulos_qs.count()
    articulos_pagina = articulos_qs.skip(skip).limit(limit)
    
    # 6. Formatear la respuesta exacta como en el documento
    data = []
    for art in articulos_pagina:
        # Buscar la foto principal
        foto_principal = next((f.url_imagen for f in art.fotos if f.es_principal), None)
        if not foto_principal and art.fotos:
            foto_principal = art.fotos[0].url_imagen # Fallback
            
        data.append({
            "id_articulo": str(art.id),
            "nombre": art.nombre,
            "precio": float(art.precio),
            "talla": art.talla,
            "estado_conservacion": art.estado_conservacion,
            "foto_principal": foto_principal,
            "vendedor": {
                "username": art.vendedor.nombre_usuario if art.vendedor else "Desconocido",
                "reputacion": 5.0 # Aquí iría la reputación real extraída de la referencia
            }
        })
        
    respuesta = {
        "success": True,
        "data": data,
        "meta": {
            "page": page,
            "limit": limit,
            "total": total
        }
    }
    return JsonResponse(respuesta, status=200)
