# -*- coding: utf-8 -*-
# Generated by Django 1.9.2 on 2016-02-22 19:59
from __future__ import unicode_literals

from django.db import migrations
import wagtail.fields


class Migration(migrations.Migration):

    dependencies = [
        ('allies', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='ally',
            old_name='description',
            new_name='short_description',
        ),
        migrations.AddField(
            model_name='ally',
            name='long_description',
            field=wagtail.fields.RichTextField(default=''),
            preserve_default=False,
        ),
    ]
