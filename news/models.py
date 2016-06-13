from django.db import models

from wagtail.wagtailadmin.edit_handlers import FieldPanel
from wagtail.wagtailcore.fields import RichTextField
from wagtail.wagtailcore.models import Page
from wagtail.wagtailsearch import index
from wagtail.wagtailimages.edit_handlers import ImageChooserPanel
from wagtail.wagtaildocs.edit_handlers import DocumentChooserPanel

from modelcluster.fields import ParentalKey
from modelcluster.contrib.taggit import ClusterTaggableManager
from taggit.models import TaggedItemBase
from openstax.functions import build_image_url


class NewsIndex(Page):
    intro = RichTextField(blank=True)
    press_kit = models.ForeignKey(
        'wagtaildocs.Document',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )

    def articles(self):
        articles = NewsArticle.objects.live().child_of(self)
        result_list = list(articles.values('id', 'heading', 'subheading', 'date', 'pin_to_top', ))
        return result_list

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
    heading = models.CharField(max_length=250)
    subheading = models.CharField(max_length=250)
    author = models.CharField(max_length=250)
    image = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )

    def get_article_image(self):
        return build_image_url(self.image)
    article_image = property(get_article_image)

    tags = ClusterTaggableManager(through=NewsArticleTag, blank=True)
    body = RichTextField(blank=True)
    pin_to_top = models.BooleanField(default=False)

    search_fields = Page.search_fields + (
        index.SearchField('intro'),
        index.SearchField('body'),
        index.SearchField('tags'),
    )

    content_panels = Page.content_panels + [
        FieldPanel('date'),
        FieldPanel('heading'),
        FieldPanel('subheading'),
        FieldPanel('author'),
        ImageChooserPanel('image'),
        FieldPanel('tags'),
        FieldPanel('body', classname="full"),
        FieldPanel('pin_to_top'),
    ]

    api_fields = (
        'date',
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
            print(current_pins)
            for pin in current_pins:
                if pin != self:
                    pin.pin_to_top = False
                    pin.save()

        return super(NewsArticle, self).save(*args, **kwargs)

