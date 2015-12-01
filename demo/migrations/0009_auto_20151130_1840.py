# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('demo', '0008_auto_20151022_1823'),
    ]

    operations = [
        migrations.AlterField(
            model_name='bookindexrelatedlink',
            name='link_external',
            field=models.URLField(blank=True, verbose_name='External link'),
        ),
        migrations.AlterField(
            model_name='bookindexrelatedlink',
            name='title',
            field=models.CharField(max_length=255, help_text='Link title'),
        ),
    ]
