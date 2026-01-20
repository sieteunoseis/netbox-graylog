"""
Views for NetBox Graylog Plugin

Registers custom tabs on Device and VirtualMachine detail views.
"""

from dcim.models import Device
from virtualization.models import VirtualMachine
from netbox.views import generic
from utilities.views import ViewTab, register_model_view
from django.shortcuts import render

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
