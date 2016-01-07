# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pages', '0021_auto_20160106_1701'),
    ]

    operations = [
        migrations.RenameField(
            model_name='homepage',
            old_name='give',
            new_name='give_to_openstax',
        ),
    ]
