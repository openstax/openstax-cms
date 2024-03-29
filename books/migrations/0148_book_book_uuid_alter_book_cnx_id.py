# Generated by Django 4.0.8 on 2023-07-12 16:31

from django.apps import apps
from django.db import migrations, models
from django.db.models import F


class Migration(migrations.Migration):

    dependencies = [
        ('books', '0147_alter_facultyresources_link_external_and_more'),
    ]

    def copy_cnx_id(apps, schema):
        book = apps.get_model('books', 'Book')
        book.objects.all().update(book_uuid=F('cnx_id'))

    operations = [
        migrations.AddField(
            model_name='book',
            name='book_uuid',
            field=models.CharField(blank=True, help_text='collection.xml UUID. Should be same as cnx id.', max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name='book',
            name='cnx_id',
            field=models.CharField(blank=True, help_text='collection.xml UUID. Should be same as book UUID', max_length=255, null=True),
        ),
        migrations.RunPython(code=copy_cnx_id),
    ]
