# Generated by Django 3.2.5 on 2022-06-16 18:49

from django.db import migrations
import news.models
import wagtail.blocks
import wagtail.fields


class Migration(migrations.Migration):

    dependencies = [
        ('news', '0045_merge_20220520_1523'),
    ]

    operations = [
        migrations.AlterField(
            model_name='newsarticle',
            name='article_subjects',
            field=wagtail.fields.StreamField([('subject', wagtail.blocks.ListBlock(wagtail.blocks.StructBlock([('subject', news.models.BlogCollectionChooserBlock(label='Blog Subject', required=True, target_model='snippets.Subject')), ('featured', wagtail.blocks.BooleanBlock(label='Featured', required=False))])))], blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='newsarticle',
            name='collections',
            field=wagtail.fields.StreamField([('collection', wagtail.blocks.ListBlock(wagtail.blocks.StructBlock([('collection', news.models.BlogCollectionChooserBlock(label='Blog Collection', required=True, target_model='snippets.BlogCollection')), ('featured', wagtail.blocks.BooleanBlock(label='Featured', required=False)), ('popular', wagtail.blocks.BooleanBlock(label='Popular', required=False))])))], blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='newsarticle',
            name='content_types',
            field=wagtail.fields.StreamField([('content_type', wagtail.blocks.ListBlock(wagtail.blocks.StructBlock([('content_type', news.models.ContentTypeChooserBlock(label='Blog Content Type', required=True, target_model='snippets.BlogContentType'))])))], blank=True, null=True),
        ),
    ]
