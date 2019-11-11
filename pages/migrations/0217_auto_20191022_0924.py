# Generated by Django 2.2.5 on 2019-10-22 14:24

from django.db import migrations
import pages.models
import wagtail.core.blocks
import wagtail.core.fields
import wagtail.images.blocks


class Migration(migrations.Migration):

    dependencies = [
        ('pages', '0216_auto_20191021_1500'),
    ]

    operations = [
        migrations.AlterField(
            model_name='creatorfestpage',
            name='page_panels',
            field=wagtail.core.fields.StreamField([('panel', wagtail.core.blocks.StructBlock([('superheading', wagtail.core.blocks.CharBlock(required=False)), ('heading', wagtail.core.blocks.CharBlock()), ('background_image', wagtail.core.blocks.StructBlock([('image', wagtail.images.blocks.ImageChooserBlock(required=False)), ('alt_text', wagtail.core.blocks.CharBlock(required=False)), ('link', wagtail.core.blocks.URLBlock(required=False)), ('alignment', pages.models.ImageFormatChoiceBlock()), ('identifier', wagtail.core.blocks.CharBlock(help_text='Used by the frontend for Google Analytics.', required=False))], required=False)), ('embed', wagtail.core.blocks.RawHTMLBlock(required=False)), ('paragraph', wagtail.core.blocks.RichTextBlock(required=False)), ('cards', wagtail.core.blocks.ListBlock(wagtail.core.blocks.StructBlock([('icon', wagtail.core.blocks.StructBlock([('image', wagtail.images.blocks.ImageChooserBlock(required=False)), ('alt_text', wagtail.core.blocks.CharBlock(required=False)), ('link', wagtail.core.blocks.URLBlock(required=False)), ('alignment', pages.models.ImageFormatChoiceBlock()), ('identifier', wagtail.core.blocks.CharBlock(help_text='Used by the frontend for Google Analytics.', required=False))])), ('headline', wagtail.core.blocks.CharBlock()), ('description', wagtail.core.blocks.RichTextBlock())], null=True)))]))], null=True),
        ),
    ]