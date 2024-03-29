# Generated by Django 3.2.4 on 2021-08-02 19:19

from django.db import migrations
import wagtail.blocks
import wagtail.fields


class Migration(migrations.Migration):

    dependencies = [
        ('books', '0131_book_translations'),
    ]

    operations = [
        migrations.AddField(
            model_name='bookindex',
            name='translations',
            field=wagtail.fields.StreamField([('translation', wagtail.blocks.ListBlock(wagtail.blocks.StructBlock([('locale', wagtail.blocks.CharBlock()), ('slug', wagtail.blocks.CharBlock())])))], blank=True, null=True),
        ),
    ]
