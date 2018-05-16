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

from modelcluster.fields import ParentalKey
from modelcluster.contrib.taggit import ClusterTaggableManager
from taggit.models import TaggedItemBase
from openstax.functions import build_image_url

class PullQuoteBlock(StructBlock):
    quote = TextBlock("quote title")
    attribution = CharBlock()

    class Meta:
        icon = "openquote"


class ImageFormatChoiceBlock(FieldBlock):
    field = forms.ChoiceField(choices=(
        ('left', 'Wrap left'), ('right', 'Wrap right'), ('mid', 'Mid width'), ('full', 'Full width'),
    ))


class HTMLAlignmentChoiceBlock(FieldBlock):
    field = forms.ChoiceField(choices=(
        ('normal', 'Normal'), ('full', 'Full width'),
    ))


class ImageBlock(StructBlock):
    image = ImageChooserBlock()
    caption = RichTextBlock()
    alignment = ImageFormatChoiceBlock()


class AlignedHTMLBlock(StructBlock):
    html = RawHTMLBlock()
    alignment = HTMLAlignmentChoiceBlock()

    class Meta:
        icon = "code"


class BlogStreamBlock(StreamBlock):
    paragraph = RichTextBlock(icon="pilcrow")
    aligned_image = ImageBlock(label="Aligned image", icon="image")
    pullquote = PullQuoteBlock()
    aligned_html = AlignedHTMLBlock(icon="code", label='Raw HTML')
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

    @property
    def articles(self):
        articles = NewsArticle.objects.live().child_of(self)
        article_data = {}
        for article in articles:
            article_data['news/{}'.format(article.slug)] = {
                'detail_url': '/api/v2/pages/{}'.format(article.pk),
                'date': article.date,
                'heading': article.heading,
                'subheading': article.subheading,
                'pin_to_top': article.pin_to_top,
                'article_image': article.article_image,
                'author': article.author,
                'tags': [tag.name for tag in article.tags.all()],
            }
        return article_data

    content_panels = Page.content_panels + [
        FieldPanel('intro', classname="full"),
        DocumentChooserPanel('press_kit'),
    ]

    api_fields = (
        'intro',
        'press_kit',
        'articles',
        'slug',
        'seo_title',
        'search_description',
    )

    subpage_types = ['news.NewsArticle']
    parent_page_types = ['pages.HomePage']


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

    def get_article_image(self):
        return build_image_url(self.featured_image)
    article_image = property(get_article_image)

    tags = ClusterTaggableManager(through=NewsArticleTag, blank=True)
    body = RichTextField(blank=True)

    body = StreamField(BlogStreamBlock())

    pin_to_top = models.BooleanField(default=False)

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
        FieldPanel('tags'),
        StreamFieldPanel('body'),
        FieldPanel('pin_to_top'),
    ]

    api_fields = (
        'date',
        'title',
        'heading',
        'subheading',
        'author',
        'article_image',
        'tags',
        'body',
        'pin_to_top',
        'slug',
        'seo_title',
        'search_description',
    )

    parent_page_types = ['news.NewsIndex']

    def save(self, *args, **kwargs):
        if self.pin_to_top:
            current_pins = self.__class__.objects.filter(pin_to_top=True)
            for pin in current_pins:
                if pin != self:
                    pin.pin_to_top = False
                    pin.save()

        return super(NewsArticle, self).save(*args, **kwargs)


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

    api_fields = ('name', 'email', 'title', 'bio', 'expert_image')

    panels = [
        FieldPanel('name'),
        FieldPanel('email'),
        FieldPanel('title'),
        FieldPanel('bio'),
        ImageChooserPanel('image'),
    ]


class ExpertsBios(Orderable, Experts):
    experts_bios = ParentalKey('news.PressIndex', related_name='experts_bios')


class NewsSourceChooserBlock(SnippetChooserBlock):
    def get_api_representation(self, value, context=None):
        if value:
            return {
                'id': value.id,
                'heading': value.heading,
                'content': value.content,
            }


class NewsMention(models.Model):
    source_name = models.CharField(max_length=255)
    image = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
    )

    def get_source_image(self):
        return build_image_url(self.image)

    source_image = property(get_source_image)
    url = models.URLField()
    headline = models.CharField(max_length=255)
    date = models.DateField()

    api_fields = ('source_name', 'source_image', 'url', 'headline', 'date' )

    panels = [
        FieldPanel('source_name'),
        ImageChooserPanel('image'),
        FieldPanel('url'),
        FieldPanel('headline'),
        FieldPanel('date'),
    ]


class NewsMentions(Orderable, NewsMention):
    news_mentions = ParentalKey('news.PressIndex', related_name='news_mentions')


class MissionStatement(models.Model):
    statement = models.CharField(max_length=255)

    api_fields = ('statement', )


class MissionStatements(Orderable, MissionStatement):
    mission_statements = ParentalKey('news.PressIndex', related_name='mission_statements')


class PressIndex(Page):
    intro = RichTextField(blank=True)
    press_kit = models.ForeignKey(
        'wagtaildocs.Document',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )
    press_inquiry_name = models.CharField(max_length=255, blank=True, null=True)
    press_inquiry_phone = models.CharField(max_length=255)
    press_inquiry_email = models.EmailField()
    experts_heading = models.CharField(max_length=255)
    experts_blurb = models.TextField()

    @property
    def releases(self):
        releases = PressRelease.objects.live().child_of(self)
        releases_data = {}
        for release in releases:
            releases_data['press/{}'.format(release.slug)] = {
                'detail_url': '/api/v2/pages/{}'.format(release.pk),
                'date': release.date,
                'heading': release.heading,
                'excerpt': release.excerpt,
                'author': release.author,
            }
        return releases_data

    content_panels = Page.content_panels + [
        FieldPanel('intro', classname="full"),
        DocumentChooserPanel('press_kit'),
        FieldPanel('press_inquiry_name'),
        FieldPanel('press_inquiry_phone'),
        FieldPanel('press_inquiry_email'),
        FieldPanel('experts_heading'),
        FieldPanel('experts_blurb'),
        InlinePanel('experts_bios', label="Experts"),
        InlinePanel('news_mentions', label="News Mentions"),
        InlinePanel('mission_statements', label="Mission Statement"),
    ]

    api_fields = (
        'intro',
        'press_kit',
        'releases',
        'slug',
        'seo_title',
        'search_description',
        'experts_bios',
        'news_mentions',
        'mission_statements',
        'press_inquiry_name',
        'press_inquiry_phone',
        'press_inquiry_email',
    )

    subpage_types = ['news.PressRelease']
    parent_page_types = ['pages.HomePage']


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

    def get_article_image(self):
        return build_image_url(self.featured_image)
    article_image = property(get_article_image)
    excerpt = models.CharField(max_length=255)

    body = StreamField(BlogStreamBlock())

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
        StreamFieldPanel('body'),
    ]

    api_fields = (
        'date',
        'title',
        'heading',
        'subheading',
        'author',
        'article_image',
        'body',
        'slug',
        'seo_title',
        'search_description',
    )
