from django.db import models

from wagtail.wagtailcore.fields import RichTextField
from wagtail.wagtailadmin.edit_handlers import FieldPanel, MultiFieldPanel
from wagtail.wagtailimages.edit_handlers import ImageChooserPanel
from wagtail.wagtailsnippets.models import register_snippet


class Ally(models.Model):
    online_course = models.BooleanField(default=False)
    adaptive_course = models.BooleanField(default=False)
    customized_tools = models.BooleanField(default=False)

    logo = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )
    heading = models.CharField(max_length=255)
    short_description = RichTextField()
    long_description = RichTextField()
    link_url = models.URLField(blank=True, help_text="Call to Action Link")
    link_text = models.CharField(max_length=255, help_text="Call to Action Text")

    api_fields = ('online_course', 'adaptive_course', 'customized_tools', 'logo', 'heading',
                  'short_description', 'long_description' )

    panels = [
        MultiFieldPanel(
        [
          FieldPanel('online_course'),
          FieldPanel('adaptive_course'),
          FieldPanel('customized_tools'),
        ],
          heading="Categories",
        ),
        ImageChooserPanel('logo'),
        FieldPanel('heading'),
        FieldPanel('short_description'),
        FieldPanel('long_description'),
    ]

    def __str__(self):
        return self.heading

register_snippet(Ally)
