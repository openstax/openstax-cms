# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('wagtailredirects', '0004_set_unique_on_path_and_site'),
        ('wagtailcore', '0020_add_index_on_page_first_published_at'),
        ('wagtailsearchpromotions', '0001_initial'),
        ('wagtailforms', '0002_add_verbose_names'),
        ('demo', '0009_auto_20151130_1840'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='bookindexpage',
            name='page_ptr',
        ),
        migrations.RemoveField(
            model_name='bookindexrelatedlink',
            name='link_document',
        ),
        migrations.RemoveField(
            model_name='bookindexrelatedlink',
            name='link_page',
        ),
        migrations.RemoveField(
            model_name='bookindexrelatedlink',
            name='page',
        ),
        migrations.RemoveField(
            model_name='bookpage',
            name='page_ptr',
        ),
        migrations.DeleteModel(
            name='BookIndexPage',
        ),
        migrations.DeleteModel(
            name='BookIndexRelatedLink',
        ),
        migrations.DeleteModel(
            name='BookPage',
        ),
    ]
