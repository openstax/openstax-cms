# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion
import wagtail.wagtailcore.fields


class Migration(migrations.Migration):

    dependencies = [
        ('wagtailcore', '0020_add_index_on_page_first_published_at'),
        ('wagtailimages', '0008_image_created_at_index'),
        ('pages', '0002_auto_20151209_1510'),
    ]

    operations = [
        migrations.CreateModel(
            name='StandardPage',
            fields=[
                ('page_ptr', models.OneToOneField(parent_link=True, serialize=False, to='wagtailcore.Page', auto_created=True, primary_key=True)),
                ('body', wagtail.wagtailcore.fields.RichTextField()),
                ('carousel_item_one', models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, blank=True, to='wagtailimages.Image', related_name='+', null=True)),
                ('carousel_item_three', models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, blank=True, to='wagtailimages.Image', related_name='+', null=True)),
                ('carousel_item_two', models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, blank=True, to='wagtailimages.Image', related_name='+', null=True)),
            ],
            options={
                'abstract': False,
            },
            bases=('wagtailcore.page',),
        ),
    ]
