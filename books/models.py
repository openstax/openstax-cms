from django.db import models

from wagtail.wagtailcore.models import Page, Orderable
from wagtail.wagtailcore.fields import RichTextField
from wagtail.wagtailadmin.edit_handlers import (FieldPanel,
                                                InlinePanel)
from wagtail.wagtailimages.edit_handlers import ImageChooserPanel

# Create your models here.

class Book(Page):
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    revision = models.CharField(max_length=255, blank=True, null=True)
    description = RichTextField(blank=True)
    cover_image = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )
    publish_date = models.DateField(blank=True, null=True)
    isbn_10 = models.IntegerField(blank=True, null=True)
    isbn_13 = models.CharField(max_length=255, blank=True, null=True)

    content_panels = Page.content_panels + [
        FieldPanel('name'),
        FieldPanel('revision'),
        FieldPanel('description', classname="full"),
        ImageChooserPanel('cover_image'),
        FieldPanel('publish_date'),
        FieldPanel('isbn_10'),
        FieldPanel('isbn_13'),
    ]
    
    api_fields = ('created',
                  'updated',
                  'revision',
                  'description',
                  'cover_image',
                  'publish_date',
                  'isbn_10',
                  'isbn_13')