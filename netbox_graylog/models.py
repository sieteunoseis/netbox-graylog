from django.db import models


class Graylog(models.Model):
    """Unmanaged model to register custom permissions for the Graylog plugin."""

    class Meta:
        managed = False
        default_permissions = ()
        permissions = (
            ("configure_graylog", "Can configure Graylog plugin settings"),
        )
