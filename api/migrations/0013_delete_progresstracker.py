# Generated by Django 5.0.12 on 2025-02-22 00:27

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("api", "0012_alter_webviewsettings_options"),
    ]

    operations = [
        migrations.DeleteModel(
            name="ProgressTracker",
        ),
    ]
