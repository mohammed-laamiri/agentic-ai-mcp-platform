"""
URL configuration for the MCP Platform frontend.
"""

from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('dashboard.urls')),
    path('tasks/', include('tasks.urls')),
    path('tools/', include('tools.urls')),
]
