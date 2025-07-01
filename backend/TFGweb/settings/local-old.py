from .base import *
import os
import os
import nltk
DEBUG = True

SECRET_KEY = os.getenv('SECRET_KEY', 'insecure-dev-key')

ALLOWED_HOSTS = ['localhost', '127.0.0.1', 'aiserv.es', 'www.aiserv.es']

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'aiserv',
        'USER': 'aiservuser',
        'PASSWORD': 'adsf3124',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}

SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False

CSRF_TRUSTED_ORIGINS = [
    "http://localhost:5173",
]

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NLTK_DATA = os.path.join(BASE_DIR, 'nltk_data')
nltk.data.path.append(NLTK_DATA)


CORS_ALLOWED_ORIGINS = [
    'https://aiserv.es',
    'https://www.aiserv.es',
]

CSRF_TRUSTED_ORIGINS = [
    'https://aiserv.es',
    'https://www.aiserv.es',
]

SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_SSL_REDIRECT = True
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

