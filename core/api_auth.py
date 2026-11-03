# core/api_auth.py
import json
import bcrypt
import jwt
import datetime
from django.http import JsonResponse
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from .models import Usuario

JWT_SECRET = getattr(settings, 'SECRET_KEY', 'super-secret-key')

def crear_respuesta_error(codigo, mensaje, detalles=None, status=400):
    error_data = {"codigo": codigo, "mensaje": mensaje}
    if detalles:
        error_data["detalles"] = detalles
    return JsonResponse({"success": False, "error": error_data}, status=status)

@csrf_exempt
def api_register(request):
    if request.method != 'POST':
        return crear_respuesta_error("METODO_NO_PERMITIDO", "Use POST", status=405)
    
    try:
        data = json.loads(request.body)
        
        # Validar campos obligatorios según el modelo y RF1
        campos_req = ['nombre1', 'apellido1', 'username', 'correo', 'contrasena']
        faltantes = [c for c in campos_req if c not in data or not data[c]]
        if faltantes:
            return crear_respuesta_error("DATOS_INVALIDOS", "Faltan campos obligatorios", {"faltan": faltantes})
            
        # Verificar duplicados (409 Conflict)
        if Usuario.objects(correo=data['correo']).first() or Usuario.objects(nombre_usuario=data['username']).first():
            return crear_respuesta_error("DUPLICADO", "El correo o @usuario ya existen", status=409)
            
        # Hashear contraseña con bcrypt factor 12
        hashed_pw = bcrypt.hashpw(data['contrasena'].encode('utf-8'), bcrypt.gensalt(12)).decode('utf-8')
        
        # Crear usuario
        nuevo_usuario = Usuario(
            nombre1=data['nombre1'],
            nombre2=data.get('nombre2', ''),
            apellido1=data['apellido1'],
            apellido2=data.get('apellido2', ''),
            nombre_usuario=data['username'],
            correo=data['correo'],
            password_hash=hashed_pw,
            rol='usuario'
        )
        nuevo_usuario.save()
        
        return JsonResponse({"success": True, "data": {"id_usuario": str(nuevo_usuario.id), "username": nuevo_usuario.nombre_usuario}}, status=201)
        
    except Exception as e:
        return crear_respuesta_error("ERROR_INTERNO", str(e), status=500)

@csrf_exempt
def api_login(request):
    if request.method != 'POST':
        return crear_respuesta_error("METODO_NO_PERMITIDO", "Use POST", status=405)
        
    try:
        data = json.loads(request.body)
        if 'correo' not in data or 'contrasena' not in data:
            return crear_respuesta_error("DATOS_INVALIDOS", "Falta correo o contraseña")
            
        usuario = Usuario.objects(correo=data['correo']).first()
        
        # Verificar usuario y contraseña
        if not usuario or not bcrypt.checkpw(data['contrasena'].encode('utf-8'), usuario.password_hash.encode('utf-8')):
            return crear_respuesta_error("CREDENCIALES_INVALIDAS", "Correo o contraseña incorrectos", status=401)
            
        # Generar Tokens
        expira_en = 900 # 15 minutos
        payload_access = {
            'sub': str(usuario.id),
            'rol': getattr(usuario, 'rol', 'usuario'),
            'exp': datetime.datetime.utcnow() + datetime.timedelta(seconds=expira_en)
        }
        payload_refresh = {
            'sub': str(usuario.id),
            'exp': datetime.datetime.utcnow() + datetime.timedelta(days=7)
        }
        
        access_token = jwt.encode(payload_access, JWT_SECRET, algorithm='HS256')
        refresh_token = jwt.encode(payload_refresh, JWT_SECRET, algorithm='HS256')
        
        respuesta = {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "expira_en": expira_en,
            "usuario": {"username": usuario.nombre_usuario, "rol": getattr(usuario, 'rol', 'usuario')}
        }
        
        return JsonResponse({"success": True, "data": respuesta}, status=200)
        
    except Exception as e:
        return crear_respuesta_error("ERROR_INTERNO", str(e), status=500)
