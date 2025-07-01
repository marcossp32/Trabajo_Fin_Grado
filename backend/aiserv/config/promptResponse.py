from django.db import models

class PromptResponse(models.Model):
    start = models.TextField()
    email = models.TextField()
    availability_yes = models.TextField()
    availability_no = models.TextField()
    instructions = models.TextField()
    emotion1 = models.TextField()
    emotion2 = models.TextField()
    emotion3 = models.TextField()
    previous_messages = models.TextField()
    #Configuracion Start
    full_name = models.TextField()
    charge = models.TextField()
    language = models.TextField()
    details = models.TextField()
    #Configuracion schedule
    work_hour = models.TextField()
    decline_event_hour = models.TextField()
    decline_event_day = models.TextField()
    #Configuracion Priority
    priority_people = models.TextField()
    priority_issues = models.TextField()
    #Configuracion Event
    duration_event = models.TextField()
    max_events = models.TextField()







