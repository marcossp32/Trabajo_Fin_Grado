from django.apps import AppConfig

class aiservConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'aiserv'


    def ready(self):
        import aiserv.signals
