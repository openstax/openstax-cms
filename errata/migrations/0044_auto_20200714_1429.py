# Generated by Django 3.0.4 on 2020-07-14 19:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('errata', '0043_auto_20200414_1517'),
    ]

    operations = [
        migrations.AlterField(
            model_name='errata',
            name='status',
            field=models.CharField(choices=[('New', 'New'), ('Editorial Review', 'Editorial Review'), ('K-12 Editorial Review', 'K-12 Editorial Review'), ('Reviewed', 'Reviewed'), ('Completed', 'Completed')], default='New', max_length=100),
        ),
    ]
