from django.contrib import admin
from .models import aiservUser, StartConfig, ScheduleConfig, PriorityConfig, EventConfig, PromptData, PromptResponse

admin.site.register(aiservUser)
admin.site.register(StartConfig)
admin.site.register(ScheduleConfig)
admin.site.register(PriorityConfig)
admin.site.register(EventConfig)
admin.site.register(PromptData)
admin.site.register(PromptResponse)
