"""
Task views for the Django frontend.
"""

import json

from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import HttpResponse
from django.views.decorators.http import require_http_methods

from core.api_client import api_client
from core.exceptions import APIError, APIConnectionError, APINotFoundError

from .forms import TaskCreateForm


def task_list(request):
    """Display list of all tasks."""
    skip = int(request.GET.get('skip', 0))
    limit = int(request.GET.get('limit', 20))

    try:
        tasks = api_client.list_tasks(skip=skip, limit=limit)
    except APIConnectionError:
        messages.error(request, "Cannot connect to backend API")
        tasks = []
    except APIError as e:
        messages.error(request, str(e))
        tasks = []

    context = {
        'tasks': tasks,
        'skip': skip,
        'limit': limit,
        'has_prev': skip > 0,
        'has_next': len(tasks) == limit,
    }

    # Return partial for HTMX requests
    if request.headers.get('HX-Request'):
        return render(request, 'tasks/partials/task_table.html', context)

    return render(request, 'tasks/list.html', context)


def task_detail(request, task_id):
    """Display task details."""
    try:
        task = api_client.get_task(task_id)
    except APINotFoundError:
        messages.error(request, "Task not found")
        return redirect('tasks:list')
    except APIConnectionError:
        messages.error(request, "Cannot connect to backend API")
        return redirect('tasks:list')
    except APIError as e:
        messages.error(request, str(e))
        return redirect('tasks:list')

    return render(request, 'tasks/detail.html', {'task': task})


def task_create(request):
    """Create a new task."""
    if request.method == 'POST':
        form = TaskCreateForm(request.POST)
        if form.is_valid():
            try:
                data = {
                    'name': form.cleaned_data['name'],
                    'description': form.cleaned_data['description'],
                    'priority': form.cleaned_data['priority'],
                }
                if form.cleaned_data.get('input_json'):
                    data['input'] = json.loads(form.cleaned_data['input_json'])

                api_client.create_task(data)
                messages.success(request, "Task created successfully")

                # HTMX redirect
                if request.headers.get('HX-Request'):
                    response = HttpResponse()
                    response['HX-Redirect'] = '/tasks/'
                    return response

                return redirect('tasks:list')

            except APIConnectionError:
                messages.error(request, "Cannot connect to backend API")
            except APIError as e:
                messages.error(request, str(e))
            except json.JSONDecodeError:
                messages.error(request, "Invalid JSON in input field")
    else:
        form = TaskCreateForm()

    return render(request, 'tasks/create.html', {'form': form})


@require_http_methods(["POST"])
def task_execute(request, task_id):
    """Execute a task via the orchestrator."""
    try:
        task = api_client.execute_task(task_id)
        messages.success(request, f"Task '{task.get('name', task_id)}' executed successfully")

        # Return updated row for HTMX
        if request.headers.get('HX-Request'):
            return render(request, 'tasks/partials/task_row.html', {'task': task})

    except APINotFoundError:
        messages.error(request, "Task not found")
    except APIConnectionError:
        messages.error(request, "Cannot connect to backend API")
    except APIError as e:
        messages.error(request, str(e))

    if request.headers.get('HX-Request'):
        return HttpResponse(status=400)

    return redirect('tasks:detail', task_id=task_id)


@require_http_methods(["POST"])
def task_complete(request, task_id):
    """Mark a task as completed."""
    try:
        result = None
        if request.POST.get('result'):
            result = json.loads(request.POST['result'])

        task = api_client.complete_task(task_id, result)
        messages.success(request, f"Task '{task.get('name', task_id)}' marked as completed")

        # Return updated row for HTMX
        if request.headers.get('HX-Request'):
            return render(request, 'tasks/partials/task_row.html', {'task': task})

    except APINotFoundError:
        messages.error(request, "Task not found")
    except APIConnectionError:
        messages.error(request, "Cannot connect to backend API")
    except APIError as e:
        messages.error(request, str(e))

    if request.headers.get('HX-Request'):
        return HttpResponse(status=400)

    return redirect('tasks:detail', task_id=task_id)


@require_http_methods(["POST"])
def task_fail(request, task_id):
    """Mark a task as failed."""
    error_message = request.POST.get('error', 'Marked as failed by user')

    try:
        task = api_client.fail_task(task_id, error_message)
        messages.success(request, f"Task '{task.get('name', task_id)}' marked as failed")

        # Return updated row for HTMX
        if request.headers.get('HX-Request'):
            return render(request, 'tasks/partials/task_row.html', {'task': task})

    except APINotFoundError:
        messages.error(request, "Task not found")
    except APIConnectionError:
        messages.error(request, "Cannot connect to backend API")
    except APIError as e:
        messages.error(request, str(e))

    if request.headers.get('HX-Request'):
        return HttpResponse(status=400)

    return redirect('tasks:detail', task_id=task_id)
