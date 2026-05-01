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
    skip = int(request.GET.get("skip", 0))
    limit = int(request.GET.get("limit", 20))

    try:
        tasks = api_client.list_tasks(skip=skip, limit=limit)
    except APIConnectionError:
        messages.error(request, "Cannot connect to backend API")
        tasks = []
    except APIError as e:
        messages.error(request, str(e))
        tasks = []

    context = {
        "tasks": tasks,
        "skip": skip,
        "limit": limit,
        "has_prev": skip > 0,
        "has_next": len(tasks) == limit,
    }

    if request.headers.get("HX-Request"):
        return render(request, "tasks/partials/task_table.html", context)

    return render(request, "tasks/list.html", context)


def task_detail(request, task_id):
    """Display task details."""
    try:
        task = api_client.get_task(task_id)
    except APINotFoundError:
        messages.error(request, "Task not found")
        return redirect("tasks:list")
    except APIConnectionError:
        messages.error(request, "Cannot connect to backend API")
        return redirect("tasks:list")
    except APIError as e:
        messages.error(request, str(e))
        return redirect("tasks:list")

    # 🔥 FORCE CSRF COOKIE CREATION
    from django.middleware.csrf import get_token
    get_token(request)

    return render(request, "tasks/detail.html", {"task": task})


def task_create(request):
    """Create a new task."""
    form = TaskCreateForm(request.POST or None)

    if request.method == "POST":
        if form.is_valid():
            try:
                data = {
                    "name": form.cleaned_data["name"],
                    "description": form.cleaned_data["description"],
                    "priority": form.cleaned_data["priority"],
                    "input": {},
                }

                raw_input = form.cleaned_data.get("input_json")

                if raw_input:
                    try:
                        parsed = json.loads(raw_input)
                        if isinstance(parsed, dict):
                            data["input"] = parsed
                        else:
                            messages.error(request, "Input JSON must be an object")
                            return render(request, "tasks/create.html", {"form": form})
                    except json.JSONDecodeError:
                        messages.error(request, "Invalid JSON format")
                        return render(request, "tasks/create.html", {"form": form})

                api_client.create_task(data)

                messages.success(request, "Task created successfully")

                if request.headers.get("HX-Request"):
                    response = HttpResponse()
                    response["HX-Redirect"] = "/tasks/"
                    return response

                return redirect("tasks:list")

            except APIConnectionError:
                messages.error(request, "Cannot connect to backend API")
            except APIError as e:
                messages.error(request, str(e))

    return render(request, "tasks/create.html", {"form": form})


@require_http_methods(["POST"])
def task_execute(request, task_id):
    """Execute a task."""
    try:
        task = api_client.execute_task(task_id)

        messages.success(request, f"Task '{task.get('name', task_id)}' executed")

        if request.headers.get("HX-Request"):
            return render(request, "tasks/partials/task_row.html", {"task": task})

    except APINotFoundError:
        messages.error(request, "Task not found")
    except APIConnectionError:
        messages.error(request, "Cannot connect to backend API")
    except APIError as e:
        messages.error(request, str(e))

    if request.headers.get("HX-Request"):
        return HttpResponse(status=400)

    return redirect("tasks:detail", task_id=task_id)


@require_http_methods(["POST"])
def task_complete(request, task_id):
    """Mark task as completed."""
    try:
        result = {}

        raw_result = request.POST.get("result")
        if raw_result:
            try:
                parsed = json.loads(raw_result)
                if isinstance(parsed, dict):
                    result = parsed
            except json.JSONDecodeError:
                messages.error(request, "Invalid JSON in result")
                return redirect("tasks:detail", task_id=task_id)

        task = api_client.complete_task(task_id, result)

        messages.success(request, f"Task '{task.get('name', task_id)}' completed")

        if request.headers.get("HX-Request"):
            return render(request, "tasks/partials/task_row.html", {"task": task})

    except APINotFoundError:
        messages.error(request, "Task not found")
    except APIConnectionError:
        messages.error(request, "Cannot connect to backend API")
    except APIError as e:
        messages.error(request, str(e))

    if request.headers.get("HX-Request"):
        return HttpResponse(status=400)

    return redirect("tasks:detail", task_id=task_id)


@require_http_methods(["POST"])
def task_fail(request, task_id):
    """Mark task as failed."""
    error_message = request.POST.get("error") or "Marked as failed"

    try:
        task = api_client.fail_task(task_id, error_message)

        messages.success(request, f"Task '{task.get('name', task_id)}' failed")

        if request.headers.get("HX-Request"):
            return render(request, "tasks/partials/task_row.html", {"task": task})

    except APINotFoundError:
        messages.error(request, "Task not found")
    except APIConnectionError:
        messages.error(request, "Cannot connect to backend API")
    except APIError as e:
        messages.error(request, str(e))

    if request.headers.get("HX-Request"):
        return HttpResponse(status=400)

    return redirect("tasks:detail", task_id=task_id)