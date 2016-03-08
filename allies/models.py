from django.db import models

from wagtail.wagtailcore.models import Page
from wagtail.wagtailcore.fields import RichTextField
from wagtail.wagtailadmin.edit_handlers import FieldPanel, MultiFieldPanel, InlinePanel
from wagtail.wagtailimages.edit_handlers import ImageChooserPanel

from modelcluster.fields import ParentalKey

from snippets.models import Subject


class AllySubject(models.Model):
    subject = models.ForeignKey(Subject)
    ally = ParentalKey('Ally', related_name='ally_subjects')


class Ally(Page):
    online_homework = models.BooleanField(default=False)
    adaptive_courseware = models.BooleanField(default=False)
    customization_tools = models.BooleanField(default=False)

    logo = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='logo'
    )
    heading = models.CharField(max_length=255)
    short_description = RichTextField()
    long_description = RichTextField()
    link_url = models.URLField(blank=True, help_text="Call to Action Link")
    link_text = models.CharField(max_length=255, help_text="Call to Action Text")

    api_fields = ('online_homework', 'adaptive_courseware', 'customization_tools', 'subjects',
                  'logo', 'heading',
                  'short_description', 'long_description' )

    content_panels = Page.content_panels + [
        MultiFieldPanel(
        [
          FieldPanel('online_homework'),
          FieldPanel('adaptive_courseware'),
          FieldPanel('customization_tools'),
        ],
          heading="Categories",
        ),
        InlinePanel('ally_subjects', label="Subjects"),
        ImageChooserPanel('logo'),
        FieldPanel('heading'),
        FieldPanel('short_description'),
        FieldPanel('long_description'),
    ]
