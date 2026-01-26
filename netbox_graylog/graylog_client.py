"""
Graylog API Client

Handles communication with Graylog's REST API for log retrieval.
"""

import logging

import requests
from django.conf import settings
from django.core.cache import cache

logger = logging.getLogger(__name__)


class GraylogClient:
    """Client for interacting with Graylog API."""

    def __init__(self):
        """Initialize the Graylog client with plugin configuration."""
        self.config = settings.PLUGINS_CONFIG.get("netbox_graylog", {})
        self.base_url = self.config.get("graylog_url", "http://graylog:9000")
        self.api_token = self.config.get("graylog_api_token", "")
        self.timeout = self.config.get("timeout", 10)
        self.cache_timeout = self.config.get("cache_timeout", 60)

    def _get_auth(self):
        """Get authentication tuple for requests."""
        # Graylog uses token:token for API token auth
        return (self.api_token, "token")

    def _get_headers(self):
        """Get default headers for API requests."""
        return {
            "Accept": "application/json",
            "X-Requested-By": "NetBox-Graylog-Plugin",
        }

    def search_logs(self, query, time_range=None, limit=None, fields=None):
        """
        Search for logs in Graylog.

        Args:
            query: Lucene query string (e.g., "source:hostname")
            time_range: Time range in seconds (default from config)
            limit: Maximum number of results (default from config)
            fields: List of fields to return (optional)

        Returns:
            dict with 'messages' list or 'error' string
        """
        if not self.api_token:
            return {"error": "Graylog API token not configured", "messages": []}

        time_range = time_range or self.config.get("time_range", 3600)
        limit = limit or self.config.get("log_limit", 50)

        # Check cache first
        cache_key = f"graylog_logs_{query}_{time_range}_{limit}"
        cached = cache.get(cache_key)
        if cached is not None:
            logger.debug(f"Returning cached results for query: {query}")
            return cached

        endpoint = f"{self.base_url}/api/search/universal/relative"

        params = {
            "query": query,
            "range": time_range,
            "limit": limit,
            "sort": "timestamp:desc",
        }

        if fields:
            params["fields"] = ",".join(fields)

        try:
            response = requests.get(
                endpoint,
                params=params,
                headers=self._get_headers(),
                auth=self._get_auth(),
                timeout=self.timeout,
                verify=False,  # Allow self-signed certs
            )
            response.raise_for_status()

            data = response.json()
            result = {
                "messages": data.get("messages", []),
                "total_results": data.get("total_results", 0),
                "time": data.get("time", 0),
                "query": query,
                "time_range": time_range,
            }

            # Cache the results
            cache.set(cache_key, result, self.cache_timeout)

            return result

        except requests.exceptions.Timeout:
            logger.error(f"Timeout connecting to Graylog: {self.base_url}")
            return {"error": "Connection timeout", "messages": []}
        except requests.exceptions.ConnectionError as e:
            logger.error(f"Connection error to Graylog: {e}")
            return {"error": f"Connection failed: {self.base_url}", "messages": []}
        except requests.exceptions.HTTPError as e:
            logger.error(f"HTTP error from Graylog: {e}")
            if e.response.status_code == 401:
                return {
                    "error": "Authentication failed - check API token",
                    "messages": [],
                }
            elif e.response.status_code == 403:
                return {
                    "error": "Permission denied - check token permissions",
                    "messages": [],
                }
            return {"error": f"HTTP error: {e.response.status_code}", "messages": []}
        except Exception as e:
            logger.exception(f"Unexpected error querying Graylog: {e}")
            return {"error": str(e), "messages": []}

    def get_logs_for_device(self, device):
        """
        Get logs for a NetBox device.

        Attempts to find logs by:
        1. Device name (FQDN or shortname) - case-insensitive regex match
        2. Primary IP address (if fallback enabled)

        For virtual chassis members, uses the chassis name (original hostname)
        instead of the member-specific name (e.g., "switch" instead of "switch.2").

        Args:
            device: NetBox Device object

        Returns:
            dict with 'messages' list or 'error' string
        """
        search_field = self.config.get("search_field", "source")
        use_fqdn = self.config.get("use_fqdn", True)
        fallback_to_ip = self.config.get("fallback_to_ip", True)

        # Build search term from device name
        # Use VC name for virtual chassis members (original hostname)
        hostname = (
            device.virtual_chassis.name if device.virtual_chassis else device.name
        )
        if not use_fqdn and "." in hostname:
            hostname = hostname.split(".")[0]

        # Build query - hostname with optional IP fallback using OR
        hostname_query = f"{search_field}:{hostname}*"

        if fallback_to_ip and device.primary_ip4:
            ip = str(device.primary_ip4.address).split("/")[0]
            # Combine hostname and IP queries with OR for single search
            query = f"({hostname_query} OR gl2_remote_ip:{ip} OR source:{ip})"
        else:
            query = hostname_query

        result = self.search_logs(query)
        result["search_type"] = "combined" if " OR " in query else "hostname"
        result["device_name"] = device.name
        return result

    def get_logs_for_vm(self, vm):
        """
        Get logs for a NetBox VirtualMachine.

        Args:
            vm: NetBox VirtualMachine object

        Returns:
            dict with 'messages' list or 'error' string
        """
        search_field = self.config.get("search_field", "source")
        use_fqdn = self.config.get("use_fqdn", True)
        fallback_to_ip = self.config.get("fallback_to_ip", True)

        # Build search term from VM name
        hostname = vm.name
        if not use_fqdn and "." in hostname:
            hostname = hostname.split(".")[0]

        # Try hostname first - use wildcard for matching (Graylog wildcards are case-insensitive)
        # Append * to match FQDN variations (e.g., admagw01 matches ADMagw01.ohsu.edu)
        query = f"{search_field}:{hostname}*"
        result = self.search_logs(query)

        # If no results and fallback enabled, try primary IP
        if (
            fallback_to_ip
            and not result.get("messages")
            and not result.get("error")
            and vm.primary_ip4
        ):
            ip = str(vm.primary_ip4.address).split("/")[0]
            query = f"gl2_remote_ip:{ip}"
            result = self.search_logs(query)
            if result.get("messages"):
                result["search_type"] = "ip"
            else:
                query = f"source:{ip}"
                result = self.search_logs(query)
                if result.get("messages"):
                    result["search_type"] = "source_ip"
        else:
            result["search_type"] = "hostname"

        result["vm_name"] = vm.name
        return result


# Singleton instance
_client = None


def get_client():
    """Get or create the Graylog client singleton."""
    global _client
    if _client is None:
        _client = GraylogClient()
    return _client
