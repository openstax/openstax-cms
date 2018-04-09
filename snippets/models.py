from django.db import models
from wagtail.search import index
from wagtail.admin.edit_handlers import FieldPanel
from wagtail.core.fields import RichTextField
from wagtail.snippets.models import register_snippet


class Subject(models.Model):
    name = models.CharField(max_length=255)

    api_fields = ('name', )

    panels = [
        FieldPanel('name'),
    ]

    def __str__(self):
        return self.name

register_snippet(Subject)


class FacultyResource(index.Indexed, models.Model):
    heading = models.CharField(max_length=255)
    description = RichTextField(blank=True, null=True)
    unlocked_resource = models.BooleanField(default=False)

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
    content = RichTextField(null=True, blank=True)

    api_fields = ('heading', 'content', )

    panels = [
        FieldPanel('title'),
        FieldPanel('heading'),
        FieldPanel('content'),
    ]

    search_fields = [
        index.SearchField('title', partial_match=True),
    ]

    def __str__(self):
        return self.title

register_snippet(SharedContent)
