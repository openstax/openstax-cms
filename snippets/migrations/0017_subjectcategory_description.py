# Generated by Django 3.2.9 on 2022-02-16 16:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('snippets', '0016_subject_icon'),
    ]

    operations = [
        migrations.AddField(
            model_name='subjectcategory',
            name='description',
            field=models.TextField(default=''),
        ),
    ]