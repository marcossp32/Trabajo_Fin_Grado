from django.db import models
from django.contrib.postgres.fields import ArrayField 

def default_low():
    return ["compañero", "confirm_event"]

def default_moderate():
    return ["nuevo cliente", "new_event", "change_event", "cancel_event", "decline_event"]

def default_high():
    return ["cliente importante", "meeting_invitation", "doubt"]

def default_urgent():
    return ["superior"]

class PriorityConfig(models.Model):
    gmail = models.EmailField(unique=True)
    priority_issues = models.CharField(max_length=100, blank=True, null=True)
    priority_people = models.CharField(max_length=100, blank=True, null=True)
    priority_hours_from = models.TimeField(blank=True, null=True)
    priority_hours_to = models.TimeField(blank=True, null=True)  
    priority_days = ArrayField(models.CharField(max_length=10, blank=True), blank=True, null=True) 

    notification_low = ArrayField(
        models.CharField(max_length=100, blank=True),
        blank=True,
        null=True,
        default=default_low
    )
    notification_moderate = ArrayField(
        models.CharField(max_length=100, blank=True),
        blank=True,
        null=True,
        default=default_moderate
    )
    notification_high = ArrayField(
        models.CharField(max_length=100, blank=True),
        blank=True,
        null=True,
        default=default_high
    )
    notification_urgent = ArrayField(
        models.CharField(max_length=100, blank=True),
        blank=True,
        null=True,
        default=default_urgent
    )
