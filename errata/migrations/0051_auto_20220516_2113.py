# Generated by Django 3.2.5 on 2022-05-17 02:13

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('errata', '0050_auto_20220207_1057'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='errata',
            name='submitted_by',
        ),
        migrations.RemoveField(
            model_name='errata',
            name='submitter_email_address',
        ),
    ]