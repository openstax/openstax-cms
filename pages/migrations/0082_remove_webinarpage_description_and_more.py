# Generated by Django 4.0.8 on 2023-07-27 14:45

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('pages', '0081_remove_allylogos_openstax_logos_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='webinarpage',
            name='description',
        ),
        migrations.RemoveField(
            model_name='webinarpage',
            name='hero_image',
        ),
    ]