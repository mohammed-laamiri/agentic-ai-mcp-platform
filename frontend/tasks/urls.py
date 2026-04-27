"""
URL configuration for tasks app.
"""

from django.urls import path
from tasks import views

app_name = "tasks"

urlpatterns = [
    path("", views.task_list, name="list"),
    path("create/", views.task_create, name="create"),
    path("<str:task_id>/", views.task_detail, name="detail"),
    path("<str:task_id>/execute/", views.task_execute, name="execute"),
    path("<str:task_id>/complete/", views.task_complete, name="complete"),
    path("<str:task_id>/fail/", views.task_fail, name="fail"),
]