from django.db import models

class NotificationConfig(models.Model):
    gmail = models.EmailField()
    title = models.CharField(max_length=100, blank=True, null=True)
    body = models.CharField(max_length=100, blank=True, null=True)
    sent_date = models.DateTimeField(blank=True, null=True) 
    expire_date = models.DateTimeField(blank=True, null=True)
    read = models.BooleanField(default=False)
    sender = models.EmailField(unique=False)
    type = models.CharField(max_length=100, blank=True, null=True)
    label = models.CharField(max_length=100, blank=True, null=True)
    

    