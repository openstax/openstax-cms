# Generated by Django 3.0.4 on 2020-07-23 17:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('salesforce', '0048_auto_20200721_1256'),
    ]

    operations = [
        migrations.AddField(
            model_name='resourcedownload',
            name='salesforce_id',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
    ]