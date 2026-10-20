
"""
Django settings for streetwear_c2c project.
"""

from pathlib import Path
import os
from mongoengine import connect # IMPORTANTE: Importamos el conector de MongoEngine

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-tu-clave-secreta-aqui'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

# Permitimos ngrok y conexiones locales para que el equipo pueda probar
ALLOWED_HOSTS = ['*']
# Reemplaza esta URL con la que te dé ngrok en el momento
CSRF_TRUSTED_ORIGINS = ['https://tu-enlace-ngrok.ngrok-free.app'] 


# ==============================================================================
# 1. APLICACIONES INSTALADAS (Puro MongoDB)
# ==============================================================================
INSTALLED_APPS = [
    # Desactivamos los módulos nativos SQL de Django comentándolos con '#':
    # 'django.contrib.admin',
    # 'django.contrib.auth',
    # 'django.contrib.contenttypes',
    # 'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    
    # Tu aplicación principal (donde están los modelos de MongoEngine)
    'core',
]

# ==============================================================================
# 2. MIDDLEWARES
# ==============================================================================
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    # 'django.contrib.sessions.middleware.SessionMiddleware', # Desactivado por requerir SQL
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    # 'django.contrib.auth.middleware.AuthenticationMiddleware', # Desactivado por requerir SQL
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'streetwear_c2c.urls.py'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                # 'django.contrib.auth.context_processors.auth', # Desactivado
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'streetwear_c2c.wsgi.application'


# ==============================================================================
# 3. BASE DE DATOS (Desactivamos SQL y conectamos MongoDB)
# ==============================================================================

# Apagamos el motor relacional (SQL) por defecto de Django
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.dummy'
    }
}

# Iniciamos la conexión nativa orientada a documentos hacia el contenedor en OrbStack
connect('c2c_db_mongo', host='localhost', port=27017)


# ==============================================================================
# CONFIGURACIONES DE ARCHIVOS ESTÁTICOS Y LENGUAJE
# ==============================================================================
LANGUAGE_CODE = 'es-cl'
TIME_ZONE = 'America/Santiago'
USE_I18N = True
USE_TZ = True

STATIC_URL = 'static/'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
