# Generated by Django 2.0.13 on 2019-05-31 05:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('salesforce', '0010_auto_20180910_1320'),
    ]

    operations = [
        migrations.AlterField(
            model_name='school',
            name='all_time_savings',
            field=models.DecimalField(blank=True, decimal_places=3, max_digits=12, null=True),
        ),
        migrations.AlterField(
            model_name='school',
            name='current_year_savings',
            field=models.DecimalField(blank=True, decimal_places=3, max_digits=12, null=True),
        ),
    ]
