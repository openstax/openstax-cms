from bs4 import BeautifulSoup

from django.db import models
from django import forms

from wagtail.models import Page, Orderable
from wagtail.fields import RichTextField, StreamField
from wagtail.admin.panels import FieldPanel, InlinePanel
from wagtail_ai.panels import AIMultipleChooserPanel
from wagtail.admin.widgets.slug import SlugInput
from wagtail.embeds.blocks import EmbedBlock
from wagtail.search import index
from wagtail import blocks
from wagtail.blocks import TextBlock, StructBlock, StreamBlock, FieldBlock, CharBlock, RichTextBlock, RawHTMLBlock, BooleanBlock
from wagtail.images.blocks import ImageChooserBlock
from wagtail.documents.blocks import DocumentChooserBlock
from wagtail.snippets.blocks import SnippetChooserBlock
from wagtail_ai.blocks import ai_image_block
from wagtail.api import APIField
from wagtail.images.api.fields import ImageRenditionField
from wagtail.models import Site

from modelcluster.fields import ParentalKey
from modelcluster.contrib.taggit import ClusterTaggableManager
from taggit.models import TaggedItemBase
from openstax.functions import build_image_url
from openstax.preview import FrontendPreviewMixin
from snippets.models import NewsSource, BlogContentType, BlogCollection, Subject
from pages.custom_blocks import APIImageChooserBlock, FAQBlock


class ImageChooserBlock(ImageChooserBlock):
    def get_api_representation(self, value, context=None):
        if value:
            return {
                'id': value.id,
                'title': value.title,
                'original': value.get_rendition('original').attrs_dict,
            }

class PullQuoteBlock(StructBlock):
    quote = TextBlock("quote title")
    attribution = CharBlock()

    class Meta:
        icon = "openquote"


class ImageFormatChoiceBlock(FieldBlock):
    field = forms.ChoiceField(choices=(
        ('left 1/3', 'Wrap left 1/3'),
        ('left 1/2', 'Wrap left 1/2'),
        ('right 1/3', 'Wrap right 1/3'),
        ('right 1/2', 'Wrap right 1/2'),
        ('left', 'Wrap left'),
        ('right', 'Wrap right'),
        ('mid', 'Mid width'),
        ('full', 'Full width'),
    ))

class CTAAlignmentChoiceBlock(FieldBlock):
    field = forms.ChoiceField(choices=(
        ('left 1/3', 'Wrap left 1/3'),
        ('left 1/2', 'Wrap left 1/2'),
        ('right 1/3', 'Wrap right 1/3'),
        ('right 1/2', 'Wrap right 1/2'),
        ('full', 'Full width'),
        ('bottom', 'Bottom of post'),
    ))


@ai_image_block()
class ImageBlock(StructBlock):
    image = ImageChooserBlock()
    caption = RichTextBlock()
    alignment = ImageFormatChoiceBlock()
    alt_text = blocks.CharBlock(required=False)

class BlogCTABlock(StructBlock):
    heading = blocks.CharBlock()
    description = blocks.TextBlock()
    button_text = blocks.CharBlock()
    button_href = blocks.URLBlock()
    alignment = CTAAlignmentChoiceBlock()


class BlogDocumentChooserBlock(DocumentChooserBlock):
    def get_api_representation(self, value, context=None):
        if value:
            return {
                'title': value.title,
                'download_url': value.url,
            }


class BlogStreamBlock(StreamBlock):
    paragraph = RichTextBlock(icon="pilcrow")
    aligned_image = ImageBlock(label="Aligned image", icon="image")
    pullquote = PullQuoteBlock()
    aligned_html = RawHTMLBlock(icon="code", label='Raw HTML')
    document = BlogDocumentChooserBlock(icon="doc-full-inverse")
    embed = EmbedBlock(icon="media", label="Embed Media URL")
    blog_cta = BlogCTABlock(icon="form", label="Call to Action block")


class BlogCollectionChooserBlock(SnippetChooserBlock):
    def get_api_representation(self, value, context=None):
        if value:
            return {
                'name': value.name,
            }


class SubjectChooserBlock(SnippetChooserBlock):
    def get_api_representation(self, value, context=None):
        if value:
            return {
                'name': value.name,
            }


class ContentTypeChooserBlock(SnippetChooserBlock):
    def get_api_representation(self, value, context=None):
        if value:
            return {
                'content_type': value.content_type,
            }


class SubjectBlock(StructBlock):
    subject = BlogCollectionChooserBlock(required=True, label='Blog Subject', target_model='snippets.Subject')
    featured = BooleanBlock(label="Featured", required=False)


class BlogCollectionBlock(StructBlock):
    collection = BlogCollectionChooserBlock(required=True, label='Blog Collection', target_model='snippets.BlogCollection')
    featured = BooleanBlock(label="Featured", required=False)
    popular = BooleanBlock(label="Popular", required=False)


class BlogContentTypeBlock(StructBlock):
    content_type = ContentTypeChooserBlock(required=True, label='Blog Content Type', target_model='snippets.BlogContentType')


class NewsIndex(FrontendPreviewMixin, Page):
    interest_block = StreamField([
            ('heading', blocks.CharBlock()),
            ('description', blocks.TextBlock()),
            ('button_text', blocks.CharBlock()),
            ('button_href', blocks.URLBlock())
         ], null=True, use_json_field=True)
    footer_text = models.CharField(max_length=255, blank=True, null=True)
    footer_link = models.URLField(blank=True, null=True)
    footer_button_text = models.CharField(max_length=255, blank=True, null=True)
    display_footer = models.BooleanField(default=False)
    promote_image = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )

    content_panels = Page.content_panels + [
        FieldPanel('interest_block'),
        FieldPanel('footer_text'),
        FieldPanel('footer_link'),
        FieldPanel('footer_button_text'),
        FieldPanel('display_footer'),
    ]

    promote_panels = [
        FieldPanel('slug', widget=SlugInput),
        FieldPanel('seo_title'),
        FieldPanel('search_description'),
        FieldPanel('promote_image')
    ]

    api_fields = [
        APIField('interest_block'),
        APIField('footer_text'),
        APIField('footer_link'),
        APIField('footer_button_text'),
        APIField('display_footer'),
        APIField('slug'),
        APIField('seo_title'),
        APIField('search_description'),
        APIField('promote_image')
    ]

    subpage_types = ['news.NewsArticle']
    parent_page_types = ['pages.HomePage', 'pages.RootPage']
    max_count = 1

    def get_url_parts(self, *args, **kwargs):
        url_parts = super().get_url_parts(*args, **kwargs)

        if url_parts is None:
            return None
        
        # note that we ignore the slug and hardcode this url to /blog
        site_id, site_root_url, page_url_relative_to_site_root = url_parts
        return (site_id, site_root_url, '/blog')



class NewsArticleTag(TaggedItemBase):
    content_object = ParentalKey('news.NewsArticle', related_name='tagged_items')


class NewsArticleRelatedPage(Orderable):
    page = ParentalKey('news.NewsArticle', related_name='related_pages', on_delete=models.CASCADE)
    related_page = models.ForeignKey('wagtailcore.Page', on_delete=models.CASCADE, related_name='+')


class NewsArticle(FrontendPreviewMixin, Page):
    date = models.DateField("Post date")
    heading = models.CharField(max_length=250, help_text="Heading displayed on website")
    subheading = models.CharField(max_length=250, blank=True, null=True)
    author = models.CharField(max_length=250)
    featured_image = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
        help_text="Image should be 1200 x 600"
    )
    featured_image_alt_text = models.CharField(max_length=250, blank=True, null=True)
    featured_video = StreamField([
        ('video', blocks.RawHTMLBlock()),
        ], null=True, blank=True, use_json_field=True)
    def get_article_image(self):
        return build_image_url(self.featured_image)
    article_image = property(get_article_image)
    tags = ClusterTaggableManager(through=NewsArticleTag, blank=True)
    body = StreamField(BlogStreamBlock(), use_json_field=True)
    pin_to_top = models.BooleanField(default=False)
    gated_content = models.BooleanField(default=False)
    collections = StreamField(blocks.StreamBlock([
            ('collection', blocks.ListBlock(BlogCollectionBlock())
             )]), null=True, blank=True, use_json_field=True)
    article_subjects = StreamField(blocks.StreamBlock([
            ('subject', blocks.ListBlock(SubjectBlock())
             )]), null=True, blank=True, use_json_field=True)
    content_types = StreamField(blocks.StreamBlock([
        ('content_type', blocks.ListBlock(BlogContentTypeBlock())
         )]), null=True, blank=True, use_json_field=True)
    promote_image = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )

    @property
    def body_blurb(self):
        paragraphs = []
        for block in self.body:
            if block.block_type == 'paragraph':
                paragraphs.append(str(block.value))

        first_paragraph_parsed = []
        if len(paragraphs) > 0:
            soup = BeautifulSoup(paragraphs[0], "html.parser")
            for tag in soup.findAll('p'):
                first_paragraph_parsed.append(tag)

            return str(first_paragraph_parsed[0])
        else:
            return ''

    @property
    def blog_content_types(self):
        prep_value = self.content_types.get_prep_value()
        types = []
        for t in prep_value:
            if len(t['value']) > 0:
                if 'value' in t['value'][0]:
                    type_id = t['value'][0]['value']['content_type']
                    type = BlogContentType.objects.filter(id=type_id)
                    types.append(str(type[0]))
        return types

    @property
    def blog_subjects(self):
        prep_value = self.article_subjects.get_prep_value()
        subjects = []
        for s in prep_value:
            if len(s['value']) > 0:
                if 'value' in s['value'][0]:
                    subject_id = s['value'][0]['value']['subject']
                    featured = s['value'][0]['value']['featured']
                    subject = Subject.objects.filter(id=subject_id)
                    data = {'name': str(subject[0]), 'featured': featured}
                    subjects.append(data)
        return subjects

    @property
    def blog_collections(self):
        prep_value = self.collections.get_prep_value()
        cols = []
        for c in prep_value:
            if len(c['value']) > 0:
                if 'value' in c['value'][0]:
                    collection_id = c['value'][0]['value']['collection']
                    featured = c['value'][0]['value']['featured']
                    popular = c['value'][0]['value']['popular']
                    collection = BlogCollection.objects.filter(id=collection_id)
                    data = {'name': str(collection[0]), 'featured': featured, 'popular': popular}
                    cols.append(data)
        return cols

    def search_subject_names(self):
        prep_value = self.article_subjects.get_prep_value() or []
        subject_ids = [
            item.get('value', {}).get('subject')
            for block in prep_value
            for item in (block.get('value') or [])
            if item.get('value', {}).get('subject') is not None
        ]
        if not subject_ids:
            return ''
        subjects = Subject.objects.in_bulk(subject_ids)
        return ' '.join(str(subjects[sid]) for sid in subject_ids if sid in subjects)

    def search_collection_names(self):
        prep_value = self.collections.get_prep_value() or []
        collection_ids = [
            item.get('value', {}).get('collection')
            for block in prep_value
            for item in (block.get('value') or [])
            if item.get('value', {}).get('collection') is not None
        ]
        if not collection_ids:
            return ''
        collections = BlogCollection.objects.in_bulk(collection_ids)
        return ' '.join(str(collections[cid]) for cid in collection_ids if cid in collections)

    def search_content_type_names(self):
        prep_value = self.content_types.get_prep_value() or []
        content_type_ids = [
            item.get('value', {}).get('content_type')
            for block in prep_value
            for item in (block.get('value') or [])
            if item.get('value', {}).get('content_type') is not None
        ]
        if not content_type_ids:
            return ''
        types = BlogContentType.objects.in_bulk(content_type_ids)
        return ' '.join(str(types[tid]) for tid in content_type_ids if tid in types)

    search_fields = Page.search_fields + [
        index.SearchField('search_subject_names', boost=5),
        index.SearchField('search_collection_names', boost=2),
        index.SearchField('author', boost=2),
        index.SearchField('body'),
        index.SearchField('search_content_type_names'),
        index.RelatedFields('tags', [index.SearchField('name')]),
    ]

    content_panels = Page.content_panels + [
        FieldPanel('date'),
        FieldPanel('title'),
        FieldPanel('heading'),
        FieldPanel('subheading'),
        FieldPanel('author'),
        FieldPanel('featured_image'),
        FieldPanel('featured_video'),
        FieldPanel('featured_image_alt_text'),
        FieldPanel('tags'),
        FieldPanel('body'),
        FieldPanel('pin_to_top'),
        FieldPanel('gated_content'),
        FieldPanel('collections'),
        FieldPanel('article_subjects'),
        FieldPanel('content_types'),
        AIMultipleChooserPanel(
            'related_pages',
            chooser_field_name='related_page',
            vector_index='PageVectorIndex',
            label='Related pages',
        ),
    ]

    promote_panels = [
        FieldPanel('slug', widget=SlugInput),
        FieldPanel('seo_title'),
        FieldPanel('search_description'),
        FieldPanel('promote_image')
    ]

    api_fields = [
        APIField('date'),
        APIField('title'),
        APIField('heading'),
        APIField('subheading'),
        APIField('author'),
        APIField('article_image'),
        APIField('featured_image_small', serializer=ImageRenditionField('width-420', source='featured_image')),
        APIField('featured_image_alt_text'),
        APIField('featured_video'),
        APIField('tags'),
        APIField('body_blurb'),
        APIField('body'),
        APIField('pin_to_top'),
        APIField('gated_content'),
        APIField('slug'),
        APIField('seo_title'),
        APIField('search_description'),
        APIField('collections'),
        APIField('article_subjects'),
        APIField('content_types'),
        APIField('promote_image')
    ]

    parent_page_types = ['news.NewsIndex']

    def save(self, *args, **kwargs):
        if self.pin_to_top:
            current_pins = self.__class__.objects.filter(pin_to_top=True)
            for pin in current_pins:
                if pin != self:
                    pin.pin_to_top = False
                    pin.save()

        return super(NewsArticle, self).save(*args, **kwargs)

    def get_url_parts(self, *args, **kwargs):
        url_parts = super().get_url_parts(*args, **kwargs)

        if url_parts is None:
            return None

        site_id, site_root_url, page_url_relative_to_site_root = url_parts
        return (site_id, site_root_url, '/blog/{}'.format(self.slug))


class Experts(models.Model):
    name = models.CharField(max_length=255)
    email = models.EmailField(blank=True, null=True)
    title = models.CharField(max_length=255)
    bio = models.TextField()
    image = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
    )

    def get_expert_image(self):
        return build_image_url(self.image)
    expert_image = property(get_expert_image)

    api_fields = [
        APIField('name'),
        APIField('email'),
        APIField('title'),
        APIField('bio'),
        APIField('expert_image')
    ]

    panels = [
        FieldPanel('name'),
        FieldPanel('email'),
        FieldPanel('title'),
        FieldPanel('bio'),
        FieldPanel('image'),
    ]


class ExpertsBios(Orderable, Experts):
    experts_bios = ParentalKey('news.PressIndex', related_name='experts_bios')


class NewsMentionChooserBlock(SnippetChooserBlock):
    def get_api_representation(self, value, context=None):
        if value:
            return {
                'id': value.id,
                'name': value.name,
                'logo': value.news_logo,
            }


class NewsMentionBlock(blocks.StructBlock):
    source = NewsMentionChooserBlock(NewsSource)
    url = blocks.URLBlock()
    headline = blocks.CharBlock()
    date = blocks.DateBlock()
    featured_in = blocks.BooleanBlock(required=False, default=False, help_text="Check if displayed in Featured In section")

    class Meta:
        icon = 'document'


class MissionStatement(models.Model):
    statement = models.CharField(max_length=255)

    api_fields = ('statement', )


class MissionStatements(Orderable, MissionStatement):
    mission_statements = ParentalKey('news.PressIndex', related_name='mission_statements')


class PressIndex(FrontendPreviewMixin, Page):
    press_kit = models.ForeignKey(
        'wagtaildocs.Document',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )

    def get_press_kit(self):
        return build_image_url(self.press_kit)
    press_kit_url = property(get_press_kit)

    about = RichTextField(blank=True, null=True)
    press_inquiry_name = models.CharField(max_length=255, blank=True, null=True)
    press_inquiry_phone = models.CharField(max_length=255)
    press_inquiry_email = models.EmailField()
    experts_heading = models.CharField(max_length=255)
    experts_blurb = models.TextField()
    infographic_image = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
    )
    infographic_text = models.TextField(default='', blank=True)
    testimonials = StreamField(
        blocks.StreamBlock([
            ('testimonial', blocks.ListBlock(blocks.StructBlock([
                ('image', APIImageChooserBlock(required=False)),
                ('testimonial', blocks.TextBlock(required=False)),
            ])))]), blank=True, null=True, use_json_field=True)
    faqs = StreamField([
        ('faq', FAQBlock()),
    ], blank=True, null=True, use_json_field=True)
    mentions = StreamField([
        ('mention', NewsMentionBlock(icon='document')),
    ], null=True, use_json_field=True)
    promote_image = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )

    def get_url_parts(self, *args, **kwargs):
        url_parts = super().get_url_parts(*args, **kwargs)

        if url_parts is None:
            return None

        # note that we ignore the slug and hardcode this url to /press
        site_id, site_root_url, page_url_relative_to_site_root = url_parts
        return (site_id, site_root_url, '/press')

    @property
    def releases(self):
        releases = PressRelease.objects.live().child_of(self)
        releases_data = {}
        for release in releases:
            releases_data['press/{}'.format(release.slug)] = {
                'detail_url': '/apps/cms/api/v2/pages/{}/'.format(release.pk),
                'date': release.date,
                'heading': release.heading,
                'excerpt': release.excerpt,
                'author': release.author,
            }
        return releases_data

    content_panels = Page.content_panels + [
        FieldPanel('press_kit'),
        FieldPanel('about'),
        FieldPanel('press_inquiry_name'),
        FieldPanel('press_inquiry_phone'),
        FieldPanel('press_inquiry_email'),
        FieldPanel('experts_heading'),
        FieldPanel('experts_blurb'),
        InlinePanel('experts_bios', label="Experts"),
        FieldPanel('infographic_image'),
        FieldPanel('infographic_text'),
        FieldPanel('testimonials'),
        FieldPanel('faqs'),
        FieldPanel('mentions'),
        InlinePanel('mission_statements', label="Mission Statement"),
    ]

    promote_panels = [
        FieldPanel('slug', widget=SlugInput),
        FieldPanel('seo_title'),
        FieldPanel('search_description'),
        FieldPanel('promote_image')
    ]

    api_fields = [
        APIField('press_kit'),
        APIField('press_kit_url'),
        APIField('about'),
        APIField('releases'),
        APIField('slug'),
        APIField('seo_title'),
        APIField('search_description'),
        APIField('promote_image'),
        APIField('experts_heading'),
        APIField('experts_blurb'),
        APIField('experts_bios'),
        APIField('infographic_image'),
        APIField('infographic_text'),
        APIField('testimonials'),
        APIField('faqs'),
        APIField('mentions'),
        APIField('mission_statements'),
        APIField('press_inquiry_name'),
        APIField('press_inquiry_phone'),
        APIField('press_inquiry_email')
    ]

    subpage_types = ['news.PressRelease']
    parent_page_types = ['pages.HomePage', 'pages.RootPage']
    max_count = 1


class PressRelease(FrontendPreviewMixin, Page):
    date = models.DateField("PR date")
    heading = models.CharField(max_length=250, help_text="Heading displayed on website")
    subheading = models.CharField(max_length=250, blank=True, null=True)
    author = models.CharField(max_length=250)

    featured_image = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
    )
    featured_image_alt_text = models.CharField(max_length=250, blank=True, null=True)

    def get_article_image(self):
        return build_image_url(self.featured_image)
    article_image = property(get_article_image)
    excerpt = models.CharField(max_length=255)

    body = StreamField(BlogStreamBlock(), use_json_field=True)

    promote_image = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )

    def get_url_parts(self, *args, **kwargs):
        url_parts = super().get_url_parts(*args, **kwargs)

        if url_parts is None:
            return None

        site_id, site_root_url, page_url_relative_to_site_root = url_parts
        return site_id, site_root_url, '/press/{}'.format(self.slug)

    search_fields = Page.search_fields + [
        index.SearchField('body'),
    ]

    content_panels = Page.content_panels + [
        FieldPanel('date'),
        FieldPanel('title'),
        FieldPanel('heading'),
        FieldPanel('subheading'),
        FieldPanel('author'),
        FieldPanel('featured_image'),
        FieldPanel('featured_image_alt_text'),
        FieldPanel('excerpt'),
        FieldPanel('body'),
    ]

    promote_panels = [
        FieldPanel('slug', widget=SlugInput),
        FieldPanel('seo_title'),
        FieldPanel('search_description'),
        FieldPanel('promote_image')
    ]

    api_fields = [
        APIField('date'),
        APIField('title'),
        APIField('heading'),
        APIField('subheading'),
        APIField('author'),
        APIField('article_image'),
        APIField('featured_image_alt_text'),
        APIField('excerpt'),
        APIField('body'),
        APIField('slug'),
        APIField('seo_title'),
        APIField('search_description'),
        APIField('promote_image')
    ]
