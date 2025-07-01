from django.db import models
from django.utils.timezone import now
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from encrypted_model_fields.fields import EncryptedCharField

class aiservUserManager(BaseUserManager):
    def create_user(self, email, username, **extra_fields):
        if not email:
            raise ValueError("El email es obligatorio.")
        if not username:
            raise ValueError("El nombre de usuario es obligatorio.")

        email = self.normalize_email(email)
        user = self.model(email=email, username=username, **extra_fields)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, username, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, username, **extra_fields)

class aiservUser(AbstractBaseUser, PermissionsMixin):
    password = None
    email = models.EmailField(unique=True)  # Email único
    username = models.CharField(max_length=255)  # Nombre de usuario
    date_joined = models.DateTimeField(default=now)  # Fecha de primera conexión
    auth_token_access = EncryptedCharField(max_length=2048, null=True, blank=True)
    auth_token_refresh = EncryptedCharField(max_length=2048, null=True, blank=True)
    is_active = models.BooleanField(default=True)  # Requerido para usuarios activos
    is_staff = models.BooleanField(default=False)  # Requerido para superusuarios
    is_active_auto = models.BooleanField(default=False)  # Nuevo atributo para autogestión
    is_first_login = models.BooleanField(default=True)


    objects = aiservUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    def __str__(self):
        return f"{self.username} ({self.email})"
