# Generated by Django 3.2.5 on 2022-05-11 12:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('books', '0134_alter_book_license_name'),
    ]

    operations = [
        migrations.AlterField(
            model_name='book',
            name='license_name',
            field=models.CharField(blank=True, choices=[('Creative Commons Attribution License', 'Creative Commons Attribution License'), ('Creative Commons Attribution-NonCommercial-ShareAlike License', 'Creative Commons Attribution-NonCommercial-ShareAlike License')], default='Creative Commons Attribution License', help_text='Name of the license.', max_length=255, null=True),
        ),
    ]