from django.db import models
from wagtail.search import index
from wagtail.admin.edit_handlers import FieldPanel
from wagtail.images.edit_handlers import ImageChooserPanel
from wagtail.core.fields import RichTextField
from wagtail.snippets.models import register_snippet
from openstax.functions import build_image_url

class Subject(models.Model):
    name = models.CharField(max_length=255)
    page_content = models.TextField(blank=True, help_text="Content that appears on the subjects page when looking at a subject.")
    seo_title = models.CharField(max_length=255, null=True, blank=True)
    search_description = models.CharField(max_length=255, null=True, blank=True)

    api_fields = ('name', 'page_content', 'seo_title', 'search_description' )

    panels = [
        FieldPanel('name'),
        FieldPanel('page_content'),
        FieldPanel('seo_title'),
        FieldPanel('search_description'),
    ]

    def __str__(self):
        return self.name

register_snippet(Subject)


class FacultyResource(index.Indexed, models.Model):
    heading = models.CharField(max_length=255)
    description = RichTextField(blank=True, null=True)
    unlocked_resource = models.BooleanField(default=False)
    creator_fest_resource = models.BooleanField(default=False)

    api_fields = ('heading', 'description', 'unlocked_resource', 'creator_fest_resource')

    panels = [
        FieldPanel('heading'),
        FieldPanel('description'),
        FieldPanel('unlocked_resource'),
        FieldPanel('creator_fest_resource')
    ]

    search_fields = [
        index.SearchField('heading', partial_match=True),
    ]

    def __str__(self):
        return self.heading

register_snippet(FacultyResource)


class StudentResource(index.Indexed, models.Model):
    heading = models.CharField(max_length=255)
    description = RichTextField(blank=True, null=True)
    unlocked_resource = models.BooleanField(default=True)

    api_fields = ('heading', 'description', 'unlocked_resource')

    panels = [
        FieldPanel('heading'),
        FieldPanel('description'),
        FieldPanel('unlocked_resource'),
    ]

    search_fields = [
        index.SearchField('heading', partial_match=True),
    ]

    def __str__(self):
        return self.heading

register_snippet(StudentResource)


class Role(models.Model):
    display_name = models.CharField(max_length=255)
    salesforce_name = models.CharField(max_length=255)

    api_fields = ('display_name',
                  'salesforce_name')

    panels = [
        FieldPanel('display_name'),
        FieldPanel('salesforce_name'),
    ]

    def __str__(self):
        return self.display_name

register_snippet(Role)


class SharedContent(index.Indexed, models.Model):
    title = models.CharField(max_length=255, help_text="Internal name for identification.")
    heading = models.CharField(max_length=255, null=True, blank=True)
    content = models.TextField(null=True, blank=True)
    content_logged_in = models.TextField(null=True, blank=True)
    button_text = models.CharField(max_length=255, null=True, blank=True)
    button_url = models.URLField(null=True, blank=True)

    api_fields = ('heading', 'content', 'content_logged_in', 'button_text', 'button_url' )

    panels = [
        FieldPanel('title'),
        FieldPanel('heading'),
        FieldPanel('content'),
        FieldPanel('content_logged_in'),
        FieldPanel('button_text'),
        FieldPanel('button_url'),
    ]

    search_fields = [
        index.SearchField('title', partial_match=True),
    ]

    def __str__(self):
        return self.title

register_snippet(SharedContent)


class NewsSource(index.Indexed, models.Model):
    name = models.CharField(max_length=255)
    logo = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
    )

    def get_news_logo(self):
        return build_image_url(self.logo)

    news_logo = property(get_news_logo)

    api_fields = ('name', 'news_logo',)

    panels = [
        FieldPanel('name'),
        ImageChooserPanel('logo'),
    ]

    search_fields = [
        index.SearchField('name', partial_match=True),
    ]

    def __str__(self):
        return self.name

register_snippet(NewsSource)
