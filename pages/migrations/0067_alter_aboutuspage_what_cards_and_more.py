# Generated by Django 4.0.8 on 2023-01-11 21:58

from django.db import migrations
import news.models
import pages.custom_blocks
import pages.models
import wagtail.blocks
import wagtail.documents.blocks
import wagtail.embeds.blocks
import wagtail.fields
import wagtail.images.blocks


class Migration(migrations.Migration):

    dependencies = [
        ('pages', '0066_allylogos'),
    ]

    operations = [
        migrations.AlterField(
            model_name='aboutuspage',
            name='what_cards',
            field=wagtail.fields.StreamField([('card', wagtail.blocks.StreamBlock([('image', wagtail.blocks.StructBlock([('image', wagtail.images.blocks.ImageChooserBlock(required=False)), ('alt_text', wagtail.blocks.CharBlock(required=False)), ('link', wagtail.blocks.URLBlock(required=False)), ('alignment', pages.custom_blocks.ImageFormatChoiceBlock()), ('identifier', wagtail.blocks.CharBlock(help_text='Used by the frontend for Google Analytics.', required=False))])), ('paragraph', wagtail.blocks.TextBlock())], icon='placeholder'))], use_json_field=True),
        ),
        migrations.AlterField(
            model_name='allylogos',
            name='ally_logos',
            field=wagtail.fields.StreamField([('ally_logo', wagtail.blocks.ListBlock(wagtail.blocks.StructBlock([('image', pages.custom_blocks.APIImageChooserBlock())])))], use_json_field=True),
        ),
        migrations.AlterField(
            model_name='allylogos',
            name='book_ally_logos',
            field=wagtail.fields.StreamField([('book_ally_logo', wagtail.blocks.ListBlock(wagtail.blocks.StructBlock([('image', pages.custom_blocks.APIImageChooserBlock())])))], use_json_field=True),
        ),
        migrations.AlterField(
            model_name='allylogos',
            name='openstax_logos',
            field=wagtail.fields.StreamField([('openstax_logo', wagtail.blocks.ListBlock(wagtail.blocks.StructBlock([('image', pages.custom_blocks.APIImageChooserBlock())])))], use_json_field=True),
        ),
        migrations.AlterField(
            model_name='creatorfestpage',
            name='navigator',
            field=wagtail.fields.StreamField([('menu_item', wagtail.blocks.ListBlock(wagtail.blocks.StructBlock([('text', wagtail.blocks.CharBlock()), ('slug', wagtail.blocks.CharBlock())])))], null=True, use_json_field=True),
        ),
        migrations.AlterField(
            model_name='creatorfestpage',
            name='page_panels',
            field=wagtail.fields.StreamField([('panel', wagtail.blocks.StructBlock([('superheading', wagtail.blocks.CharBlock(required=False)), ('heading', wagtail.blocks.CharBlock()), ('background_image', wagtail.blocks.StructBlock([('image', wagtail.images.blocks.ImageChooserBlock(required=False)), ('alt_text', wagtail.blocks.CharBlock(required=False)), ('link', wagtail.blocks.URLBlock(required=False)), ('alignment', pages.custom_blocks.ImageFormatChoiceBlock()), ('identifier', wagtail.blocks.CharBlock(help_text='Used by the frontend for Google Analytics.', required=False))], required=False)), ('embed', wagtail.blocks.RawHTMLBlock(required=False)), ('paragraph', wagtail.blocks.RichTextBlock(required=False)), ('cards', wagtail.blocks.ListBlock(wagtail.blocks.StructBlock([('icon', wagtail.blocks.StructBlock([('image', wagtail.images.blocks.ImageChooserBlock(required=False)), ('alt_text', wagtail.blocks.CharBlock(required=False)), ('link', wagtail.blocks.URLBlock(required=False)), ('alignment', pages.custom_blocks.ImageFormatChoiceBlock()), ('identifier', wagtail.blocks.CharBlock(help_text='Used by the frontend for Google Analytics.', required=False))])), ('headline', wagtail.blocks.CharBlock()), ('description', wagtail.blocks.RichTextBlock())], null=True)))]))], null=True, use_json_field=True),
        ),
        migrations.AlterField(
            model_name='creatorfestpage',
            name='register',
            field=wagtail.fields.StreamField([('box', wagtail.blocks.ListBlock(wagtail.blocks.StructBlock([('headline', wagtail.blocks.CharBlock()), ('address', wagtail.blocks.RichTextBlock()), ('button_url', wagtail.blocks.URLBlock()), ('button_text', wagtail.blocks.CharBlock())])))], use_json_field=True),
        ),
        migrations.AlterField(
            model_name='faq',
            name='questions',
            field=wagtail.fields.StreamField([('question', wagtail.blocks.StructBlock([('question', wagtail.blocks.RichTextBlock(required=True)), ('slug', wagtail.blocks.CharBlock(required=True)), ('answer', wagtail.blocks.RichTextBlock(required=True)), ('document', wagtail.documents.blocks.DocumentChooserBlock(required=False))]))], use_json_field=True),
        ),
        migrations.AlterField(
            model_name='generalpage',
            name='body',
            field=wagtail.fields.StreamField([('heading', wagtail.blocks.CharBlock(form_classname='full title')), ('tagline', wagtail.blocks.CharBlock(form_classname='full title')), ('paragraph', wagtail.blocks.RichTextBlock()), ('image', pages.custom_blocks.APIImageChooserBlock()), ('html', wagtail.blocks.RawHTMLBlock())], use_json_field=True),
        ),
        migrations.AlterField(
            model_name='group',
            name='people',
            field=wagtail.fields.StreamField([('person', wagtail.blocks.StructBlock([('name', wagtail.blocks.CharBlock()), ('title', wagtail.blocks.CharBlock(required=False)), ('bio', wagtail.blocks.CharBlock(required=False)), ('photo', pages.custom_blocks.APIImageChooserBlock(required=False))], icon='user'))], use_json_field=True),
        ),
        migrations.AlterField(
            model_name='homepage',
            name='features_tab1_features',
            field=wagtail.fields.StreamField([('feature_text', wagtail.blocks.CharBlock())], use_json_field=True),
        ),
        migrations.AlterField(
            model_name='homepage',
            name='features_tab2_features',
            field=wagtail.fields.StreamField([('feature_text', wagtail.blocks.CharBlock())], use_json_field=True),
        ),
        migrations.AlterField(
            model_name='homepage',
            name='quotes',
            field=wagtail.fields.StreamField([('quote', wagtail.blocks.ListBlock(wagtail.blocks.StructBlock([('testimonial', wagtail.blocks.TextBlock(required=False)), ('author', wagtail.blocks.CharBlock(Required=False))])))], use_json_field=True),
        ),
        migrations.AlterField(
            model_name='homepage',
            name='tutor_features',
            field=wagtail.fields.StreamField([('features', wagtail.blocks.ListBlock(wagtail.blocks.StructBlock([('image', pages.custom_blocks.APIImageChooserBlock(required=False)), ('title', wagtail.blocks.CharBlock(required=False))])))], use_json_field=True),
        ),
        migrations.AlterField(
            model_name='impact',
            name='disruption',
            field=wagtail.fields.StreamField([('content', wagtail.blocks.StructBlock([('heading', wagtail.blocks.CharBlock()), ('description', wagtail.blocks.TextBlock()), ('graph', wagtail.blocks.StructBlock([('image', wagtail.blocks.StructBlock([('image', wagtail.images.blocks.ImageChooserBlock(required=False)), ('alt_text', wagtail.blocks.CharBlock(required=False)), ('link', wagtail.blocks.URLBlock(required=False)), ('alignment', pages.custom_blocks.ImageFormatChoiceBlock()), ('identifier', wagtail.blocks.CharBlock(help_text='Used by the frontend for Google Analytics.', required=False))], required=False)), ('image_alt_text', wagtail.blocks.CharBlock(required=False))]))]))], use_json_field=True),
        ),
        migrations.AlterField(
            model_name='impact',
            name='giving',
            field=wagtail.fields.StreamField([('content', wagtail.blocks.StructBlock([('heading', wagtail.blocks.CharBlock()), ('description', wagtail.blocks.TextBlock()), ('link_text', wagtail.blocks.CharBlock()), ('link_href', wagtail.blocks.URLBlock()), ('nonprofit_statement', wagtail.blocks.TextBlock()), ('annual_report_link_text', wagtail.blocks.CharBlock()), ('annual_report_link_href', wagtail.blocks.URLBlock())]))], use_json_field=True),
        ),
        migrations.AlterField(
            model_name='impact',
            name='improving_access',
            field=wagtail.fields.StreamField([('content', wagtail.blocks.StructBlock([('image', wagtail.blocks.StructBlock([('image', wagtail.images.blocks.ImageChooserBlock(required=False)), ('alt_text', wagtail.blocks.CharBlock(required=False)), ('link', wagtail.blocks.URLBlock(required=False)), ('alignment', pages.custom_blocks.ImageFormatChoiceBlock()), ('identifier', wagtail.blocks.CharBlock(help_text='Used by the frontend for Google Analytics.', required=False))])), ('heading', wagtail.blocks.CharBlock()), ('description', wagtail.blocks.RichTextBlock()), ('button_text', wagtail.blocks.CharBlock()), ('button_href', wagtail.blocks.URLBlock())]))], use_json_field=True),
        ),
        migrations.AlterField(
            model_name='impact',
            name='making_a_difference',
            field=wagtail.fields.StreamField([('content', wagtail.blocks.StructBlock([('heading', wagtail.blocks.CharBlock()), ('description', wagtail.blocks.RichTextBlock()), ('stories', wagtail.blocks.ListBlock(wagtail.blocks.StructBlock([('image', pages.custom_blocks.APIImageChooserBlock(required=False)), ('story_text', wagtail.blocks.TextBlock(required=False)), ('linked_story', wagtail.blocks.PageChooserBlock(page_type=['pages.ImpactStory'])), ('embedded_video', wagtail.blocks.RawHTMLBlock(required=False))])))]))], use_json_field=True),
        ),
        migrations.AlterField(
            model_name='impact',
            name='quote',
            field=wagtail.fields.StreamField([('content', wagtail.blocks.StructBlock([('image', wagtail.blocks.StructBlock([('image', wagtail.images.blocks.ImageChooserBlock(required=False)), ('alt_text', wagtail.blocks.CharBlock(required=False)), ('link', wagtail.blocks.URLBlock(required=False)), ('alignment', pages.custom_blocks.ImageFormatChoiceBlock()), ('identifier', wagtail.blocks.CharBlock(help_text='Used by the frontend for Google Analytics.', required=False))])), ('quote', wagtail.blocks.RichTextBlock())]))], use_json_field=True),
        ),
        migrations.AlterField(
            model_name='impact',
            name='reach',
            field=wagtail.fields.StreamField([('content', wagtail.blocks.StructBlock([('image', wagtail.blocks.StructBlock([('image', wagtail.images.blocks.ImageChooserBlock(required=False)), ('alt_text', wagtail.blocks.CharBlock(required=False)), ('link', wagtail.blocks.URLBlock(required=False)), ('alignment', pages.custom_blocks.ImageFormatChoiceBlock()), ('identifier', wagtail.blocks.CharBlock(help_text='Used by the frontend for Google Analytics.', required=False))])), ('heading', wagtail.blocks.CharBlock()), ('description', wagtail.blocks.RichTextBlock()), ('cards', wagtail.blocks.ListBlock(wagtail.blocks.StructBlock([('icon', pages.custom_blocks.APIImageChooserBlock(required=False)), ('description', wagtail.blocks.CharBlock()), ('link_text', wagtail.blocks.CharBlock(required=False)), ('link_href', wagtail.blocks.URLBlock(required=False))])))]))], use_json_field=True),
        ),
        migrations.AlterField(
            model_name='impact',
            name='supporter_community',
            field=wagtail.fields.StreamField([('content', wagtail.blocks.StructBlock([('heading', wagtail.blocks.CharBlock()), ('image', wagtail.blocks.StructBlock([('image', wagtail.images.blocks.ImageChooserBlock(required=False)), ('alt_text', wagtail.blocks.CharBlock(required=False)), ('link', wagtail.blocks.URLBlock(required=False)), ('alignment', pages.custom_blocks.ImageFormatChoiceBlock()), ('identifier', wagtail.blocks.CharBlock(help_text='Used by the frontend for Google Analytics.', required=False))])), ('quote', wagtail.blocks.RichTextBlock()), ('link_text', wagtail.blocks.CharBlock()), ('link_href', wagtail.blocks.URLBlock())]))], use_json_field=True),
        ),
        migrations.AlterField(
            model_name='impactstory',
            name='body',
            field=wagtail.fields.StreamField([('paragraph', wagtail.blocks.RichTextBlock(icon='pilcrow')), ('aligned_image', wagtail.blocks.StructBlock([('image', news.models.ImageChooserBlock()), ('caption', wagtail.blocks.RichTextBlock()), ('alignment', news.models.ImageFormatChoiceBlock()), ('alt_text', wagtail.blocks.CharBlock(required=False))], icon='image', label='Aligned image')), ('pullquote', wagtail.blocks.StructBlock([('quote', wagtail.blocks.TextBlock('quote title')), ('attribution', wagtail.blocks.CharBlock())])), ('aligned_html', wagtail.blocks.RawHTMLBlock(icon='code', label='Raw HTML')), ('document', news.models.BlogDocumentChooserBlock(icon='doc-full-inverse')), ('embed', wagtail.embeds.blocks.EmbedBlock(icon='media', label='Embed Media URL')), ('blog_cta', wagtail.blocks.StructBlock([('heading', wagtail.blocks.CharBlock()), ('description', wagtail.blocks.TextBlock()), ('button_text', wagtail.blocks.CharBlock()), ('button_href', wagtail.blocks.URLBlock()), ('alignment', news.models.CTAAlignmentChoiceBlock())], icon='form', label='Call to Action block'))], use_json_field=True),
        ),
        migrations.AlterField(
            model_name='institutionalpartnerprogrampage',
            name='section_3_tall_cards',
            field=wagtail.fields.StreamField([('card', wagtail.blocks.ListBlock(wagtail.blocks.StructBlock([('html', wagtail.blocks.RichTextBlock()), ('link', wagtail.blocks.URLBlock()), ('link_text', wagtail.blocks.CharBlock())])))], use_json_field=True),
        ),
        migrations.AlterField(
            model_name='institutionalpartnerprogrampage',
            name='section_3_wide_cards',
            field=wagtail.fields.StreamField([('card', wagtail.blocks.ListBlock(wagtail.blocks.StructBlock([('icon', wagtail.blocks.StructBlock([('image', wagtail.images.blocks.ImageChooserBlock(required=False)), ('alt_text', wagtail.blocks.CharBlock(required=False)), ('link', wagtail.blocks.URLBlock(required=False)), ('alignment', pages.custom_blocks.ImageFormatChoiceBlock()), ('identifier', wagtail.blocks.CharBlock(help_text='Used by the frontend for Google Analytics.', required=False))])), ('html', wagtail.blocks.RichTextBlock())])))], use_json_field=True),
        ),
        migrations.AlterField(
            model_name='institutionalpartnerprogrampage',
            name='section_6_cards',
            field=wagtail.fields.StreamField([('card', wagtail.blocks.ListBlock(wagtail.blocks.StructBlock([('heading_number', wagtail.blocks.CharBlock()), ('heading_unit', wagtail.blocks.CharBlock()), ('description', wagtail.blocks.CharBlock())])))], use_json_field=True),
        ),
        migrations.AlterField(
            model_name='institutionalpartnerprogrampage',
            name='section_7_icons',
            field=wagtail.fields.StreamField([('card', wagtail.blocks.ListBlock(wagtail.blocks.StructBlock([('image', wagtail.blocks.StructBlock([('image', wagtail.images.blocks.ImageChooserBlock(required=False)), ('alt_text', wagtail.blocks.CharBlock(required=False)), ('link', wagtail.blocks.URLBlock(required=False)), ('alignment', pages.custom_blocks.ImageFormatChoiceBlock()), ('identifier', wagtail.blocks.CharBlock(help_text='Used by the frontend for Google Analytics.', required=False))])), ('image_alt_text', wagtail.blocks.CharBlock()), ('current_cohort', wagtail.blocks.BooleanBlock(required=False))])))], use_json_field=True),
        ),
        migrations.AlterField(
            model_name='institutionalpartnership',
            name='program_tab_content',
            field=wagtail.fields.StreamField([('tab', wagtail.blocks.ListBlock(wagtail.blocks.StructBlock([('heading', wagtail.blocks.CharBlock()), ('description', wagtail.blocks.RichTextBlock())])))], null=True, use_json_field=True),
        ),
        migrations.AlterField(
            model_name='mappage',
            name='section_1_cards',
            field=wagtail.fields.StreamField([('card', wagtail.blocks.StructBlock([('image', wagtail.blocks.StructBlock([('image', wagtail.images.blocks.ImageChooserBlock(required=False)), ('alt_text', wagtail.blocks.CharBlock(required=False)), ('link', wagtail.blocks.URLBlock(required=False)), ('alignment', pages.custom_blocks.ImageFormatChoiceBlock()), ('identifier', wagtail.blocks.CharBlock(help_text='Used by the frontend for Google Analytics.', required=False))])), ('number', wagtail.blocks.CharBlock(required=False)), ('unit', wagtail.blocks.CharBlock(required=False)), ('description', wagtail.blocks.TextBlock(required=False))], icon='document'))], null=True, use_json_field=True),
        ),
        migrations.AlterField(
            model_name='mathquizpage',
            name='results',
            field=wagtail.fields.StreamField([('result', wagtail.blocks.ListBlock(wagtail.blocks.StructBlock([('image', wagtail.blocks.StructBlock([('image', wagtail.images.blocks.ImageChooserBlock(required=False)), ('alt_text', wagtail.blocks.CharBlock(required=False)), ('link', wagtail.blocks.URLBlock(required=False)), ('alignment', pages.custom_blocks.ImageFormatChoiceBlock()), ('identifier', wagtail.blocks.CharBlock(help_text='Used by the frontend for Google Analytics.', required=False))])), ('headline', wagtail.blocks.CharBlock()), ('description', wagtail.blocks.TextBlock()), ('partners', wagtail.blocks.ListBlock(wagtail.blocks.StructBlock([('partner', pages.models.PartnerChooserBlock())])))])))], use_json_field=True),
        ),
        migrations.AlterField(
            model_name='printorder',
            name='featured_providers',
            field=wagtail.fields.StreamField([('provider', wagtail.blocks.StructBlock([('name', wagtail.blocks.CharBlock()), ('blurb', wagtail.blocks.TextBlock(required=False)), ('icon', wagtail.images.blocks.ImageChooserBlock()), ('cta', wagtail.blocks.CharBlock()), ('url', wagtail.blocks.URLBlock()), ('canadian', wagtail.blocks.BooleanBlock(required=False))], icon='document'))], null=True, use_json_field=True),
        ),
        migrations.AlterField(
            model_name='printorder',
            name='providers',
            field=wagtail.fields.StreamField([('provider', wagtail.blocks.StructBlock([('name', wagtail.blocks.CharBlock()), ('blurb', wagtail.blocks.TextBlock(required=False)), ('icon', wagtail.images.blocks.ImageChooserBlock()), ('cta', wagtail.blocks.CharBlock()), ('url', wagtail.blocks.URLBlock()), ('canadian', wagtail.blocks.BooleanBlock(required=False))], icon='document'))], use_json_field=True),
        ),
        migrations.AlterField(
            model_name='researchpage',
            name='alumni',
            field=wagtail.fields.StreamField([('person', wagtail.blocks.StructBlock([('name', wagtail.blocks.CharBlock()), ('title', wagtail.blocks.CharBlock()), ('website', wagtail.blocks.URLBlock(required=False))], icon='user'))], blank=True, null=True, use_json_field=True),
        ),
        migrations.AlterField(
            model_name='researchpage',
            name='current_members',
            field=wagtail.fields.StreamField([('person', wagtail.blocks.StructBlock([('name', wagtail.blocks.CharBlock()), ('title', wagtail.blocks.CharBlock()), ('photo', pages.custom_blocks.APIImageChooserBlock(required=False)), ('website', wagtail.blocks.URLBlock(required=False))], icon='user'))], blank=True, null=True, use_json_field=True),
        ),
        migrations.AlterField(
            model_name='researchpage',
            name='external_collaborators',
            field=wagtail.fields.StreamField([('person', wagtail.blocks.StructBlock([('name', wagtail.blocks.CharBlock()), ('title', wagtail.blocks.CharBlock()), ('photo', pages.custom_blocks.APIImageChooserBlock(required=False)), ('website', wagtail.blocks.URLBlock(required=False))], icon='user'))], blank=True, null=True, use_json_field=True),
        ),
        migrations.AlterField(
            model_name='researchpage',
            name='projects',
            field=wagtail.fields.StreamField([('project', wagtail.blocks.StructBlock([('title', wagtail.blocks.CharBlock()), ('blurb', wagtail.blocks.TextBlock()), ('link', wagtail.blocks.URLBlock(help_text='Optional link to project.', required=False))], icon='user'))], blank=True, null=True, use_json_field=True),
        ),
        migrations.AlterField(
            model_name='researchpage',
            name='publications',
            field=wagtail.fields.StreamField([('publication', wagtail.blocks.StructBlock([('authors', wagtail.blocks.CharBlock()), ('date', wagtail.blocks.DateBlock()), ('title', wagtail.blocks.CharBlock()), ('excerpt', wagtail.blocks.CharBlock()), ('download_url', wagtail.blocks.URLBlock())], icon='user'))], blank=True, null=True, use_json_field=True),
        ),
        migrations.AlterField(
            model_name='subject',
            name='about_os',
            field=wagtail.fields.StreamField([('content', wagtail.blocks.StructBlock([('heading', wagtail.blocks.CharBlock()), ('image', pages.custom_blocks.APIImageChooserBlock()), ('os_text', wagtail.blocks.TextBlock()), ('link_text', wagtail.blocks.CharBlock()), ('link_href', wagtail.blocks.URLBlock())]))], use_json_field=True),
        ),
        migrations.AlterField(
            model_name='subject',
            name='blog_header',
            field=wagtail.fields.StreamField([('content', wagtail.blocks.StructBlock([('heading', wagtail.blocks.CharBlock()), ('blog_description', wagtail.blocks.TextBlock()), ('link_text', wagtail.blocks.CharBlock()), ('link_href', wagtail.blocks.URLBlock())]))], use_json_field=True),
        ),
        migrations.AlterField(
            model_name='subject',
            name='info_boxes',
            field=wagtail.fields.StreamField([('info_box', wagtail.blocks.ListBlock(wagtail.blocks.StructBlock([('image', pages.custom_blocks.APIImageChooserBlock()), ('heading', wagtail.blocks.CharBlock()), ('text', wagtail.blocks.CharBlock())])))], use_json_field=True),
        ),
        migrations.AlterField(
            model_name='subject',
            name='os_textbook_categories',
            field=wagtail.fields.StreamField([('category', wagtail.blocks.ListBlock(wagtail.blocks.StructBlock([('heading', wagtail.blocks.CharBlock()), ('text', wagtail.blocks.TextBlock())])))], blank=True, null=True, use_json_field=True),
        ),
        migrations.AlterField(
            model_name='subject',
            name='translations',
            field=wagtail.fields.StreamField([('translation', wagtail.blocks.ListBlock(wagtail.blocks.StructBlock([('locale', wagtail.blocks.CharBlock()), ('slug', wagtail.blocks.CharBlock())])))], blank=True, null=True, use_json_field=True),
        ),
        migrations.AlterField(
            model_name='subject',
            name='tutor_ad',
            field=wagtail.fields.StreamField([('content', wagtail.blocks.StructBlock([('heading', wagtail.blocks.CharBlock()), ('image', pages.custom_blocks.APIImageChooserBlock()), ('ad_html', wagtail.blocks.TextBlock()), ('link_text', wagtail.blocks.CharBlock()), ('link_href', wagtail.blocks.URLBlock())]))], blank=True, null=True, use_json_field=True),
        ),
        migrations.AlterField(
            model_name='subject',
            name='webinar_header',
            field=wagtail.fields.StreamField([('content', wagtail.blocks.StructBlock([('heading', wagtail.blocks.CharBlock()), ('webinar_description', wagtail.blocks.TextBlock()), ('link_text', wagtail.blocks.CharBlock()), ('link_href', wagtail.blocks.URLBlock())]))], use_json_field=True),
        ),
        migrations.AlterField(
            model_name='subjects',
            name='about_os',
            field=wagtail.fields.StreamField([('content', wagtail.blocks.StructBlock([('heading', wagtail.blocks.CharBlock()), ('image', pages.custom_blocks.APIImageChooserBlock()), ('os_text', wagtail.blocks.TextBlock()), ('link_text', wagtail.blocks.CharBlock()), ('link_href', wagtail.blocks.URLBlock())]))], use_json_field=True),
        ),
        migrations.AlterField(
            model_name='subjects',
            name='info_boxes',
            field=wagtail.fields.StreamField([('info_box', wagtail.blocks.ListBlock(wagtail.blocks.StructBlock([('image', pages.custom_blocks.APIImageChooserBlock()), ('heading', wagtail.blocks.CharBlock()), ('text', wagtail.blocks.CharBlock())])))], use_json_field=True),
        ),
        migrations.AlterField(
            model_name='subjects',
            name='translations',
            field=wagtail.fields.StreamField([('translation', wagtail.blocks.ListBlock(wagtail.blocks.StructBlock([('locale', wagtail.blocks.CharBlock()), ('slug', wagtail.blocks.CharBlock())])))], blank=True, null=True, use_json_field=True),
        ),
        migrations.AlterField(
            model_name='subjects',
            name='tutor_ad',
            field=wagtail.fields.StreamField([('content', wagtail.blocks.StructBlock([('heading', wagtail.blocks.CharBlock()), ('image', pages.custom_blocks.APIImageChooserBlock()), ('ad_html', wagtail.blocks.TextBlock()), ('link_text', wagtail.blocks.CharBlock()), ('link_href', wagtail.blocks.URLBlock())]))], use_json_field=True),
        ),
        migrations.AlterField(
            model_name='supporters',
            name='funder_groups',
            field=wagtail.fields.StreamField([('content', wagtail.blocks.StructBlock([('group_title', wagtail.blocks.CharBlock(form_classname='name of funder group')), ('description', wagtail.blocks.TextBlock(form_classname='description of funder group')), ('image', pages.custom_blocks.APIImageChooserBlock(required=False)), ('funders', wagtail.blocks.ListBlock(wagtail.blocks.StructBlock([('funder_name', wagtail.blocks.CharBlock(required=True)), ('url', wagtail.blocks.URLBlock(required=False))])))]))], use_json_field=True),
        ),
        migrations.AlterField(
            model_name='tutormarketing',
            name='cost_cards',
            field=wagtail.fields.StreamField([('cards', wagtail.blocks.StructBlock([('title', wagtail.blocks.CharBlock(required=True)), ('description', wagtail.blocks.RichTextBlock(required=True))]))], use_json_field=True),
        ),
        migrations.AlterField(
            model_name='tutormarketing',
            name='faqs',
            field=wagtail.fields.StreamField([('faq', wagtail.blocks.StructBlock([('question', wagtail.blocks.RichTextBlock(required=True)), ('slug', wagtail.blocks.CharBlock(required=True)), ('answer', wagtail.blocks.RichTextBlock(required=True)), ('document', wagtail.documents.blocks.DocumentChooserBlock(required=False))]))], use_json_field=True),
        ),
        migrations.AlterField(
            model_name='tutormarketing',
            name='features_cards',
            field=wagtail.fields.StreamField([('cards', wagtail.blocks.StructBlock([('icon', pages.custom_blocks.APIImageChooserBlock(required=False)), ('title', wagtail.blocks.CharBlock(required=True)), ('description', wagtail.blocks.RichTextBlock(required=True))]))], use_json_field=True),
        ),
        migrations.AlterField(
            model_name='tutormarketing',
            name='feedback_media',
            field=wagtail.fields.StreamField([('image', wagtail.blocks.StructBlock([('image', wagtail.images.blocks.ImageChooserBlock(required=False)), ('alt_text', wagtail.blocks.CharBlock(required=False)), ('link', wagtail.blocks.URLBlock(required=False)), ('alignment', pages.custom_blocks.ImageFormatChoiceBlock()), ('identifier', wagtail.blocks.CharBlock(help_text='Used by the frontend for Google Analytics.', required=False))])), ('video', wagtail.blocks.RawHTMLBlock())], use_json_field=True),
        ),
    ]