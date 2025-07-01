# from django.contrib.auth.models import BaseUserManager

# # Creamos un "Manager" personalizado para gestionar la creación de usuarios y superusuarios.
# class aiservUserManager(BaseUserManager):
    
#     # Función para crear un usuario normal
#     def create_user(self, email, username, password=None, **extra_fields):

#         # Si no se encuentra el email mandamos un erro ya que es obligatorio
#         if not email:
#             raise ValueError('El email es obligatorio')
        
#         # Normalizamos el email, conviertiendo mayusculas en minusculas...
#         email = self.normalize_email(email)
        
#         # Creamos una instancia del modelo de usuario
#         user = self.model(email=email, username=username, **extra_fields)
        
#         # Establecemos la contraseña usando 'set_password' que la cifra automáticamente
#         user.set_password(password)
        
#         # Guardamos el usuario en la base de datos
#         user.save(using=self._db)
        
#         return user

#     # Método para crear un superusuario
#     def create_superuser(self, email, username, password=None, **extra_fields):

#         # Asignamos valores predeterminados a los campos extra
#         extra_fields.setdefault('is_staff', True)
#         extra_fields.setdefault('is_superuser', True)  
        
#         # Verificamos que los valores de 'is_staff' y 'is_superuser' sean correctos
#         if extra_fields.get('is_staff') is not True:
#             raise ValueError('Superuser debe tener is_staff=True.')
#         if extra_fields.get('is_superuser') is not True:
#             raise ValueError('Superuser debe tener is_superuser=True.')

#         # Llamamos al método de crear usuario estándar, pero con permisos de superusuario
#         return self.create_user(email, username, password, **extra_fields)
