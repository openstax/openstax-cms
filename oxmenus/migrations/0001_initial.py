# Generated by Django 4.0.8 on 2023-05-31 16:09

from django.db import migrations, models
import wagtail.blocks
import wagtail.fields


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Menus',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('menu', wagtail.fields.StreamField([('menus', wagtail.blocks.StructBlock([('menu_items', wagtail.blocks.ListBlock(wagtail.blocks.StructBlock([('label', wagtail.blocks.CharBlock(max_length=255)), ('partial_url', wagtail.blocks.CharBlock(max_length=255))], required=True)))], required=True))], use_json_field=True)),
            ],
        ),
    ]
