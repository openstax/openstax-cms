# -*- coding: utf-8 -*-
# Generated by Django 1.10.1 on 2016-09-23 15:11
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('global_settings', '0004_auto_20160906_1403'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='stickynote',
            name='header',
        ),
    ]
