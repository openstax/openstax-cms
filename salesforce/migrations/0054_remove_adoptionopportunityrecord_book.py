# Generated by Django 3.0.4 on 2020-07-28 21:42

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('salesforce', '0053_remove_adoptionopportunityrecord_updated'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='adoptionopportunityrecord',
            name='book',
        ),
    ]
