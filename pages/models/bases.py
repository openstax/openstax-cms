from django.db import models

from wagtail import blocks
from wagtail.fields import RichTextField, StreamField
from wagtail.admin.panels import FieldPanel
from wagtail.api import APIField

from pages.custom_blocks import APIImageChooserBlock
from openstax.functions import build_image_url
from openstax.api_fields import ExpandedRichTextField

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
        APIField('quote_text', serializer=ExpandedRichTextField()),
        'quote_image_url',
        'get_quote_image_alignment_display',
        'quote_link',
        'quote_link_text',
    )

    panels = [
        FieldPanel('quote_text'),
        FieldPanel('quote_image'),
        FieldPanel('quote_image_alignment'),
        FieldPanel('quote_link'),
        FieldPanel('quote_link_text'),
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
        FieldPanel('logo'),
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
    ], use_json_field=True)

    api_fields = ('heading',
                  'people', )

    panels = [
        FieldPanel('heading'),
        FieldPanel('people'),
    ]


class PersonTag(models.Model):
    """Controlled-vocabulary tag for people (e.g. "Core Team", "Advisor").

    A Wagtail snippet so editors pick from a shared list and new tags need no
    migration. Serialized inline by PersonTagChooserBlock as {id, name, slug}."""
    name = models.CharField(max_length=100, help_text='Display label, e.g. "Core Team".')
    slug = models.SlugField(max_length=100, unique=True,
        help_text='Stable key used by the frontend for styling/filtering.')
    sort_order = models.IntegerField(default=0,
        help_text='Lower numbers sort first.')

    panels = [
        FieldPanel('name'),
        FieldPanel('slug'),
        FieldPanel('sort_order'),
    ]

    class Meta:
        ordering = ['sort_order', 'name']
        verbose_name = 'Person tag'

    def __str__(self):
        return self.name
