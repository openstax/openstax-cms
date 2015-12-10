# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pages', '0003_standardpage'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='standardpage',
            name='carousel_item_one',
        ),
        migrations.RemoveField(
            model_name='standardpage',
            name='carousel_item_three',
        ),
        migrations.RemoveField(
            model_name='standardpage',
            name='carousel_item_two',
        ),
    ]
