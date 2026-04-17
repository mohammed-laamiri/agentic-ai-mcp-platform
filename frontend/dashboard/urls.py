"""
URL configuration for dashboard app.
"""

from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    path('', views.index, name='index'),
    path('health-check/', views.health_check, name='health_check'),
]
