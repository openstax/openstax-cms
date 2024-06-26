# Generated by Django 3.0.4 on 2020-12-04 19:38

from django.db import migrations, models
import django.db.models.deletion
import pages.models
import wagtail.blocks
import wagtail.fields
import wagtail.documents.blocks
import wagtail.images.blocks


class Migration(migrations.Migration):

    dependencies = [
        ('wagtailimages', '0022_uploadedimage'),
        ('wagtaildocs', '0010_document_file_hash'),
        ('wagtailcore', '0052_pagelogentry'),
        ('pages', '0007_merge_20201106_1444'),
    ]

    operations = [
        migrations.CreateModel(
            name='TutorMarketing',
            fields=[
                ('page_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='wagtailcore.Page')),
                ('header', models.CharField(max_length=255)),
                ('description', models.TextField()),
                ('header_cta_button_text', models.CharField(max_length=255)),
                ('header_cta_button_link', models.URLField()),
                ('quote', wagtail.fields.RichTextField()),
                ('features_header', models.CharField(max_length=255)),
                ('features_cards', wagtail.fields.StreamField([('card', wagtail.blocks.StreamBlock([('icon', wagtail.blocks.StructBlock([('image', wagtail.images.blocks.ImageChooserBlock(required=False)), ('alt_text', wagtail.blocks.CharBlock(required=False)), ('link', wagtail.blocks.URLBlock(required=False)), ('alignment', pages.custom_blocks.ImageFormatChoiceBlock()), ('identifier', wagtail.blocks.CharBlock(help_text='Used by the frontend for Google Analytics.', required=False))])), ('title', wagtail.blocks.TextBlock()), ('description', wagtail.blocks.TextBlock())], icon='placeholder'))])),
                ('available_books_header', models.CharField(max_length=255)),
                ('cost_header', models.CharField(max_length=255)),
                ('cost_description', models.TextField()),
                ('cost_cards', wagtail.fields.StreamField([('card', wagtail.blocks.StreamBlock([('title', wagtail.blocks.CharBlock()), ('description', wagtail.blocks.TextBlock())], icon='placeholder'))])),
                ('cost_institution_message', models.CharField(max_length=255)),
                ('feedback_heading', models.CharField(max_length=255)),
                ('feedback_quote', models.TextField()),
                ('feedback_name', models.CharField(max_length=255)),
                ('feedback_occupation', models.CharField(max_length=255)),
                ('feedback_organization', models.CharField(max_length=255)),
                ('webinars_header', models.CharField(max_length=255)),
                ('faq_header', models.CharField(max_length=255)),
                ('faqs', wagtail.fields.StreamField([('faq', wagtail.blocks.StructBlock([('question', wagtail.blocks.RichTextBlock(required=True)), ('slug', wagtail.blocks.CharBlock(required=True)), ('answer', wagtail.blocks.RichTextBlock(required=True)), ('document', wagtail.documents.blocks.DocumentChooserBlock(required=False))]))])),
                ('demo_cta_text', models.CharField(max_length=255)),
                ('demo_cta_link', models.URLField()),
                ('tutor_login_link', models.URLField()),
                ('feedback_image', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='wagtaildocs.Document')),
                ('promote_image', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='wagtailimages.Image')),
            ],
            options={
                'abstract': False,
            },
            bases=('wagtailcore.page',),
        ),
    ]
