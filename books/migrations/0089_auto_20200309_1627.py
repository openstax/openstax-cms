# Generated by Django 2.2.10 on 2020-03-09 21:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('books', '0088_auto_20200309_1624'),
    ]

    operations = [
        migrations.AlterField(
            model_name='book',
            name='updated',
            field=models.DateTimeField(blank=True, help_text='Late date web content was updated', null=True),
        ),
    ]