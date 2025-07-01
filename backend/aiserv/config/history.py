from django.db import models

class HistoryConfig(models.Model):
    gmail = models.EmailField()
    sender = models.EmailField()
    subject = models.CharField(max_length=100, blank=True, null=True)
    summary = models.CharField(max_length=100, blank=True, null=True)
    sent_date = models.TimeField(blank=True, null=True)  
    expire_date = models.TimeField(blank=True, null=True)
