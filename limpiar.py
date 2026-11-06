from core.models import Articulo, Chat, Venta, Reporte, Usuario

def borrar(modelo):
    return modelo._get_collection().delete_many({}).deleted_count

print('Artículos :', borrar(Articulo))
print('Reportes  :', borrar(Reporte))
print('Chats     :', borrar(Chat))
print('Ventas    :', borrar(Venta), '(incluye las valoraciones)')

# Vacía carrito y favoritos de los usuarios que queden
r = Usuario._get_collection().update_many({}, {'$set': {'carrito': [], 'favoritos': []}})
print('Usuarios con carrito/favoritos vaciados:', r.modified_count)

# --- OPCIONAL: borrar también los usuarios (conserva a los admin) ---
# print('Usuarios  :', Usuario._get_collection().delete_many({'rol': {'$ne': 'admin'}}).deleted_count)