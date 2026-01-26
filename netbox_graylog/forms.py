"""
Forms for NetBox Graylog Plugin settings.
"""

from django import forms


class GraylogSettingsForm(forms.Form):
    """Form for configuring Graylog plugin settings."""

    graylog_url = forms.URLField(
        label="Graylog URL",
        help_text="Base URL for Graylog API (e.g., http://graylog:9000)",
        required=True,
        widget=forms.URLInput(
            attrs={"class": "form-control", "placeholder": "http://graylog:9000"}
        ),
    )

    graylog_api_token = forms.CharField(
        label="API Token",
        help_text="Graylog API token for authentication",
        required=True,
        widget=forms.PasswordInput(
            attrs={"class": "form-control", "placeholder": "Enter API token"},
            render_value=True,
        ),
    )

    log_limit = forms.IntegerField(
        label="Log Limit",
        help_text="Maximum number of logs to display per request",
        required=False,
        initial=50,
        min_value=10,
        max_value=500,
        widget=forms.NumberInput(attrs={"class": "form-control"}),
    )

    time_range = forms.ChoiceField(
        label="Default Time Range",
        help_text="Default time range for log queries",
        choices=[
            (300, "5 minutes"),
            (900, "15 minutes"),
            (3600, "1 hour"),
            (14400, "4 hours"),
            (86400, "24 hours"),
            (604800, "7 days"),
        ],
        initial=3600,
        widget=forms.Select(attrs={"class": "form-control"}),
    )

    timeout = forms.IntegerField(
        label="API Timeout",
        help_text="Timeout for Graylog API requests (seconds)",
        required=False,
        initial=10,
        min_value=5,
        max_value=60,
        widget=forms.NumberInput(attrs={"class": "form-control"}),
    )

    cache_timeout = forms.IntegerField(
        label="Cache Timeout",
        help_text="How long to cache API responses (seconds)",
        required=False,
        initial=60,
        min_value=0,
        max_value=300,
        widget=forms.NumberInput(attrs={"class": "form-control"}),
    )

    search_field = forms.ChoiceField(
        label="Search Field",
        help_text="Graylog field to search for device name",
        choices=[
            ("source", "source (hostname)"),
            ("gl2_remote_ip", "gl2_remote_ip (IP address)"),
        ],
        initial="source",
        widget=forms.Select(attrs={"class": "form-control"}),
    )

    use_fqdn = forms.BooleanField(
        label="Use FQDN",
        help_text="Use fully qualified domain name for searches",
        required=False,
        initial=True,
        widget=forms.CheckboxInput(attrs={"class": "form-check-input"}),
    )

    fallback_to_ip = forms.BooleanField(
        label="Fallback to IP",
        help_text="Try searching by primary IP if hostname search fails",
        required=False,
        initial=True,
        widget=forms.CheckboxInput(attrs={"class": "form-check-input"}),
    )
