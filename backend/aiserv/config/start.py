from django.db import models

class StartConfig(models.Model):
    gmail = models.EmailField(unique=True)  # Se mete el campo de gmail para tener conexcion entre las tablas
    full_name = models.CharField(max_length=100, blank=True, null=True)
    charge = models.CharField(max_length=100, blank=True, null=True)
    language = models.CharField(max_length=50, blank=True, null=True)
    details = models.TextField(blank=True, null=True)
