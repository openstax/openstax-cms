# Generated by Django 3.2.4 on 2021-06-29 15:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('salesforce', '0082_partner_partnership_level'),
    ]

    operations = [
        migrations.AlterField(
            model_name='resourcedownload',
            name='contact_id',
            field=models.CharField(default='', max_length=100, null=True),
        ),
    ]
