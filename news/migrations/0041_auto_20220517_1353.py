# Generated by Django 3.2.5 on 2022-05-17 18:53

from django.db import migrations
import wagtail.core.blocks
import wagtail.core.fields


class Migration(migrations.Migration):

    dependencies = [
        ('news', '0040_alter_newsarticle_content_types'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='newsindex',
            name='intro',
        ),
        migrations.RemoveField(
            model_name='newsindex',
            name='press_kit',
        ),
        migrations.AddField(
            model_name='newsindex',
            name='interest_block',
            field=wagtail.core.fields.StreamField([('heading', wagtail.core.blocks.CharBlock()), ('description', wagtail.core.blocks.TextBlock()), ('button_text', wagtail.core.blocks.CharBlock()), ('button_href', wagtail.core.blocks.URLBlock())], null=True),
        ),
    ]