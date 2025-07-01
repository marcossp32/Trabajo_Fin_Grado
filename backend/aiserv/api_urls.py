from django.urls import path
from .api_views import(
    ConnectAPIView,
    OAuthCallbackAPIView,
    GetUserDataAPIView,
    LogoutAPIView,
    GetCalendarEventsAPIView,
    SaveStartConfigAPIView,
    SaveScheduleConfigAPIView,
    SavePriorityConfigAPIView,
    SaveEventConfigAPIView,
    StartFlowRequestAPIView,
    StartFlowAPIView,
    GetUserHistoryAPIView,
    GetNotificationsAPIView,
    GetOnlyNotificationLevelsAPIView,
    UpdatePriorityNotificationsAPIView,
    CompleteOnboardingAPIView
)

urlpatterns = [
    path('connect/', ConnectAPIView.as_view(), name='connect'),
    path('connect/callback/', OAuthCallbackAPIView.as_view(), name='oauth_callback'),
    path('user/data/', GetUserDataAPIView.as_view(), name='get_user_data'),
    path('logout/', LogoutAPIView.as_view(), name='logout'),
    path('get-calendar-events/', GetCalendarEventsAPIView.as_view(), name='get_calendar_events'),
    path('save-start-config/', SaveStartConfigAPIView.as_view(), name='save_start_config'),
    path('save-schedule-config/', SaveScheduleConfigAPIView.as_view(), name='save_schedule_config'),
    path('save-priority-config/', SavePriorityConfigAPIView.as_view(), name='save_priority_config'),
    path('save-event-config/', SaveEventConfigAPIView.as_view(), name='save_event_config'),
    path('start-flow-request/', StartFlowRequestAPIView.as_view(), name='start_flow_request'),
    path('start-flow/', StartFlowAPIView.as_view(), name='start_flow'),
    path('get-user-history/', GetUserHistoryAPIView.as_view(), name='get-user-history'),
    path('get-notifications/', GetNotificationsAPIView.as_view(), name='get-notifications'),
    path('get-priority-notifications/', GetOnlyNotificationLevelsAPIView.as_view(), name='get-priority-notifications'),
    path('update-priority-config/', UpdatePriorityNotificationsAPIView.as_view(), name='update-priority-config'),
    path("onboarding/complete/", CompleteOnboardingAPIView.as_view()),


]
