# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import wagtail.wagtailimages.blocks
import wagtail.wagtailcore.fields
import wagtail.wagtailcore.blocks


class Migration(migrations.Migration):

    dependencies = [
        ('wagtailcore', '0020_add_index_on_page_first_published_at'),
        ('pages', '0019_remove_give_classroom_text'),
    ]

    operations = [
        migrations.CreateModel(
            name='GeneralPage',
            fields=[
                ('page_ptr', models.OneToOneField(serialize=False, primary_key=True, to='wagtailcore.Page', auto_created=True, parent_link=True)),
                ('body', wagtail.wagtailcore.fields.StreamField((('heading', wagtail.wagtailcore.blocks.CharBlock(classname='full title')), ('paragraph', wagtail.wagtailcore.blocks.RichTextBlock()), ('image', wagtail.wagtailimages.blocks.ImageChooserBlock()), ('html', wagtail.wagtailcore.blocks.RawHTMLBlock())))),
            ],
            options={
                'abstract': False,
            },
            bases=('wagtailcore.page',),
        ),
    ]
