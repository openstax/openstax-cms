# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pages', '0023_merge'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='homepagerelatedlink',
            name='link_document',
        ),
        migrations.RemoveField(
            model_name='homepagerelatedlink',
            name='link_page',
        ),
        migrations.RemoveField(
            model_name='homepagerelatedlink',
            name='page',
        ),
        migrations.RemoveField(
            model_name='homepage',
            name='wwd_12',
        ),
        migrations.DeleteModel(
            name='HomePageRelatedLink',
        ),
    ]
