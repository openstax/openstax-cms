# Generated by Django 3.2.4 on 2021-10-18 16:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('salesforce', '0090_auto_20211014_1201'),
    ]

    operations = [
        migrations.AddField(
            model_name='resourcedownload',
            name='accounts_uuid',
            field=models.UUIDField(null=True),
        ),
        migrations.AlterField(
            model_name='resourcedownload',
            name='account_id',
            field=models.IntegerField(blank=True, null=True),
        ),
    ]