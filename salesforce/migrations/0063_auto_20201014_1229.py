# Generated by Django 3.0.4 on 2020-10-14 17:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('salesforce', '0062_savingsnumber'),
    ]

    operations = [
        migrations.AlterField(
            model_name='savingsnumber',
            name='savings',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=50, null=True),
        ),
    ]
