# -*- coding: utf-8 -*-
# Generated by Django 1.9.5 on 2016-04-07 16:45
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('wagtailimages', '0012_copy_image_permissions_to_collections'),
        ('allies', '0007_auto_20160330_1021'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='ally',
            name='logo',
        ),
        migrations.AddField(
            model_name='ally',
            name='logo_bw',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='logo_bw', to='wagtailimages.Image'),
        ),
        migrations.AddField(
            model_name='ally',
            name='logo_color',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='logo_color', to='wagtailimages.Image'),
        ),
    ]
