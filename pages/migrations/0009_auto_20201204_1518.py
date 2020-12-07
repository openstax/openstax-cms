# Generated by Django 3.0.4 on 2020-12-04 21:18

from django.db import migrations, models
import django.db.models.deletion
import wagtail.core.blocks
import wagtail.core.fields
import wagtail.images.blocks


class Migration(migrations.Migration):

    dependencies = [
        ('wagtaildocs', '0010_document_file_hash'),
        ('pages', '0008_tutormarketing'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tutormarketing',
            name='cost_cards',
            field=wagtail.core.fields.StreamField([('cards', wagtail.core.blocks.StructBlock([('icon', wagtail.images.blocks.ImageChooserBlock(required=False)), ('title', wagtail.core.blocks.CharBlock(required=True)), ('description', wagtail.core.blocks.RichTextBlock(required=True))]))]),
        ),
        migrations.AlterField(
            model_name='tutormarketing',
            name='features_cards',
            field=wagtail.core.fields.StreamField([('cards', wagtail.core.blocks.StructBlock([('icon', wagtail.images.blocks.ImageChooserBlock(required=False)), ('title', wagtail.core.blocks.CharBlock(required=True)), ('description', wagtail.core.blocks.RichTextBlock(required=True))]))]),
        ),
        migrations.AlterField(
            model_name='tutormarketing',
            name='feedback_image',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='wagtaildocs.Document'),
        ),
    ]