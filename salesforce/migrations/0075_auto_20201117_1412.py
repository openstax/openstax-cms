# Generated by Django 3.0.4 on 2020-11-17 20:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('salesforce', '0074_partnerreview_partner_response_date'),
    ]

    operations = [
        migrations.AlterField(
            model_name='partnerreview',
            name='partner_response_date',
            field=models.DateField(blank=True, null=True),
        ),
    ]