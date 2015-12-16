# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import wagtail.wagtailcore.fields


class Migration(migrations.Migration):

    dependencies = [
        ('pages', '0009_homepage_page_header'),
    ]

    operations = [
        migrations.AddField(
            model_name='homepage',
            name='introduction',
            field=wagtail.wagtailcore.fields.RichTextField(default=''),
            preserve_default=False,
        ),
    ]
