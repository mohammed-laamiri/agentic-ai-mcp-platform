"""
Dashboard views for the Django frontend.
"""

from django.shortcuts import render
from django.http import HttpResponse

from core.api_client import api_client
from core.exceptions import APIError, APIConnectionError


def index(request):
    """Display dashboard with stats."""
    # Fetch data
    tasks = []
    tools = []
    health_ok = False

    try:
        health = api_client.health_check()
        health_ok = health.get('status') == 'ok'
    except (APIConnectionError, APIError):
        health_ok = False

    try:
        tasks = api_client.list_tasks(skip=0, limit=1000)
    except (APIConnectionError, APIError):
        tasks = []

    try:
        tools = api_client.list_tools()
    except (APIConnectionError, APIError):
        tools = []

    # Calculate stats
    total_tasks = len(tasks)
    pending_tasks = sum(1 for t in tasks if t.get('status') == 'pending')
    completed_tasks = sum(1 for t in tasks if t.get('status') == 'completed')
    failed_tasks = sum(1 for t in tasks if t.get('status') == 'failed')
    total_tools = len(tools)

    context = {
        'health_ok': health_ok,
        'total_tasks': total_tasks,
        'pending_tasks': pending_tasks,
        'completed_tasks': completed_tasks,
        'failed_tasks': failed_tasks,
        'total_tools': total_tools,
        'recent_tasks': tasks[:5],
    }

    return render(request, 'dashboard/index.html', context)


def health_check(request):
    """HTMX endpoint for health check indicator."""
    try:
        health = api_client.health_check()
        if health.get('status') == 'ok':
            return HttpResponse(
                '<span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800">'
                'API Online'
                '</span>'
            )
    except (APIConnectionError, APIError):
        pass

    return HttpResponse(
        '<span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-red-100 text-red-800">'
        'API Offline'
        '</span>'
    )
