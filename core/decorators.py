import jwt
from functools import wraps
from django.http import JsonResponse
from django.conf import settings

JWT_SECRET = getattr(settings, 'SECRET_KEY', 'super-secret-key')

def crear_respuesta_error(codigo, mensaje, status=400):
    """Función auxiliar para mantener el formato JSON de errores del informe"""
    return JsonResponse({
        "success": False, 
        "error": {"codigo": codigo, "mensaje": mensaje}
    }, status=status)

def requiere_jwt(rol_requerido=None):
    """
    Decorador para proteger rutas con JWT.
    Opcionalmente verifica si el usuario tiene un rol específico (ej. 'admin').
    """
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            # 1. Extraer el token del encabezado
            auth_header = request.headers.get('Authorization')
            if not auth_header or not auth_header.startswith('Bearer '):
                return crear_respuesta_error("TOKEN_AUSENTE", "No se envió el token JWT o el formato es incorrecto.", status=401)
            
            token = auth_header.split(' ')[1]
            
            # 2. Decodificar y validar el token
            try:
                payload = jwt.decode(token, JWT_SECRET, algorithms=['HS256'])
                
                # 3. Validar el rol si la ruta lo exige (ej. rutas de administrador)
                if rol_requerido and payload.get('rol') != rol_requerido:
                    return crear_respuesta_error("SIN_PERMISO", "Se requiere rol administrador.", status=403)
                
                # 4. Adjuntar la información del usuario a la request
                request.jwt_payload = payload
                
            except jwt.ExpiredSignatureError:
                return crear_respuesta_error("TOKEN_INVALIDO", "El token ha expirado.", status=401)
            except jwt.InvalidTokenError:
                return crear_respuesta_error("TOKEN_INVALIDO", "El token es inválido o está malformado.", status=401)
            
            # Si todo está bien, ejecutar la vista original
            return view_func(request, *args, **kwargs)
        return _wrapped_view
    return decorator
