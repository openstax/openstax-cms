# -*- coding: utf-8 -*-
# Generated by Django 1.9.1 on 2016-03-25 21:24
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('allies', '0005_auto_20160307_1432'),
    ]

    operations = [
        migrations.AddField(
            model_name='ally',
            name='is_ap',
            field=models.BooleanField(default=False),
        ),
    ]
