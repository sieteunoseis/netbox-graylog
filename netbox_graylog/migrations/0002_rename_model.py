from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("netbox_graylog", "0001_initial"),
    ]

    operations = [
        migrations.RenameModel(
            old_name="GraylogPermission",
            new_name="Graylog",
        ),
    ]
