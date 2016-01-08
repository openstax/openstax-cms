# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import wagtail.wagtailcore.fields


class Migration(migrations.Migration):

    dependencies = [
        ('pages', '0024_auto_20160107_1338'),
    ]

    operations = [
        migrations.RenameField(
            model_name='homepage',
            old_name='about_us',
            new_name='about_us_description',
        ),
        migrations.RenameField(
            model_name='homepage',
            old_name='adopter',
            new_name='adopter_description',
        ),
        migrations.RenameField(
            model_name='homepage',
            old_name='allies',
            new_name='allies_description',
        ),
        migrations.RenameField(
            model_name='homepage',
            old_name='give_to_openstax',
            new_name='give_description',
        ),
        migrations.RenameField(
            model_name='homepage',
            old_name='wwd_higher_ed',
            new_name='wwd_higher_ed_description',
        ),
        migrations.RemoveField(
            model_name='homepage',
            name='ap_disclaimer',
        ),
        migrations.AddField(
            model_name='homepage',
            name='wwd_12_description',
            field=wagtail.wagtailcore.fields.RichTextField(default=''),
            preserve_default=False,
        ),
    ]
