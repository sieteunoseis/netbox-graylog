"""
NetBox Graylog Plugin

Display recent Graylog logs in Device and VirtualMachine detail pages.
"""

import logging

from netbox.plugins import PluginConfig

__version__ = "1.1.3"

logger = logging.getLogger(__name__)


class GraylogConfig(PluginConfig):
    """Plugin configuration for NetBox Graylog integration."""

    name = "netbox_graylog"
    verbose_name = "Graylog Logs"
    description = "Display recent Graylog logs in device and VM detail pages"
    version = __version__
    author = "sieteunoseis"
    author_email = "sieteunoseis@github.com"
    base_url = "graylog"
    min_version = "4.0.0"

    # Required settings - plugin won't load without these
    required_settings = []

    # Default configuration values
    default_settings = {
        "graylog_url": "http://graylog:9000",
        "graylog_api_token": "",
        "log_limit": 50,
        "time_range": 3600,  # 1 hour in seconds
        "timeout": 10,  # API timeout in seconds
        "cache_timeout": 60,  # Cache results for 60 seconds
        "search_field": "source",  # Field to search (source, gl2_remote_ip)
        "use_fqdn": True,  # Use FQDN for hostname matching
        "fallback_to_ip": True,  # Fall back to primary IP if hostname not found
    }

    def ready(self):
        """Register endpoint view if netbox_endpoints is available."""
        super().ready()
        self._register_endpoint_views()

    def _register_endpoint_views(self):
        """Register Graylog Logs tab for Endpoints if plugin is installed."""
        try:
            from django.shortcuts import render
            from netbox.views import generic
            from netbox_endpoints.models import Endpoint

            # Check if already registered
            from utilities.views import ViewTab, register_model_view, registry

            views_dict = registry.get("views", {})
            endpoint_views = views_dict.get("netbox_endpoints", {}).get("endpoint", [])
            if any(v.get("name") == "graylog_logs" for v in endpoint_views):
                return  # Already registered

            @register_model_view(Endpoint, name="graylog_logs", path="logs")
            class EndpointGraylogLogsView(generic.ObjectView):
                """Display Graylog logs for an Endpoint with async loading."""

                queryset = Endpoint.objects.all()
                template_name = "netbox_graylog/endpoint_logs_tab.html"

                tab = ViewTab(
                    label="Logs",
                    weight=9000,
                    permission="netbox_endpoints.view_endpoint",
                    hide_if_empty=False,
                )

                def get(self, request, pk):
                    endpoint = Endpoint.objects.get(pk=pk)
                    time_range = request.GET.get("range", "")
                    return render(
                        request,
                        self.template_name,
                        {
                            "object": endpoint,
                            "tab": self.tab,
                            "loading": True,
                            "time_range_param": time_range,
                        },
                    )

            logger.info("Registered Graylog Logs tab for Endpoint model")
        except ImportError:
            logger.debug("netbox_endpoints not installed, skipping endpoint view registration")
        except Exception as e:
            logger.warning(f"Could not register endpoint views: {e}")


config = GraylogConfig
