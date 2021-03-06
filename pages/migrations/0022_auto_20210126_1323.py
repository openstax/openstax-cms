# Generated by Django 3.0.4 on 2021-01-26 19:23

from django.db import migrations
import pages.custom_blocks
import wagtail.core.blocks
import wagtail.core.fields
import wagtail.images.blocks


class Migration(migrations.Migration):

    dependencies = [
        ('pages', '0021_auto_20210126_1318'),
    ]

    operations = [
        migrations.AlterField(
            model_name='impact',
            name='disruption',
            field=wagtail.core.fields.StreamField([('content', wagtail.core.blocks.StructBlock([('heading', wagtail.core.blocks.CharBlock()), ('description', wagtail.core.blocks.TextBlock()), ('graph', wagtail.core.blocks.StructBlock([('top_caption', wagtail.core.blocks.CharBlock()), ('bottom_caption', wagtail.core.blocks.RichTextBlock()), ('image', wagtail.core.blocks.StructBlock([('image', wagtail.images.blocks.ImageChooserBlock(required=False)), ('alt_text', wagtail.core.blocks.CharBlock(required=False)), ('link', wagtail.core.blocks.URLBlock(required=False)), ('alignment', pages.custom_blocks.ImageFormatChoiceBlock()), ('identifier', wagtail.core.blocks.CharBlock(help_text='Used by the frontend for Google Analytics.', required=False))], required=False)), ('image_alt_text', wagtail.core.blocks.CharBlock(required=False))]))], max_num=1))], blank=True),
        ),
        migrations.AlterField(
            model_name='impact',
            name='giving',
            field=wagtail.core.fields.StreamField([('content', wagtail.core.blocks.StructBlock([('heading', wagtail.core.blocks.CharBlock()), ('description', wagtail.core.blocks.TextBlock()), ('link', wagtail.core.blocks.CharBlock()), ('link_text', wagtail.core.blocks.CharBlock())], max_num=1))], blank=True),
        ),
        migrations.AlterField(
            model_name='impact',
            name='making_a_difference',
            field=wagtail.core.fields.StreamField([('content', wagtail.core.blocks.StructBlock([('heading', wagtail.core.blocks.CharBlock()), ('description', wagtail.core.blocks.RichTextBlock()), ('stories', wagtail.core.blocks.ListBlock(wagtail.core.blocks.StructBlock([('image', pages.custom_blocks.APIImageChooserBlock(required=False)), ('story_text', wagtail.core.blocks.TextBlock(required=False)), ('embeded_video', wagtail.core.blocks.RawHTMLBlock(required=False))])))], max_num=1))], blank=True),
        ),
        migrations.AlterField(
            model_name='impact',
            name='quote',
            field=wagtail.core.fields.StreamField([('content', wagtail.core.blocks.StructBlock([('image', wagtail.core.blocks.StructBlock([('image', wagtail.images.blocks.ImageChooserBlock(required=False)), ('alt_text', wagtail.core.blocks.CharBlock(required=False)), ('link', wagtail.core.blocks.URLBlock(required=False)), ('alignment', pages.custom_blocks.ImageFormatChoiceBlock()), ('identifier', wagtail.core.blocks.CharBlock(help_text='Used by the frontend for Google Analytics.', required=False))])), ('quote', wagtail.core.blocks.RichTextBlock())], max_num=1))], blank=True),
        ),
        migrations.AlterField(
            model_name='impact',
            name='reach',
            field=wagtail.core.fields.StreamField([('content', wagtail.core.blocks.StructBlock([('heading', wagtail.core.blocks.CharBlock()), ('description', wagtail.core.blocks.RichTextBlock()), ('cards', wagtail.core.blocks.ListBlock(wagtail.core.blocks.StructBlock([('icon', pages.custom_blocks.APIImageChooserBlock(required=False)), ('title', wagtail.core.blocks.CharBlock(required=True)), ('description', wagtail.core.blocks.RichTextBlock(required=True))])))], max_num=1))], blank=True),
        ),
        migrations.AlterField(
            model_name='impact',
            name='supporter_community',
            field=wagtail.core.fields.StreamField([('content', wagtail.core.blocks.StructBlock([('heading', wagtail.core.blocks.CharBlock()), ('image', wagtail.core.blocks.StructBlock([('image', wagtail.images.blocks.ImageChooserBlock(required=False)), ('alt_text', wagtail.core.blocks.CharBlock(required=False)), ('link', wagtail.core.blocks.URLBlock(required=False)), ('alignment', pages.custom_blocks.ImageFormatChoiceBlock()), ('identifier', wagtail.core.blocks.CharBlock(help_text='Used by the frontend for Google Analytics.', required=False))])), ('quote', wagtail.core.blocks.RichTextBlock()), ('link_text', wagtail.core.blocks.CharBlock()), ('link_href', wagtail.core.blocks.URLBlock())], max_num=1))], blank=True),
        ),
    ]
