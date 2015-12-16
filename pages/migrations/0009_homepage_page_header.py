# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pages', '0008_homepage_intro_image'),
    ]

    operations = [
        migrations.AddField(
            model_name='homepage',
            name='page_header',
            field=models.CharField(max_length=255, default='test'),
            preserve_default=False,
        ),
    ]
