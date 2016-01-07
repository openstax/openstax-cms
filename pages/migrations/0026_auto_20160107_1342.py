# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pages', '0025_auto_20160107_1341'),
    ]

    operations = [
        migrations.RenameField(
            model_name='homepage',
            old_name='wwd_12_description',
            new_name='wwd_k12_description',
        ),
    ]
