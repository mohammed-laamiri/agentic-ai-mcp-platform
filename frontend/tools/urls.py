"""
URL configuration for tools app.
"""

from django.urls import path
from . import views

app_name = 'tools'

urlpatterns = [
    path('', views.tool_list, name='list'),
    path('register/', views.tool_register, name='register'),
    path('<str:tool_id>/', views.tool_detail, name='detail'),
]
