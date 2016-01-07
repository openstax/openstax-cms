# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import wagtail.wagtailcore.fields


class Migration(migrations.Migration):

    dependencies = [
        ('pages', '0018_auto_20160106_1254'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='k12',
            name='classroom_text',
        ),
        migrations.AddField(
            model_name='k12',
            name='allies',
            field=wagtail.wagtailcore.fields.RichTextField(default=''),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='k12',
            name='allies_heading',
            field=models.CharField(default='', max_length=255),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='k12',
            name='cnx',
            field=wagtail.wagtailcore.fields.RichTextField(default=''),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='k12',
            name='cnx_heading',
            field=models.CharField(default='', max_length=255),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='k12',
            name='k12',
            field=wagtail.wagtailcore.fields.RichTextField(default=''),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='k12',
            name='k12_heading',
            field=models.CharField(default='', max_length=255),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='k12',
            name='tutor',
            field=wagtail.wagtailcore.fields.RichTextField(default=''),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='k12',
            name='tutor_heading',
            field=models.CharField(default='', max_length=255),
            preserve_default=False,
        ),
    ]
