# Generated by Django 3.0.4 on 2021-01-28 18:08

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('books', '0125_remove_book_table_of_contents'),
        ('api', '0005_customizationrequest_created'),
    ]

    operations = [
        migrations.AddField(
            model_name='customizationrequest',
            name='book',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='books.Book'),
        ),
    ]
