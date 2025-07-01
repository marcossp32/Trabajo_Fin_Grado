from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('connect/', views.connect, name='connect'),
    path('oauth2callback/', views.oauth2callback, name='oauth2callback'),
    path('logout/', views.logout_view, name='logout'),
    path('configurator/', views.configurator, name='configurator'),
]
