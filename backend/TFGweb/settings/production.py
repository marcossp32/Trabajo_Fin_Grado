from .base import *
import os
from .base import LOGGING as BASE_LOGGING

DEBUG = False

SECRET_KEY = os.getenv('SECRET_KEY')

ALLOWED_HOSTS = ['aiserv.es', 'www.aiserv.es']

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.getenv('DB_NAME'),
        'USER': os.getenv('DB_USER'),
        'PASSWORD': os.getenv('DB_PASSWORD'),
        'HOST': os.getenv('DB_HOST'),
        'PORT': os.getenv('DB_PORT'),
    }
}

CORS_ALLOWED_ORIGINS = [
    'https://aiserv.es',
]

CSRF_TRUSTED_ORIGINS = [
    'https://aiserv.es',
]

SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_SSL_REDIRECT = True
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

LOG_DIR = os.path.join(BASE_DIR, "logs")
os.makedirs(LOG_DIR, exist_ok=True)

BASE_LOGGING["handlers"]["file"] = {
    "level": "INFO",
    "class": "logging.handlers.RotatingFileHandler",
    "filename": os.path.join(LOG_DIR, "app.log"),
    "maxBytes": 1024 * 1024 * 5,  # 5 MB
    "backupCount": 3,
    "formatter": "standard",
}

BASE_LOGGING["root"]["handlers"].append("file")

LOGGING = BASE_LOGGING
