# Generated by Django 3.0.4 on 2020-08-13 21:13

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('wagtaildocs', '0010_document_file_hash'),
        ('books', '0106_auto_20200728_1547'),
    ]

    operations = [
        migrations.AlterField(
            model_name='book',
            name='cover',
            field=models.ForeignKey(blank=True, help_text='The book cover to be shown on the website.', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='wagtaildocs.Document'),
        ),
        migrations.AlterField(
            model_name='book',
            name='title_image',
            field=models.ForeignKey(blank=True, help_text='The svg for title image to be shown on the website.', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='wagtaildocs.Document'),
        ),
    ]
