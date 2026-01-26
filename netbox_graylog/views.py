"""
Views for NetBox Graylog Plugin

Registers custom tabs on Device and VirtualMachine detail views.
Provides settings configuration UI.
"""

from dcim.models import Device
from django.conf import settings
from django.contrib import messages
from django.http import JsonResponse
from django.shortcuts import render
from django.views import View
from netbox.views import generic
from utilities.views import ViewTab, register_model_view
from virtualization.models import VirtualMachine

from .forms import GraylogSettingsForm
from .graylog_client import get_client


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
        device = Device.objects.get(pk=pk)

        # Get time range from query params (default to config value)
        time_range = request.GET.get("range", None)
        if time_range:
            try:
                time_range = int(time_range)
            except ValueError:
                time_range = None

        # Fetch logs from Graylog
        client = get_client()
        config = settings.PLUGINS_CONFIG.get("netbox_graylog", {})

        if time_range:
            # Build query with wildcard (Graylog wildcards are case-insensitive)
            # Use VC name for virtual chassis members (original hostname)
            hostname = (
                device.virtual_chassis.name if device.virtual_chassis else device.name
            )
            query = f"source:{hostname}*"
            logs_data = client.search_logs(query, time_range=time_range)
            logs_data["search_type"] = "hostname"
        else:
            logs_data = client.get_logs_for_device(device)

        # Get external Graylog URL for browser links
        graylog_base_url = config.get(
            "graylog_external_url", config.get("graylog_url", "")
        ).rstrip("/")

        # Transform logs to rename _id to message_id (Django templates can't access underscore-prefixed attrs)
        logs = []
        for log in logs_data.get("messages", []):
            transformed = {
                "index": log.get("index", ""),
                "message": {
                    **log.get("message", {}),
                    "message_id": log.get("message", {}).get("_id", ""),
                },
            }
            logs.append(transformed)

        return render(
            request,
            self.template_name,
            {
                "object": device,
                "tab": self.tab,
                "logs": logs,
                "error": logs_data.get("error"),
                "total_results": logs_data.get("total_results", 0),
                "query": logs_data.get("query", ""),
                "time_range": logs_data.get("time_range", 3600),
                "search_type": logs_data.get("search_type", "hostname"),
                "graylog_base_url": graylog_base_url,
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
        vm = VirtualMachine.objects.get(pk=pk)

        # Get time range from query params
        time_range = request.GET.get("range", None)
        if time_range:
            try:
                time_range = int(time_range)
            except ValueError:
                time_range = None

        # Fetch logs from Graylog
        client = get_client()
        config = settings.PLUGINS_CONFIG.get("netbox_graylog", {})

        if time_range:
            # Build query with wildcard (Graylog wildcards are case-insensitive)
            hostname = vm.name
            query = f"source:{hostname}*"
            logs_data = client.search_logs(query, time_range=time_range)
            logs_data["search_type"] = "hostname"
        else:
            logs_data = client.get_logs_for_vm(vm)

        # Get external Graylog URL for browser links
        graylog_base_url = config.get(
            "graylog_external_url", config.get("graylog_url", "")
        ).rstrip("/")

        # Transform logs to rename _id to message_id (Django templates can't access underscore-prefixed attrs)
        logs = []
        for log in logs_data.get("messages", []):
            transformed = {
                "index": log.get("index", ""),
                "message": {
                    **log.get("message", {}),
                    "message_id": log.get("message", {}).get("_id", ""),
                },
            }
            logs.append(transformed)

        return render(
            request,
            self.template_name,
            {
                "object": vm,
                "tab": self.tab,
                "logs": logs,
                "error": logs_data.get("error"),
                "total_results": logs_data.get("total_results", 0),
                "query": logs_data.get("query", ""),
                "time_range": logs_data.get("time_range", 3600),
                "search_type": logs_data.get("search_type", "hostname"),
                "graylog_base_url": graylog_base_url,
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
