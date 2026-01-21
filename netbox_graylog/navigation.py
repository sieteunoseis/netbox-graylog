"""
Navigation menu items for NetBox Graylog Plugin.
"""

from netbox.plugins import PluginMenu, PluginMenuItem

menu = PluginMenu(
    label="Graylog",
    groups=(
        (
            "Settings",
            (
                PluginMenuItem(
                    link="plugins:netbox_graylog:settings",
                    link_text="Configuration",
                    permissions=["netbox_graylog.configure_graylog"],
                ),
            ),
        ),
    ),
    icon_class="mdi mdi-file-document-outline",
)
