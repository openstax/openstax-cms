# Generated by Django 3.2.9 on 2021-12-15 16:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pages', '0048_auto_20210830_1133'),
    ]

    operations = [
        migrations.AlterField(
            model_name='homepage',
            name='banner_get_started_link',
            field=models.CharField(blank=True, default='', max_length=255),
        ),
        migrations.AlterField(
            model_name='homepage',
            name='banner_login_link',
            field=models.CharField(blank=True, default='', max_length=255),
        ),
    ]
