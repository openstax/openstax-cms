# Generated by Django 3.0.4 on 2021-01-26 21:19

from django.db import migrations
import pages.custom_blocks
import wagtail.core.blocks
import wagtail.core.fields


class Migration(migrations.Migration):

    dependencies = [
        ('pages', '0024_auto_20210126_1336'),
    ]

    operations = [
        migrations.AlterField(
            model_name='impact',
            name='making_a_difference',
            field=wagtail.core.fields.StreamField([('content', wagtail.core.blocks.StructBlock([('heading', wagtail.core.blocks.CharBlock()), ('description', wagtail.core.blocks.RichTextBlock()), ('stories', wagtail.core.blocks.StructBlock([('image', pages.custom_blocks.APIImageChooserBlock(required=False)), ('story_text', wagtail.core.blocks.TextBlock(required=False)), ('embeded_video', wagtail.core.blocks.RawHTMLBlock(required=False))]))]))]),
        ),
    ]