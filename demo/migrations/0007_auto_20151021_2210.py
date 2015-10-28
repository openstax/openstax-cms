# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import wagtail.wagtailcore.fields
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('wagtailimages', '0008_image_created_at_index'),
        ('wagtailredirects', '0002_add_verbose_names'),
        ('wagtailforms', '0002_add_verbose_names'),
        ('wagtailcore', '0019_verbose_names_cleanup'),
        ('wagtailsearchpromotions', '0001_initial'),
        ('demo', '0006_bookindexrelatedlink'),
    ]

    operations = [
        migrations.CreateModel(
            name='BookPage',
            fields=[
                ('page_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='wagtailcore.Page')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('name', models.CharField(max_length=255)),
                ('revision', models.CharField(max_length=255, null=True, blank=True)),
                ('description', wagtail.wagtailcore.fields.RichTextField(blank=True)),
                ('publish_date', models.DateField(null=True, blank=True)),
                ('isbn_10', models.IntegerField(null=True, blank=True)),
                ('isbn_13', models.CharField(max_length=255, null=True, blank=True)),
                ('cover_image', models.ForeignKey(related_name='+', on_delete=django.db.models.deletion.SET_NULL, blank=True, to='wagtailimages.Image', null=True)),
            ],
            options={
                'abstract': False,
            },
            bases=('wagtailcore.page',),
        ),
        migrations.RemoveField(
            model_name='book',
            name='cover_image',
        ),
        migrations.RemoveField(
            model_name='book',
            name='page_ptr',
        ),
        migrations.DeleteModel(
            name='Book',
        ),
    ]
