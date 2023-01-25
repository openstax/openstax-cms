# Generated by Django 3.2.16 on 2023-01-12 20:26

from django.db import migrations, models
import django.db.models.deletion
import modelcluster.fields


class Migration(migrations.Migration):

    dependencies = [
        ('snippets', '0024_k12subject'),
        ('books', '0138_auto_20230112_1426'),
    ]

    operations = [
        migrations.AddField(
            model_name='k12subjectbooks',
            name='subject',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='k12subjects_subject', to='snippets.k12subject'),
        ),
        migrations.AddField(
            model_name='k12booksubjects',
            name='k12book_subject',
            field=modelcluster.fields.ParentalKey(on_delete=django.db.models.deletion.CASCADE, related_name='k12book_subjects', to='books.book'),
        ),
    ]