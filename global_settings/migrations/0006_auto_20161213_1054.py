# -*- coding: utf-8 -*-
# Generated by Django 1.10.2 on 2016-12-13 16:54
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('global_settings', '0005_remove_stickynote_header'),
    ]

    operations = [
        migrations.AddField(
            model_name='stickynote',
            name='emergency_content',
            field=models.CharField(default='', max_length=255),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='stickynote',
            name='emergency_expires',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
