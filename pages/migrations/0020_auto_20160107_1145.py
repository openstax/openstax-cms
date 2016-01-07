# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pages', '0019_auto_20160107_1143'),
    ]

    operations = [
        migrations.RenameField(
            model_name='k12',
            old_name='allies',
            new_name='allies_description',
        ),
        migrations.RenameField(
            model_name='k12',
            old_name='cnx',
            new_name='cnx_description',
        ),
        migrations.RenameField(
            model_name='k12',
            old_name='k12',
            new_name='k12_description',
        ),
        migrations.RenameField(
            model_name='k12',
            old_name='tutor',
            new_name='tutor_description',
        ),
    ]
