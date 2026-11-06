import os, sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'streetwear_c2c.settings')
django.setup()

from core.models import Usuario

if len(sys.argv) < 2:
    print('Uso: python dar_admin.py correo@ejemplo.cl   (o @usuario)')
    sys.exit(1)

dato = sys.argv[1].strip()
quitar = len(sys.argv) > 2 and sys.argv[2] == '--quitar'

col = Usuario._get_collection()
filtro = {'nombre_usuario': dato} if dato.startswith('@') else {'email': dato.lower()}
usuario = col.find_one(filtro, {'email': 1, 'nombre_usuario': 1, 'rol': 1})

if not usuario:
    print('No se encontró ningún usuario con', dato)
    sys.exit(1)

nuevo = 'usuario' if quitar else 'admin'
col.update_one({'_id': usuario['_id']}, {'$set': {'rol': nuevo}})
print(f"{usuario.get('nombre_usuario')} ({usuario.get('email')}): rol {usuario.get('rol')!r} -> {nuevo!r}")