from django.db import models
from django.contrib.postgres.fields import ArrayField  # 🔥 Importamos ArrayField

class ScheduleConfig(models.Model):
    gmail = models.EmailField(unique=True)
    work_hours_from = models.TimeField(blank=True, null=True)
    work_hours_to = models.TimeField(blank=True, null=True)
    no_meetings_hours_from = models.TimeField(blank=True, null=True)
    no_meetings_hours_to = models.TimeField(blank=True, null=True)
    no_meetings_days = ArrayField(models.CharField(max_length=10, blank=True), blank=True, null=True) 
    tolerance = models.IntegerField(default=0)
