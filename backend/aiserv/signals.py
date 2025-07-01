from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User as AuthUser
from .models import aiservUser, PriorityConfig
from .config.priority import default_low, default_moderate, default_high, default_urgent 

@receiver(post_save, sender=AuthUser)
def create_aiserv_user(sender, instance, created, **kwargs):
    if created:

        print("Nuevo usuario creado")
        


@receiver(post_save, sender=aiservUser)
def create_priority_config(sender, instance, created, **kwargs):
    if created:
        PriorityConfig.objects.create(
            gmail=instance.email,
            notification_low=default_low(),
            notification_moderate=default_moderate(),
            notification_high=default_high(),
            notification_urgent=default_urgent()
        )
