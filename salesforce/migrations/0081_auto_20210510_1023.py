# Generated by Django 3.0.4 on 2021-05-10 15:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('salesforce', '0080_resourcedownload_contact_id'),
    ]

    operations = [
        migrations.AlterField(
            model_name='resourcedownload',
            name='contact_id',
            field=models.CharField(blank=True, default='', max_length=100),
        ),
    ]
