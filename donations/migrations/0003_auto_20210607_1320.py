# Generated by Django 3.0.4 on 2021-06-07 18:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('donations', '0002_donationpopup'),
    ]

    operations = [
        migrations.AlterField(
            model_name='donationpopup',
            name='download_ready',
            field=models.TextField(blank=True, default=''),
        ),
        migrations.AlterField(
            model_name='donationpopup',
            name='give_link',
            field=models.TextField(blank=True, default=''),
        ),
        migrations.AlterField(
            model_name='donationpopup',
            name='header_subtitle',
            field=models.TextField(blank=True, default=''),
        ),
        migrations.AlterField(
            model_name='donationpopup',
            name='header_title',
            field=models.TextField(blank=True, default=''),
        ),
        migrations.AlterField(
            model_name='donationpopup',
            name='thank_you_link',
            field=models.TextField(blank=True, default=''),
        ),
        migrations.AlterField(
            model_name='thankyounote',
            name='thank_you_note',
            field=models.TextField(blank=True, default=''),
        ),
        migrations.AlterField(
            model_name='thankyounote',
            name='user_info',
            field=models.TextField(blank=True, default=''),
        ),
    ]
