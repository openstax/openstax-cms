# Generated by Django 5.0.7 on 2024-07-24 23:53

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("snippets", "0040_remove_pagelayout_background_image"),
    ]

    operations = [
        migrations.DeleteModel(
            name="PageLayout",
        ),
    ]