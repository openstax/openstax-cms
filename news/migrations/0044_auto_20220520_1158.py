# Generated by Django 3.2.5 on 2022-05-20 16:58

from django.db import migrations
import news.models
import wagtail.core.blocks
import wagtail.core.fields
import wagtail.embeds.blocks


class Migration(migrations.Migration):

    dependencies = [
        ('news', '0043_alter_newsarticle_featured_video'),
    ]

    operations = [
        migrations.AlterField(
            model_name='newsarticle',
            name='body',
            field=wagtail.core.fields.StreamField([('paragraph', wagtail.core.blocks.RichTextBlock(icon='pilcrow')), ('aligned_image', wagtail.core.blocks.StructBlock([('image', news.models.ImageChooserBlock()), ('caption', wagtail.core.blocks.RichTextBlock()), ('alignment', news.models.ImageFormatChoiceBlock()), ('alt_text', wagtail.core.blocks.CharBlock(required=False))], icon='image', label='Aligned image')), ('pullquote', wagtail.core.blocks.StructBlock([('quote', wagtail.core.blocks.TextBlock('quote title')), ('attribution', wagtail.core.blocks.CharBlock())])), ('aligned_html', wagtail.core.blocks.RawHTMLBlock(icon='code', label='Raw HTML')), ('document', news.models.BlogDocumentChooserBlock(icon='doc-full-inverse')), ('embed', wagtail.embeds.blocks.EmbedBlock(icon='media', label='Embed Media URL')), ('blog_cta', wagtail.core.blocks.StructBlock([('heading', wagtail.core.blocks.CharBlock()), ('description', wagtail.core.blocks.TextBlock()), ('button_text', wagtail.core.blocks.CharBlock()), ('button_href', wagtail.core.blocks.URLBlock()), ('alignment', news.models.CTAAlignmentChoiceBlock())], icon='form', label='Call to Action block'))]),
        ),
        migrations.AlterField(
            model_name='pressrelease',
            name='body',
            field=wagtail.core.fields.StreamField([('paragraph', wagtail.core.blocks.RichTextBlock(icon='pilcrow')), ('aligned_image', wagtail.core.blocks.StructBlock([('image', news.models.ImageChooserBlock()), ('caption', wagtail.core.blocks.RichTextBlock()), ('alignment', news.models.ImageFormatChoiceBlock()), ('alt_text', wagtail.core.blocks.CharBlock(required=False))], icon='image', label='Aligned image')), ('pullquote', wagtail.core.blocks.StructBlock([('quote', wagtail.core.blocks.TextBlock('quote title')), ('attribution', wagtail.core.blocks.CharBlock())])), ('aligned_html', wagtail.core.blocks.RawHTMLBlock(icon='code', label='Raw HTML')), ('document', news.models.BlogDocumentChooserBlock(icon='doc-full-inverse')), ('embed', wagtail.embeds.blocks.EmbedBlock(icon='media', label='Embed Media URL')), ('blog_cta', wagtail.core.blocks.StructBlock([('heading', wagtail.core.blocks.CharBlock()), ('description', wagtail.core.blocks.TextBlock()), ('button_text', wagtail.core.blocks.CharBlock()), ('button_href', wagtail.core.blocks.URLBlock()), ('alignment', news.models.CTAAlignmentChoiceBlock())], icon='form', label='Call to Action block'))]),
        ),
    ]