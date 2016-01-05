# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import wagtail.wagtailcore.fields


class Migration(migrations.Migration):

    dependencies = [
        ('pages', '0016_auto_20160105_1328'),
    ]

    operations = [
        migrations.RenameField(
            model_name='products',
            old_name='allies_intro',
            new_name='allies',
        ),
        migrations.RenameField(
            model_name='products',
            old_name='cnx_intro',
            new_name='cnx',
        ),
        migrations.RenameField(
            model_name='products',
            old_name='concept_coach_intro',
            new_name='concept_coach',
        ),
        migrations.RenameField(
            model_name='products',
            old_name='tutor_intro',
            new_name='tutor',
        ),
        migrations.AddField(
            model_name='products',
            name='allies_heading',
            field=models.CharField(max_length=255, default=''),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='products',
            name='ally_1_heading',
            field=models.CharField(max_length=255, default=''),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='products',
            name='ally_2_heading',
            field=models.CharField(max_length=255, default=''),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='products',
            name='ally_3_heading',
            field=models.CharField(max_length=255, default=''),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='products',
            name='ally_4_heading',
            field=models.CharField(max_length=255, default=''),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='products',
            name='ally_5',
            field=wagtail.wagtailcore.fields.RichTextField(default=''),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='products',
            name='ally_5_heading',
            field=models.CharField(max_length=255, default=''),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='products',
            name='cnx_heading',
            field=models.CharField(max_length=255, default=''),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='products',
            name='concept_coach_heading',
            field=models.CharField(max_length=255, default=''),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='products',
            name='intro_heading',
            field=models.CharField(max_length=255, default=''),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='products',
            name='tutor_heading',
            field=models.CharField(max_length=255, default=''),
            preserve_default=False,
        ),
    ]
