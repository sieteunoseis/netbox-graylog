"""
Views for NetBox Graylog Plugin

Registers custom tabs on Device and VirtualMachine detail views.
Provides settings configuration UI.
"""

from django.conf import settings
from django.contrib import messages
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.views import View
from django.views.generic import FormView

from dcim.models import Device
from virtualization.models import VirtualMachine
from netbox.views import generic
from utilities.views import ViewTab, register_model_view

from .forms import GraylogSettingsForm
from .graylog_client import get_client, GraylogClient


@register_model_view(Device, name="graylog_logs", path="logs")
class DeviceGraylogLogsView(generic.ObjectView):
    """Display Graylog logs for a Device."""

    queryset = Device.objects.all()
    template_name = "netbox_graylog/logs_tab.html"

    tab = ViewTab(
        label="Logs",
        weight=9000,
        permission="dcim.view_device",
        hide_if_empty=False,
    )

    def get(self, request, pk):
        """Handle GET request for the logs tab."""
        device = self.get_object()

        # Get time range from query params (default to config value)
        time_range = request.GET.get("range", None)
        if time_range:
            try:
                time_range = int(time_range)
            except ValueError:
                time_range = None

        # Fetch logs from Graylog
        client = get_client()
        if time_range:
            logs_data = client.search_logs(
                f"source:{device.name}",
                time_range=time_range,
            )
        else:
            logs_data = client.get_logs_for_device(device)

        return render(
            request,
            self.template_name,
            {
                "object": device,
                "tab": self.tab,
                "logs": logs_data.get("messages", []),
                "error": logs_data.get("error"),
                "total_results": logs_data.get("total_results", 0),
                "query": logs_data.get("query", ""),
                "time_range": logs_data.get("time_range", 3600),
                "search_type": logs_data.get("search_type", "hostname"),
            },
        )


@register_model_view(VirtualMachine, name="graylog_logs", path="logs")
class VirtualMachineGraylogLogsView(generic.ObjectView):
    """Display Graylog logs for a VirtualMachine."""

    queryset = VirtualMachine.objects.all()
    template_name = "netbox_graylog/logs_tab.html"

    tab = ViewTab(
        label="Logs",
        weight=9000,
        permission="virtualization.view_virtualmachine",
        hide_if_empty=False,
    )

    def get(self, request, pk):
        """Handle GET request for the logs tab."""
        vm = self.get_object()

        # Get time range from query params
        time_range = request.GET.get("range", None)
        if time_range:
            try:
                time_range = int(time_range)
            except ValueError:
                time_range = None

        # Fetch logs from Graylog
        client = get_client()
        if time_range:
            logs_data = client.search_logs(
                f"source:{vm.name}",
                time_range=time_range,
            )
        else:
            logs_data = client.get_logs_for_vm(vm)

        return render(
            request,
            self.template_name,
            {
                "object": vm,
                "tab": self.tab,
                "logs": logs_data.get("messages", []),
                "error": logs_data.get("error"),
                "total_results": logs_data.get("total_results", 0),
                "query": logs_data.get("query", ""),
                "time_range": logs_data.get("time_range", 3600),
                "search_type": logs_data.get("search_type", "hostname"),
            },
        )


class GraylogSettingsView(View):
    """View for configuring Graylog plugin settings."""

    template_name = "netbox_graylog/settings.html"

    def get_current_config(self):
        """Get current plugin configuration."""
        return settings.PLUGINS_CONFIG.get("netbox_graylog", {})

    def get(self, request):
        """Display the settings form."""
        config = self.get_current_config()
        form = GraylogSettingsForm(initial=config)

        return render(
            request,
            self.template_name,
            {
                "form": form,
                "config": config,
            },
        )

    def post(self, request):
        """Handle settings form submission."""
        form = GraylogSettingsForm(request.POST)

        if form.is_valid():
            # Note: Settings are read-only at runtime in NetBox
            # Users must update configuration.py manually
            # This view shows current settings and validates test connections
            messages.warning(
                request,
                "Settings must be configured in NetBox's configuration.py file. "
                "See the README for configuration instructions.",
            )
        else:
            messages.error(request, "Invalid settings provided.")

        return render(
            request,
            self.template_name,
            {
                "form": form,
                "config": self.get_current_config(),
            },
        )


class TestConnectionView(View):
    """Test connection to Graylog API."""

    def post(self, request):
        """Test the Graylog connection and return result."""
        client = get_client()

        # Try a simple search to verify connectivity
        result = client.search_logs("*", time_range=60, limit=1)

        if result.get("error"):
            return JsonResponse(
                {
                    "success": False,
                    "error": result["error"],
                },
                status=400,
            )

        return JsonResponse(
            {
                "success": True,
                "message": f"Connected successfully. Found {result.get('total_results', 0)} messages in last minute.",
            }
        )
