# Generated by Django 4.1.7 on 2023-12-13 19:28

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("salesforce", "0105_auto_20221212_1543"),
    ]

    operations = [
        migrations.RemoveIndex(
            model_name="resourcedownload",
            name="salesforce__account_b11d37_idx",
        ),
        migrations.RemoveField(
            model_name="resourcedownload",
            name="account_id",
        ),
    ]
