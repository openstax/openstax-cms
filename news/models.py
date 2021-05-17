from bs4 import BeautifulSoup

from django.db import models
from django import forms

from wagtail.core.models import Page, Orderable
from wagtail.core.fields import RichTextField, StreamField
from wagtail.admin.edit_handlers import FieldPanel, StreamFieldPanel, InlinePanel
from wagtail.images.edit_handlers import ImageChooserPanel
from wagtail.documents.edit_handlers import DocumentChooserPanel
from wagtail.embeds.blocks import EmbedBlock
from wagtail.search import index
from wagtail.core import blocks
from wagtail.core.blocks import TextBlock, StructBlock, StreamBlock, FieldBlock, CharBlock, RichTextBlock, RawHTMLBlock
from wagtail.images.blocks import ImageChooserBlock
from wagtail.documents.blocks import DocumentChooserBlock
from wagtail.snippets.blocks import SnippetChooserBlock
from wagtail.snippets.edit_handlers import SnippetChooserPanel
from wagtail.snippets.models import register_snippet
from wagtail.api import APIField
from wagtail.images.api.fields import ImageRenditionField
from wagtail.core.models import Site

from modelcluster.fields import ParentalKey
from modelcluster.contrib.taggit import ClusterTaggableManager
from taggit.models import TaggedItemBase
from openstax.functions import build_image_url
from snippets.models import NewsSource

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
        ('left', 'Wrap left'), ('right', 'Wrap right'), ('mid', 'Mid width'), ('full', 'Full width'),
    ))


class ImageBlock(StructBlock):
    image = ImageChooserBlock()
    caption = RichTextBlock()
    alignment = ImageFormatChoiceBlock()
    alt_text = blocks.CharBlock(required=False)


class BlogStreamBlock(StreamBlock):
    paragraph = RichTextBlock(icon="pilcrow")
    aligned_image = ImageBlock(label="Aligned image", icon="image")
    pullquote = PullQuoteBlock()
    aligned_html = RawHTMLBlock(icon="code", label='Raw HTML')
    document = DocumentChooserBlock(icon="doc-full-inverse")
    embed = EmbedBlock(icon="media", label="Embed Media URL")


class NewsIndex(Page):
    intro = RichTextField(blank=True)
    press_kit = models.ForeignKey(
        'wagtaildocs.Document',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )
    promote_image = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )

    content_panels = Page.content_panels + [
        FieldPanel('intro', classname="full"),
        DocumentChooserPanel('press_kit'),
    ]

    promote_panels = [
        FieldPanel('slug'),
        FieldPanel('seo_title'),
        FieldPanel('search_description'),
        ImageChooserPanel('promote_image')
    ]

    api_fields = [
        APIField('intro'),
        APIField('press_kit'),
        APIField('slug'),
        APIField('seo_title'),
        APIField('search_description'),
        APIField('promote_image')
    ]

    subpage_types = ['news.NewsArticle']
    parent_page_types = ['pages.HomePage']
    max_count = 1

    def get_sitemap_urls(self, request=None):
        return [
            {
                'location': '{}/blog/'.format(Site.find_for_request(request).root_url),
                'lastmod': (self.last_published_at or self.latest_revision_created_at),
            }
        ]



class NewsArticleTag(TaggedItemBase):
    content_object = ParentalKey('news.NewsArticle', related_name='tagged_items')


class NewsArticle(Page):
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
    def get_article_image(self):
        return build_image_url(self.featured_image)
    article_image = property(get_article_image)
    tags = ClusterTaggableManager(through=NewsArticleTag, blank=True)
    body = StreamField(BlogStreamBlock())
    pin_to_top = models.BooleanField(default=False)
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
        soup = BeautifulSoup(paragraphs[0], "html.parser")
        for tag in soup.findAll('p'):
            first_paragraph_parsed.append(tag)

        return str(first_paragraph_parsed[0])

    search_fields = Page.search_fields + [
        index.SearchField('body'),
        index.SearchField('tags'),
    ]

    content_panels = Page.content_panels + [
        FieldPanel('date'),
        FieldPanel('title'),
        FieldPanel('heading'),
        FieldPanel('subheading'),
        FieldPanel('author'),
        ImageChooserPanel('featured_image'),
        FieldPanel('featured_image_alt_text'),
        FieldPanel('tags'),
        StreamFieldPanel('body'),
        FieldPanel('pin_to_top'),
    ]

    promote_panels = [
        FieldPanel('slug'),
        FieldPanel('seo_title'),
        FieldPanel('search_description'),
        ImageChooserPanel('promote_image')
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
        APIField('tags'),
        APIField('body_blurb'),
        APIField('body'),
        APIField('pin_to_top'),
        APIField('slug'),
        APIField('seo_title'),
        APIField('search_description'),
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

    def get_sitemap_urls(self, request=None):
        return [
            {
                'location': '{}/blog/{}/'.format(Site.find_for_request(request).root_url, self.slug),
                'lastmod': (self.last_published_at or self.latest_revision_created_at),
            }
        ]


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
        ImageChooserPanel('image'),
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

    class Meta:
        icon = 'document'


class MissionStatement(models.Model):
    statement = models.CharField(max_length=255)

    api_fields = ('statement', )


class MissionStatements(Orderable, MissionStatement):
    mission_statements = ParentalKey('news.PressIndex', related_name='mission_statements')


class PressIndex(Page):
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

    press_inquiry_name = models.CharField(max_length=255, blank=True, null=True)
    press_inquiry_phone = models.CharField(max_length=255)
    press_inquiry_email = models.EmailField()
    experts_heading = models.CharField(max_length=255)
    experts_blurb = models.TextField()
    mentions = StreamField([
        ('mention', NewsMentionBlock(icon='document')),
    ], null=True)
    promote_image = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )

    def get_sitemap_urls(self, request=None):
        return [
            {
                'location': '{}/press/'.format(Site.find_for_request(request).root_url),
                'lastmod': (self.last_published_at or self.latest_revision_created_at),
            }
        ]

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
        DocumentChooserPanel('press_kit'),
        FieldPanel('press_inquiry_name'),
        FieldPanel('press_inquiry_phone'),
        FieldPanel('press_inquiry_email'),
        FieldPanel('experts_heading'),
        FieldPanel('experts_blurb'),
        InlinePanel('experts_bios', label="Experts"),
        StreamFieldPanel('mentions'),
        InlinePanel('mission_statements', label="Mission Statement"),
    ]

    promote_panels = [
        FieldPanel('slug'),
        FieldPanel('seo_title'),
        FieldPanel('search_description'),
        ImageChooserPanel('promote_image')
    ]

    api_fields = [
        APIField('press_kit'),
        APIField('press_kit_url'),
        APIField('releases'),
        APIField('slug'),
        APIField('seo_title'),
        APIField('search_description'),
        APIField('promote_image'),
        APIField('experts_heading'),
        APIField('experts_blurb'),
        APIField('experts_bios'),
        APIField('mentions'),
        APIField('mission_statements'),
        APIField('press_inquiry_name'),
        APIField('press_inquiry_phone'),
        APIField('press_inquiry_email')
    ]

    subpage_types = ['news.PressRelease']
    parent_page_types = ['pages.HomePage']
    max_count = 1


class PressRelease(Page):
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

    body = StreamField(BlogStreamBlock())

    promote_image = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )

    def get_sitemap_urls(self, request=None):
        return [
            {
                'location': '{}/press/{}'.format(Site.find_for_request(request).root_url, self.slug),
                'lastmod': (self.last_published_at or self.latest_revision_created_at),
            }
        ]

    search_fields = Page.search_fields + [
        index.SearchField('body'),
    ]

    content_panels = Page.content_panels + [
        FieldPanel('date'),
        FieldPanel('title'),
        FieldPanel('heading'),
        FieldPanel('subheading'),
        FieldPanel('author'),
        ImageChooserPanel('featured_image'),
        FieldPanel('featured_image_alt_text'),
        FieldPanel('excerpt'),
        StreamFieldPanel('body'),
    ]

    promote_panels = [
        FieldPanel('slug'),
        FieldPanel('seo_title'),
        FieldPanel('search_description'),
        ImageChooserPanel('promote_image')
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
