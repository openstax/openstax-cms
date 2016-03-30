from django.db import models

from wagtail.wagtailcore.models import Page
from wagtail.wagtailcore.fields import RichTextField
from wagtail.wagtailadmin.edit_handlers import FieldPanel, MultiFieldPanel, InlinePanel
from wagtail.wagtailimages.edit_handlers import ImageChooserPanel

from modelcluster.fields import ParentalKey

from snippets.models import Subject

from openstax.functions import build_image_url


class AllySubject(models.Model):
    subject = models.ForeignKey(Subject)
    ally = ParentalKey('Ally', related_name='ally_subjects')

    def get_subject_name(self):
        return self.subject.name


class Ally(Page):
    online_homework = models.BooleanField(default=False)
    adaptive_courseware = models.BooleanField(default=False)
    customization_tools = models.BooleanField(default=False)
    is_ap = models.BooleanField(default=False)

    logo = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='logo'
    )

    def get_ally_logo(self):
        return build_image_url(self.ally.logo)
    ally_logo = property(get_ally_logo)

    heading = models.CharField(max_length=255)
    short_description = RichTextField()
    long_description = RichTextField()

    # a method to reverse retrieve the subject names, prevents multiple calls from Webview
    # /api/v1/pages/?type=allies.Ally&fields=title,short_description,ally_logo,heading,ally_subject_list
    def ally_subject_list(self):
        subjects = AllySubject.objects.filter(ally=self)
        subject_names = []
        for subject in subjects:
            subject_names.append(subject.subject.name)
        return subject_names
    property(ally_subject_list)

    api_fields = ('online_homework', 'adaptive_courseware', 'customization_tools',
                  'ally_subject_list', 'is_ap',
                  'ally_logo', 'heading',
                  'short_description', 'long_description')

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
        FieldPanel('is_ap'),
        ImageChooserPanel('logo'),
        FieldPanel('heading'),
        FieldPanel('short_description'),
        FieldPanel('long_description'),
    ]
