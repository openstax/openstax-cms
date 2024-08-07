# Generated by Django 3.0.4 on 2020-12-04 21:18

from django.db import migrations, models
import django.db.models.deletion
import wagtail.blocks
import wagtail.fields
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
            field=wagtail.fields.StreamField([('cards', wagtail.blocks.StructBlock([('icon', wagtail.images.blocks.ImageChooserBlock(required=False)), ('title', wagtail.blocks.CharBlock(required=True)), ('description', wagtail.blocks.RichTextBlock(required=True))]))]),
        ),
        migrations.AlterField(
            model_name='tutormarketing',
            name='features_cards',
            field=wagtail.fields.StreamField([('cards', wagtail.blocks.StructBlock([('icon', wagtail.images.blocks.ImageChooserBlock(required=False)), ('title', wagtail.blocks.CharBlock(required=True)), ('description', wagtail.blocks.RichTextBlock(required=True))]))]),
        ),
        migrations.AlterField(
            model_name='tutormarketing',
            name='feedback_image',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='wagtaildocs.Document'),
        ),
    ]
