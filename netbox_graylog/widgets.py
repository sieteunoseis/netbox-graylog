"""Dashboard widgets for the NetBox Graylog plugin."""

import logging

from django import forms
from django.template.loader import render_to_string
from django.utils.translation import gettext as _
from extras.dashboard.utils import register_widget
from extras.dashboard.widgets import DashboardWidget, WidgetConfigForm

from .graylog_client import get_client

logger = logging.getLogger(__name__)


@register_widget
class GraylogSummaryWidget(DashboardWidget):
    """Dashboard widget showing log volume and error counts from Graylog."""

    default_title = _("Graylog Summary")
    description = _("Display log volume and error counts from Graylog.")
    template_name = "netbox_graylog/widgets/graylog_summary.html"
    width = 4
    height = 3

    class ConfigForm(WidgetConfigForm):
        time_range = forms.ChoiceField(
            choices=[
                (300, "5 minutes"),
                (900, "15 minutes"),
                (3600, "1 hour"),
                (14400, "4 hours"),
                (86400, "24 hours"),
            ],
            initial=3600,
            required=False,
            label=_("Time range"),
            help_text=_("Time window for log counts."),
        )
        cache_timeout = forms.IntegerField(
            min_value=30,
            max_value=3600,
            initial=120,
            required=False,
            label=_("Cache timeout (seconds)"),
            help_text=_("How long to cache log counts (30-3600 seconds)."),
        )

    def render(self, request):
        client = get_client()
        if not client:
            return render_to_string(
                self.template_name,
                {"error": "Graylog not configured. Set graylog_url and graylog_api_token in plugin settings."},
            )

        time_range = int(self.config.get("time_range", 3600))
        cache_timeout = self.config.get("cache_timeout", 120)
        summary = client.get_log_summary(time_range=time_range, cache_timeout=cache_timeout)

        if "error" in summary:
            return render_to_string(self.template_name, {"error": summary["error"]})

        # Format time range for display
        if time_range < 3600:
            time_label = f"{time_range // 60}m"
        elif time_range < 86400:
            time_label = f"{time_range // 3600}h"
        else:
            time_label = f"{time_range // 86400}d"

        return render_to_string(
            self.template_name,
            {
                "total": summary.get("total", 0),
                "errors": summary.get("errors", 0),
                "warnings": summary.get("warnings", 0),
                "time_label": time_label,
                "cached": summary.get("cached", False),
                "graylog_url": client.config.get("graylog_external_url") or client.base_url,
            },
        )
