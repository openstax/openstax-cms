# Generated by Django 3.2.5 on 2022-07-19 17:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('errata', '0051_auto_20220516_2113'),
    ]

    operations = [
        migrations.AlterField(
            model_name='errata',
            name='status',
            field=models.CharField(choices=[('New', 'New'), ('Editorial Review', 'Editorial Review'), ('K-12 Editorial Review', 'K-12 Editorial Review'), ('Cartridge Review', 'Cartridge Review'), ('OpenStax Editorial Review', 'OpenStax Editorial Review'), ('Reviewed', 'Reviewed'), ('Completed', 'Completed')], default='New', max_length=100),
        ),
    ]