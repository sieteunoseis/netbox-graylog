"""
NetBox Graylog Plugin

Display recent Graylog logs in Device and VirtualMachine detail pages.
"""

from netbox.plugins import PluginConfig

__version__ = "1.1.0"


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


config = GraylogConfig
