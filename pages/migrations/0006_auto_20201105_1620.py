# Generated by Django 3.0.4 on 2020-11-05 22:20

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('wagtaildocs', '0010_document_file_hash'),
        ('pages', '0005_auto_20201105_1414'),
    ]

    operations = [
        migrations.AlterField(
            model_name='llphpage',
            name='book_cover',
            field=models.ForeignKey(blank=True, help_text='The book cover to be shown on the website.', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='wagtaildocs.Document'),
        ),
    ]
