from rest_framework import serializers
from .models import ScheduleConfig, EventConfig, StartConfig, PriorityConfig,HistoryConfig,NotificationConfig

class ScheduleConfigSerializer(serializers.ModelSerializer):
    class Meta:
        model = ScheduleConfig
        fields = '__all__'

class EventConfigSerializer(serializers.ModelSerializer):
    class Meta:
        model = EventConfig
        fields = '__all__'

class StartConfigSerializer(serializers.ModelSerializer):
    class Meta:
        model = StartConfig
        fields = ['gmail', 'full_name', 'charge', 'language', 'details']

class PriorityConfigSerializer(serializers.ModelSerializer):
    class Meta:
        model = PriorityConfig
        fields = [
            'gmail',
            'priority_issues',
            'priority_people',
            'priority_hours_from',
            'priority_hours_to',
            'priority_days'
        ]

class PriorityNotificationOnlySerializer(serializers.ModelSerializer):
    class Meta:
        model = PriorityConfig
        fields = [
            'gmail',
            'notification_low',
            'notification_moderate',
            'notification_high',
            'notification_urgent'
        ]

class HistoryConfigSerializer(serializers.ModelSerializer):
    class Meta:
        model = HistoryConfig
        fields = ['gmail', 'sender', 'subject', 'summary', 'sent_date', 'expire_date']

class NotificationConfigSerializer(serializers.ModelSerializer):
    class Meta:
        model = NotificationConfig
        fields = ['gmail', 'title', 'body', 'sent_date', 'expire_date', 'read', 'sender','type','label']
