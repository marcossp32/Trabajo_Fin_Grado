from .base import *
import os
import nltk

# --- DEBUG & SECRET ---
DEBUG = os.getenv('DEBUG', 'False') == 'True'
SECRET_KEY = os.getenv('SECRET_KEY', 'insecure-dev-key')

# --- HOSTS ---
ALLOWED_HOSTS = os.getenv(
    'ALLOWED_HOSTS',
    'localhost,127.0.0.1,aiserv.es,www.aiserv.es'
).split(',')

# --- BASE DIR & NLTK ---
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NLTK_DATA = os.path.join(BASE_DIR, 'nltk_data')
nltk.data.path.append(NLTK_DATA)

# --- DATABASE ---
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.getenv('DB_NAME', 'aiserv'),
        'USER': os.getenv('DB_USER', 'aiservuser'),
        'PASSWORD': os.getenv('DB_PASSWORD', 'adsf3124'),
        'HOST': os.getenv('DB_HOST', 'localhost'),
        'PORT': os.getenv('DB_PORT', '5432'),
    }
}

# --- CORS & CSRF ---
CORS_ALLOWED_ORIGINS = [
    'https://aiserv.es',
    'https://www.aiserv.es',
    # si necesitas desarrollo en Vite/React:
    'http://localhost:5173',
]

CSRF_TRUSTED_ORIGINS = [
    'https://aiserv.es',
    'https://www.aiserv.es',
    'http://localhost:5173',
]

SESSION_COOKIE_DOMAIN = ".aiserv.es"
SESSION_COOKIE_SECURE = True
SESSION_COOKIE_SAMESITE = "None" 
CSRF_COOKIE_SECURE = True
CSRF_COOKIE_SAMESITE = "None" 
SECURE_SSL_REDIRECT = not DEBUG
SECURE_HSTS_SECONDS = 31_536_000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# --- Opcional: credenciales enviadas en CORS ---
CORS_ALLOW_CREDENTIALS = True
