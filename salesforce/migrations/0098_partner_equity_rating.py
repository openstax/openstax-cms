# Generated by Django 3.2.9 on 2022-04-11 13:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('salesforce', '0097_auto_20220328_1130'),
    ]

    operations = [
        migrations.AddField(
            model_name='partner',
            name='equity_rating',
            field=models.CharField(default='', max_length=255, null=True),
        ),
    ]
