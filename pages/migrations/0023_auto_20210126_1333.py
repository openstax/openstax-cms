# Generated by Django 3.0.4 on 2021-01-26 19:33

from django.db import migrations
import pages.custom_blocks
import wagtail.blocks
import wagtail.fields
import wagtail.images.blocks


class Migration(migrations.Migration):

    dependencies = [
        ('pages', '0022_auto_20210126_1323'),
    ]

    operations = [
        migrations.AlterField(
            model_name='impact',
            name='improving_access',
            field=wagtail.fields.StreamField([('content', wagtail.blocks.StructBlock([('image', wagtail.blocks.StructBlock([('image', wagtail.images.blocks.ImageChooserBlock(required=False)), ('alt_text', wagtail.blocks.CharBlock(required=False)), ('link', wagtail.blocks.URLBlock(required=False)), ('alignment', pages.custom_blocks.ImageFormatChoiceBlock()), ('identifier', wagtail.blocks.CharBlock(help_text='Used by the frontend for Google Analytics.', required=False))])), ('heading', wagtail.blocks.CharBlock()), ('description', wagtail.blocks.RichTextBlock()), ('button_text', wagtail.blocks.CharBlock()), ('button_href', wagtail.blocks.URLBlock())]))]),
        ),
    ]
