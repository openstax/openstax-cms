# Generated by Django 2.0.2 on 2018-07-06 00:47

from django.db import migrations, models
import news.models
import wagtail.blocks
import wagtail.fields
import wagtail.documents.blocks
import wagtail.embeds.blocks
import wagtail.images.blocks


class Migration(migrations.Migration):

    dependencies = [
        ('news', '0031_auto_20180523_0934'),
    ]

    operations = [
        migrations.AddField(
            model_name='newsarticle',
            name='featured_image_alt_text',
            field=models.CharField(blank=True, max_length=250, null=True),
        ),
        migrations.AddField(
            model_name='pressrelease',
            name='featured_image_alt_text',
            field=models.CharField(blank=True, max_length=250, null=True),
        ),
        migrations.AlterField(
            model_name='newsarticle',
            name='body',
            field=wagtail.fields.StreamField((('paragraph', wagtail.blocks.RichTextBlock(icon='pilcrow')), ('aligned_image', wagtail.blocks.StructBlock((('image', wagtail.images.blocks.ImageChooserBlock()), ('caption', wagtail.blocks.RichTextBlock()), ('alignment', news.models.ImageFormatChoiceBlock()), ('alt_text', wagtail.blocks.CharBlock(required=False))), icon='image', label='Aligned image')), ('pullquote', wagtail.blocks.StructBlock((('quote', wagtail.blocks.TextBlock('quote title')), ('attribution', wagtail.blocks.CharBlock())))), ('aligned_html', wagtail.blocks.RawHTMLBlock()), ('document', wagtail.documents.blocks.DocumentChooserBlock(icon='doc-full-inverse')), ('embed', wagtail.embeds.blocks.EmbedBlock(icon='media', label='Embed Media URL')))),
        ),
        migrations.AlterField(
            model_name='pressrelease',
            name='body',
            field=wagtail.fields.StreamField((('paragraph', wagtail.blocks.RichTextBlock(icon='pilcrow')), ('aligned_image', wagtail.blocks.StructBlock((('image', wagtail.images.blocks.ImageChooserBlock()), ('caption', wagtail.blocks.RichTextBlock()), ('alignment', news.models.ImageFormatChoiceBlock()), ('alt_text', wagtail.blocks.CharBlock(required=False))), icon='image', label='Aligned image')), ('pullquote', wagtail.blocks.StructBlock((('quote', wagtail.blocks.TextBlock('quote title')), ('attribution', wagtail.blocks.CharBlock())))), ('aligned_html', wagtail.blocks.RawHTMLBlock()), ('document', wagtail.documents.blocks.DocumentChooserBlock(icon='doc-full-inverse')), ('embed', wagtail.embeds.blocks.EmbedBlock(icon='media', label='Embed Media URL')))),
        ),
    ]
