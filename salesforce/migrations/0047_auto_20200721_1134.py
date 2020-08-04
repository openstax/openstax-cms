# Generated by Django 3.0.4 on 2020-07-21 16:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('books', '0002_auto_20200720_1527'),
        ('salesforce', '0046_auto_20200720_1527'),
    ]

    operations = [
        migrations.AlterField(
            model_name='resourcedownload',
            name='account_id',
            field=models.IntegerField(),
        ),
        migrations.AlterUniqueTogether(
            name='resourcedownload',
            unique_together={('account_id', 'book', 'resource_name')},
        ),
    ]