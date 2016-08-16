from django.db import models
from django import forms

from wagtail.wagtailcore.models import Page
from wagtail.wagtailcore.fields import RichTextField, StreamField
from wagtail.wagtailadmin.edit_handlers import FieldPanel, PageChooserPanel, StreamFieldPanel
from wagtail.wagtailimages.edit_handlers import ImageChooserPanel
from wagtail.wagtaildocs.edit_handlers import DocumentChooserPanel
from wagtail.wagtailembeds.blocks import EmbedBlock
from wagtail.wagtailsearch import index

from wagtail.wagtailcore.blocks import TextBlock, StructBlock, StreamBlock, FieldBlock, CharBlock, RichTextBlock, RawHTMLBlock
from wagtail.wagtailimages.blocks import ImageChooserBlock
from wagtail.wagtaildocs.blocks import DocumentChooserBlock

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
                'date': article.date,
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
    subheading = models.CharField(max_length=250, blank=True, null=True)
    author = models.CharField(max_length=250)
    featured_image = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )

    def get_article_image(self):
        return build_image_url(self.featured_image)
    article_image = property(get_article_image)

    tags = ClusterTaggableManager(through=NewsArticleTag, blank=True)
    body = RichTextField(blank=True)

    body = StreamField(BlogStreamBlock())

    pin_to_top = models.BooleanField(default=False)

    search_fields = Page.search_fields + (
        index.SearchField('intro'),
        index.SearchField('body'),
        index.SearchField('tags'),
    )

    content_panels = Page.content_panels + [
        FieldPanel('date'),
        FieldPanel('subheading'),
        FieldPanel('author'),
        ImageChooserPanel('featured_image'),
        FieldPanel('tags'),
        StreamFieldPanel('body'),
        FieldPanel('pin_to_top'),
    ]

    api_fields = (
        'date',
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
            print(current_pins)
            for pin in current_pins:
                if pin != self:
                    pin.pin_to_top = False
                    pin.save()

        return super(NewsArticle, self).save(*args, **kwargs)

