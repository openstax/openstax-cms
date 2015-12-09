# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion
import wagtail.wagtailcore.fields


class Migration(migrations.Migration):

    dependencies = [
        ('wagtailimages', '0008_image_created_at_index'),
        ('wagtailcore', '0020_add_index_on_page_first_published_at'),
    ]

    operations = [
        migrations.CreateModel(
            name='Book',
            fields=[
                ('page_ptr', models.OneToOneField(parent_link=True, auto_created=True, serialize=False, primary_key=True, to='wagtailcore.Page')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('name', models.CharField(max_length=255)),
                ('revision', models.CharField(null=True, max_length=255, blank=True)),
                ('description', wagtail.wagtailcore.fields.RichTextField(blank=True)),
                ('publish_date', models.DateField(null=True, blank=True)),
                ('isbn_10', models.IntegerField(null=True, blank=True)),
                ('isbn_13', models.CharField(null=True, max_length=255, blank=True)),
                ('cover_image', models.ForeignKey(null=True, blank=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='wagtailimages.Image')),
            ],
            options={
                'abstract': False,
            },
            bases=('wagtailcore.page',),
        ),
    ]
