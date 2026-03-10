"""
Tool views for the Django frontend.
"""

from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import HttpResponse

from core.api_client import api_client
from core.exceptions import APIError, APIConnectionError, APINotFoundError

from .forms import ToolRegisterForm


def tool_list(request):
    """Display list of all registered tools."""
    try:
        tools = api_client.list_tools()
    except APIConnectionError:
        messages.error(request, "Cannot connect to backend API")
        tools = []
    except APIError as e:
        messages.error(request, str(e))
        tools = []

    # Return partial for HTMX requests
    if request.headers.get('HX-Request'):
        return render(request, 'tools/partials/tool_table.html', {'tools': tools})

    return render(request, 'tools/list.html', {'tools': tools})


def tool_detail(request, tool_id):
    """Display tool details."""
    try:
        tool = api_client.get_tool(tool_id)
    except APINotFoundError:
        messages.error(request, "Tool not found")
        return redirect('tools:list')
    except APIConnectionError:
        messages.error(request, "Cannot connect to backend API")
        return redirect('tools:list')
    except APIError as e:
        messages.error(request, str(e))
        return redirect('tools:list')

    return render(request, 'tools/detail.html', {'tool': tool})


def tool_register(request):
    """Register a new tool."""
    if request.method == 'POST':
        form = ToolRegisterForm(request.POST)
        if form.is_valid():
            try:
                data = {
                    'tool_id': form.cleaned_data['tool_id'],
                    'name': form.cleaned_data['name'],
                    'version': form.cleaned_data['version'],
                    'description': form.cleaned_data['description'],
                }

                api_client.register_tool(data)
                messages.success(request, "Tool registered successfully")

                # HTMX redirect
                if request.headers.get('HX-Request'):
                    response = HttpResponse()
                    response['HX-Redirect'] = '/tools/'
                    return response

                return redirect('tools:list')

            except APIConnectionError:
                messages.error(request, "Cannot connect to backend API")
            except APIError as e:
                messages.error(request, str(e))
    else:
        form = ToolRegisterForm()

    return render(request, 'tools/register.html', {'form': form})
