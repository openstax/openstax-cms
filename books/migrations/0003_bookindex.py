# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import wagtail.wagtailcore.fields


class Migration(migrations.Migration):

    dependencies = [
        ('wagtailcore', '0020_add_index_on_page_first_published_at'),
        ('books', '0002_remove_book_name'),
    ]

    operations = [
        migrations.CreateModel(
            name='BookIndex',
            fields=[
                ('page_ptr', models.OneToOneField(serialize=False, primary_key=True, auto_created=True, to='wagtailcore.Page', parent_link=True)),
                ('page_description', wagtail.wagtailcore.fields.RichTextField()),
                ('dev_standards_heading', models.CharField(blank=True, null=True, max_length=255)),
                ('dev_standard_1_heading', models.CharField(blank=True, null=True, max_length=255)),
                ('dev_standard_1_description', wagtail.wagtailcore.fields.RichTextField()),
                ('dev_standard_2_heading', models.CharField(blank=True, null=True, max_length=255)),
                ('dev_standard_2_description', wagtail.wagtailcore.fields.RichTextField()),
                ('dev_standard_3_heading', models.CharField(blank=True, null=True, max_length=255)),
                ('dev_standard_3_description', wagtail.wagtailcore.fields.RichTextField()),
            ],
            options={
                'abstract': False,
            },
            bases=('wagtailcore.page',),
        ),
    ]
