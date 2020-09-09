# Generated by Django 3.0.4 on 2020-08-10 18:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('global_settings', '0018_auto_20200727_1047'),
    ]

    operations = [
        migrations.AddField(
            model_name='stickynote',
            name='show_popup',
            field=models.BooleanField(default=False, help_text='Replaces the top banner with a popup, start and expire dates still control timing.'),
        ),
    ]