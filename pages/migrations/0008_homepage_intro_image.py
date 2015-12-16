# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('wagtailimages', '0008_image_created_at_index'),
        ('pages', '0007_auto_20151216_1150'),
    ]

    operations = [
        migrations.AddField(
            model_name='homepage',
            name='intro_image',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='wagtailimages.Image', related_name='+', blank=True),
        ),
    ]
