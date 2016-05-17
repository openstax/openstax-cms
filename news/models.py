from django.db import models

from wagtail.wagtailadmin.edit_handlers import FieldPanel
from wagtail.wagtailcore.fields import RichTextField
from wagtail.wagtailcore.models import Page
from wagtail.wagtailsearch import index

from modelcluster.fields import ParentalKey
from modelcluster.contrib.taggit import ClusterTaggableManager
from taggit.models import TaggedItemBase


class NewsIndex(Page):
    intro = RichTextField(blank=True)

    content_panels = Page.content_panels + [
        FieldPanel('intro', classname="full")
    ]

    api_fields = (
        'intro',
    )

    subpage_types = ['news.NewsArticle']
    parent_page_types = ['pages.HomePage']


class NewsArticleTag(TaggedItemBase):
    content_object = ParentalKey('news.NewsArticle', related_name='tagged_items')


class NewsArticle(Page):
    date = models.DateField("Post date")
    intro = models.CharField(max_length=250)
    tags = ClusterTaggableManager(through=NewsArticleTag, blank=True)
    body = RichTextField(blank=True)

    search_fields = Page.search_fields + (
        index.SearchField('intro'),
        index.SearchField('body'),
    )

    content_panels = Page.content_panels + [
        FieldPanel('date'),
        FieldPanel('intro'),
        FieldPanel('tags'),
        FieldPanel('body', classname="full")
    ]

    api_fields = (
        'date',
        'intro',
        'tags',
        'body',
    )

    parent_page_types = ['news.NewsIndex']

