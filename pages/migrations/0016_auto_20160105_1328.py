# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('wagtailredirects', '0004_set_unique_on_path_and_site'),
        ('wagtailcore', '0020_add_index_on_page_first_published_at'),
        ('wagtailsearchpromotions', '0001_initial'),
        ('wagtailforms', '0002_add_verbose_names'),
        ('pages', '0015_auto_20160104_1443'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='bookdetail',
            name='page_ptr',
        ),
        migrations.RemoveField(
            model_name='books',
            name='page_ptr',
        ),
        migrations.AddField(
            model_name='highereducation',
            name='allies_heading',
            field=models.CharField(max_length=255, default=''),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='highereducation',
            name='ally_1_heading',
            field=models.CharField(max_length=255, default=''),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='highereducation',
            name='ally_2_heading',
            field=models.CharField(max_length=255, default=''),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='highereducation',
            name='ally_3_heading',
            field=models.CharField(max_length=255, default=''),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='highereducation',
            name='ally_4_heading',
            field=models.CharField(max_length=255, default=''),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='highereducation',
            name='ally_5_heading',
            field=models.CharField(max_length=255, default=''),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='highereducation',
            name='cnx_heading',
            field=models.CharField(max_length=255, default=''),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='highereducation',
            name='get_started_heading',
            field=models.CharField(max_length=255, default=''),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='highereducation',
            name='intro_heading',
            field=models.CharField(max_length=255, default=''),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='highereducation',
            name='our_books_heading',
            field=models.CharField(max_length=255, default=''),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='highereducation',
            name='our_impact_heading',
            field=models.CharField(max_length=255, default=''),
            preserve_default=False,
        ),
        migrations.DeleteModel(
            name='BookDetail',
        ),
        migrations.DeleteModel(
            name='Books',
        ),
    ]
