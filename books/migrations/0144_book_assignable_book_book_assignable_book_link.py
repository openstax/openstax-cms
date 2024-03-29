# Generated by Django 4.0.8 on 2023-03-22 20:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('books', '0143_remove_studentresources_k12_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='book',
            name='assignable_book',
            field=models.BooleanField(default=False, help_text='Whether this is an Assignable book.'),
        ),
        migrations.AddField(
            model_name='book',
            name='assignable_book_link',
            field=models.URLField(blank=True, help_text='Link to assignable page for book', null=True),
        ),
    ]
