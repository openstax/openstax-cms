# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import wagtail.wagtailcore.fields


class Migration(migrations.Migration):

    dependencies = [
        ('pages', '0020_generalpage'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='homepage',
            name='intro_image',
        ),
        migrations.RemoveField(
            model_name='homepage',
            name='introduction',
        ),
        migrations.RemoveField(
            model_name='homepage',
            name='page_header',
        ),
        migrations.AddField(
            model_name='homepage',
            name='about_us',
            field=wagtail.wagtailcore.fields.RichTextField(default=''),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='homepage',
            name='about_us_heading',
            field=models.CharField(max_length=255, default=''),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='homepage',
            name='adopter',
            field=wagtail.wagtailcore.fields.RichTextField(default=''),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='homepage',
            name='adopter_heading',
            field=models.CharField(max_length=255, default=''),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='homepage',
            name='allies',
            field=wagtail.wagtailcore.fields.RichTextField(default=''),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='homepage',
            name='allies_heading',
            field=models.CharField(max_length=255, default=''),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='homepage',
            name='ap_disclaimer',
            field=wagtail.wagtailcore.fields.RichTextField(default=''),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='homepage',
            name='give',
            field=wagtail.wagtailcore.fields.RichTextField(default=''),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='homepage',
            name='give_heading',
            field=models.CharField(max_length=255, default=''),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='homepage',
            name='wwd_12',
            field=wagtail.wagtailcore.fields.RichTextField(default=''),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='homepage',
            name='wwd_higher_ed',
            field=wagtail.wagtailcore.fields.RichTextField(default=''),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='homepage',
            name='wwd_higher_ed_heading',
            field=models.CharField(max_length=255, default=''),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='homepage',
            name='wwd_k12_heading',
            field=models.CharField(max_length=255, default=''),
            preserve_default=False,
        ),
    ]
