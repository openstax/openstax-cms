from django.db import models

from wagtail.wagtailcore.models import Page
from wagtail.wagtailcore.fields import RichTextField
from wagtail.wagtailadmin.edit_handlers import FieldPanel
from wagtail.wagtailimages.edit_handlers import ImageChooserPanel
from wagtail.wagtailsnippets.edit_handlers import SnippetChooserPanel
from wagtail.wagtailsnippets.models import register_snippet


class Ally(models.Model):
    ALLY_CATEGORY = (
        ('OH', 'Online Homework'),
        ('AC', 'Adaptive Courseware'),
        ('CT', 'Customized Tools'),
    )
    ally_category = models.CharField(max_length=2,
                        choices=ALLY_CATEGORY)
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

    api_fields = ('ally_category', 'logo', 'heading', 'description', )

    panels = [
        FieldPanel('ally_category'),
        ImageChooserPanel('logo'),
        FieldPanel('heading'),
        FieldPanel('description'),
    ]

    def __str__(self):
        return self.heading

register_snippet(Ally)
