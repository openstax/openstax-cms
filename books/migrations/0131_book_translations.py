# Generated by Django 3.2.4 on 2021-07-22 20:39

from django.db import migrations
import wagtail.blocks
import wagtail.fields


class Migration(migrations.Migration):

    dependencies = [
        ('books', '0130_remove_book_errata_content'),
    ]

    operations = [
        migrations.AddField(
            model_name='book',
            name='translations',
            field=wagtail.fields.StreamField([('translation', wagtail.blocks.ListBlock(wagtail.blocks.StructBlock([('locale', wagtail.blocks.CharBlock()), ('slug', wagtail.blocks.CharBlock())])))], blank=True, null=True),
        ),
    ]
