# Generated by Django 2.0.2 on 2018-05-17 21:54

from django.db import migrations
import news.models
import snippets.models
import wagtail.blocks
import wagtail.fields


class Migration(migrations.Migration):

    dependencies = [
        ('news', '0028_remove_pressindex_mentions'),
    ]

    operations = [
        migrations.AddField(
            model_name='pressindex',
            name='mentions',
            field=wagtail.fields.StreamField((('mention', wagtail.blocks.StructBlock((('source', news.models.NewsMentionChooserBlock(snippets.models.NewsSource)), ('url', wagtail.blocks.URLBlock()), ('headline', wagtail.blocks.CharBlock()), ('date', wagtail.blocks.DateBlock())))),), null=True),
        ),
    ]
