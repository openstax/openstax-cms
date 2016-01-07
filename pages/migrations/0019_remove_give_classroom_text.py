# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pages', '0018_auto_20160106_1254'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='give',
            name='classroom_text',
        ),
    ]
