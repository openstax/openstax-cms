from django.db import models

from wagtail.core import blocks
from wagtail.core.fields import RichTextField, StreamField
from wagtail.admin.edit_handlers import FieldPanel, StreamFieldPanel
from wagtail.images.edit_handlers import ImageChooserPanel

from .custom_blocks import APIImageChooserBlock, ImageBlock

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
                                             null=True)
    quote_link = models.URLField(blank=True, null=True)
    quote_link_text = models.CharField(max_length=255, blank=True, null=True)

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
    description = models.TextField(blank=True, null=True)

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


class MarketingVideoLink(models.Model):
    video_title = models.CharField(max_length=255, blank=True, null=True)
    video_url = models.URLField(blank=True, null=True)
    video_file = models.FileField(upload_to='marketing_videos', blank=True, null=True)
    image_url = models.URLField(blank=True, null=True)
    image_file = models.ForeignKey(
        'wagtailimages.Image',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='+',
    )
    video_image_blurb = models.CharField(max_length=255, null=True, blank=True)

    def get_image(self):
        return build_image_url(self.image_file)
    image = property(get_image)

    api_fields = ('video_title',
                  'video_url',
                  'video_file',
                  'image_url',
                  'image',
                  'video_image_blurb',)

    panels = [
        FieldPanel('video_title'),
        FieldPanel('video_url'),
        FieldPanel('video_file'),
        FieldPanel('image_url'),
        ImageChooserPanel('image_file'),
        FieldPanel('video_image_blurb'),
    ]

class Resource(models.Model):
    name = models.CharField(max_length=255, help_text="Resources should be added in pairs to display properly.")
    available = models.BooleanField(default=False)
    available_image = models.ForeignKey(
        'wagtailimages.Image',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='+',
    )

    def get_available_image(self):
        return build_image_url(self.available_image)
    available_image_url = property(get_available_image)

    alternate_text = models.CharField(max_length=255, null=True, blank=True, help_text="If this has text, availability is ignored.")

    api_fields = ('name',
                  'available',
                  'available_image_url',
                  'alternate_text')

    panels = [
        FieldPanel('name'),
        FieldPanel('available'),
        ImageChooserPanel('available_image'),
        FieldPanel('alternate_text'),
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

class Card(models.Model):
    heading = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    cards = StreamField([
        ('card', blocks.StructBlock([
            ('image', ImageBlock()),
            ('headline', blocks.TextBlock(required=False)),
            ('description', blocks.TextBlock(required=False)),
            ('button_text', blocks.CharBlock(required=False)),
            ('button_url', blocks.CharBlock(required=False))
        ], icon='document')),
    ])

    api_fields = ('heading',
                  'description',
                  'cards')

    panels = [
        FieldPanel('heading'),
        FieldPanel('description'),
        StreamFieldPanel('cards')
    ]
