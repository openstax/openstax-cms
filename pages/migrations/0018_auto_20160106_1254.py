# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('wagtailforms', '0002_add_verbose_names'),
        ('wagtailsearchpromotions', '0001_initial'),
        ('wagtailredirects', '0004_set_unique_on_path_and_site'),
        ('wagtailcore', '0020_add_index_on_page_first_published_at'),
        ('pages', '0017_auto_20160105_1605'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='news',
            name='page_ptr',
        ),
        migrations.RemoveField(
            model_name='newsarticle',
            name='page_ptr',
        ),
        migrations.DeleteModel(
            name='News',
        ),
        migrations.DeleteModel(
            name='NewsArticle',
        ),
    ]
