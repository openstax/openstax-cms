# Generated by Django 3.0.4 on 2020-10-28 19:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('salesforce', '0071_auto_20201028_1427'),
    ]

    operations = [
        migrations.AlterField(
            model_name='partnerreview',
            name='status',
            field=models.CharField(choices=[('New', 'New'), ('Edited', 'Edited'), ('Awaiting Approval', 'Awaiting Approval'), ('Approved', 'Approved')], default='New', max_length=255),
        ),
    ]