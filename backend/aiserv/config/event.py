from django.db import models
from django.contrib.postgres.fields import ArrayField 

class EventConfig(models.Model):
    gmail = models.EmailField(unique=True)
    meeting_duration = models.IntegerField(blank=True, null=True)
    notify_meeting = models.BooleanField(default=False)
    propose_meeting = models.BooleanField(default=False)
    meeting_limit = models.IntegerField(blank=True, null=True)
    free_days = ArrayField(models.DateField(), blank=True, null=True)  
