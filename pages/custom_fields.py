from django.db import models

from wagtail.core import blocks
from wagtail.core.fields import RichTextField, StreamField
from wagtail.admin.edit_handlers import FieldPanel, StreamFieldPanel
from wagtail.images.edit_handlers import ImageChooserPanel

from .custom_blocks import APIImageChooserBlock
from openstax.functions import build_image_url

class Quote(models.Model):
    IMAGE_ALIGNMENT_CHOICES = (
        ('L', 'left'),
        ('R', 'right'),
        ('F', 'full'),
    )
    quote_text = RichTextField()

    quote_image = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )

    def get_quote_image(self):
        return build_image_url(self.quote_image)
    quote_image_url = property(get_quote_image)

    quote_image_alignment = models.CharField(max_length=1,
                                             choices=IMAGE_ALIGNMENT_CHOICES,
                                             blank=True,
                                             default='')
    quote_link = models.URLField(blank=True, default='')
    quote_link_text = models.CharField(max_length=255, blank=True, default='')

    api_fields = (
        'quote_text',
        'quote_image_url',
        'get_quote_image_alignment_display',
        'quote_link',
        'quote_link_text',
    )

    panels = [
        FieldPanel('quote_text'),
        ImageChooserPanel('quote_image'),
        FieldPanel('quote_image_alignment'),
        FieldPanel('quote_link'),
        FieldPanel('quote_link_text'),
    ]


class Funder(models.Model):
    title = models.CharField(max_length=250)
    logo = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )

    def get_funder_logo(self):
        return build_image_url(self.logo)
    funder_logo = property(get_funder_logo)
    description = models.TextField(blank=True, default='')

    api_fields = ('title', 'funder_logo', 'description', )

    panels = [
        FieldPanel('title'),
        ImageChooserPanel('logo'),
        FieldPanel('description'),
    ]


class Institutions(models.Model):
    title = models.CharField(max_length=250)
    logo = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
        help_text='Image should be 340px wide, horizontal images are ideal'
    )

    def get_institution_logo(self):
        return build_image_url(self.logo)
    institution_logo = property(get_institution_logo)

    api_fields = ('title', 'institution_logo')

    panels = [
        FieldPanel('title'),
        ImageChooserPanel('logo'),
    ]


class Group(models.Model):
    heading = models.CharField(max_length=255)
    people = StreamField([
        ('person', blocks.StructBlock([
            ('name', blocks.CharBlock()),
            ('title', blocks.CharBlock(required=False)),
            ('bio', blocks.CharBlock(required=False)),
            ('photo', APIImageChooserBlock(required=False)),
        ], icon='user')),
    ])

    api_fields = ('heading',
                  'people', )

    panels = [
        FieldPanel('heading'),
        StreamFieldPanel('people'),
    ]
