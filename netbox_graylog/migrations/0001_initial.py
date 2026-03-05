from django.db import migrations


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="GraylogPermission",
            fields=[],
            options={
                "managed": False,
                "default_permissions": (),
                "permissions": (
                    ("configure_graylog", "Can configure Graylog plugin settings"),
                ),
            },
        ),
    ]
