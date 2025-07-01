from django.db import models

class PromptData(models.Model):
    start = models.TextField()
    date = models.TextField()
    change_date = models.TextField()
    place = models.TextField()
    participants = models.TextField()
    email_type = models.TextField()
    link = models.TextField()
    attachments = models.TextField()
    details = models.TextField()
    duration = models.TextField()
    previous_messages = models.TextField()
