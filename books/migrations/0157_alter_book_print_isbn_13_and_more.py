# Generated by Django 5.0.7 on 2024-07-22 21:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("books", "0156_book_content_warning"),
    ]

    operations = [
        migrations.AlterField(
            model_name="book",
            name="print_isbn_13",
            field=models.CharField(
                blank=True, help_text="ISBN 13 for print version (color).", max_length=255, null=True
            ),
        ),
        migrations.AlterField(
            model_name="book",
            name="print_softcover_isbn_13",
            field=models.CharField(
                blank=True, help_text="ISBN 13 for print version (black and white).", max_length=255, null=True
            ),
        ),
    ]
