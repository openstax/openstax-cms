from django.db import models
from wagtail.wagtailadmin.edit_handlers import FieldPanel
from wagtail.wagtailcore.fields import RichTextField
from wagtail.wagtailsnippets.models import register_snippet


class Subject(models.Model):
    name = models.CharField(max_length=255)

    api_fields = ('name', )

    panels = [
        FieldPanel('name'),
    ]

    def __str__(self):
        return self.name

register_snippet(Subject)


class FacultyResource(models.Model):
    heading = models.CharField(max_length=255)
    description = RichTextField(blank=True, null=True)

    api_fields = ('heading', 'description', )

    panels = [
        FieldPanel('heading'),
        FieldPanel('description'),
    ]

    def __str__(self):
        return self.heading

register_snippet(FacultyResource)


class StudentResource(models.Model):
    heading = models.CharField(max_length=255)
    description = RichTextField(blank=True, null=True)

    api_fields = ('heading', 'description', )

    panels = [
        FieldPanel('heading'),
        FieldPanel('description'),
    ]

    def __str__(self):
        return self.heading

register_snippet(StudentResource)
