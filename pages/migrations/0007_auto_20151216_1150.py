# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('wagtailcore', '0020_add_index_on_page_first_published_at'),
        ('wagtailsearchpromotions', '0001_initial'),
        ('wagtailforms', '0002_add_verbose_names'),
        ('wagtailredirects', '0004_set_unique_on_path_and_site'),
        ('pages', '0006_auto_20151210_1407'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='standardpage',
            name='page_ptr',
        ),
        migrations.AlterModelOptions(
            name='homepage',
            options={'verbose_name': 'Home Page'},
        ),
        migrations.RemoveField(
            model_name='homepage',
            name='body',
        ),
        migrations.DeleteModel(
            name='StandardPage',
        ),
    ]
