import json

from django.db import models
from wagtail.core import blocks
from wagtail.core.fields import StreamField
from news.models import SubjectBlock
from snippets.models import Subject


def webinar_subject_search(subject):
    webinars = Webinar.objects.all()
    webinars_to_return = []
    for webinar in webinars:
        webinar_subjects = webinar.selected_subjects
        if subject in webinar_subjects:
            webinars_to_return.append(webinar)

    return webinars_to_return


class Webinar(models.Model):
    start = models.DateTimeField()
    end = models.DateTimeField()
    title = models.CharField(max_length=255)
    description = models.TextField()
    speakers = models.CharField(max_length=255)
    spaces_remaining = models.PositiveIntegerField()
    registration_url = models.URLField()
    registration_link_text = models.CharField(max_length=255)
    display_on_tutor_page = models.BooleanField(default=False)
    webinar_subjects = StreamField(blocks.StreamBlock([
        ('subject', blocks.ListBlock(SubjectBlock())
         )]), null=True, blank=True)

    @property
    def selected_subjects(self):
        prep_value = self.webinar_subjects.get_prep_value()
        subjects = []
        for s in prep_value:
            for x in s['value']:
                subject_id = x['value']['subject']
                subject = Subject.objects.filter(id=subject_id)
                subjects.append(str(subject[0]))
        return subjects

    def selected_subjects_json(self):
        prep_value = self.webinar_subjects.get_prep_value()
        subjects = []
        for s in prep_value:
            for x in s['value']:
                subject_id = x['value']['subject']
                featured = x['value']['featured']
                subject = Subject.objects.filter(id=subject_id)
                subjects.append({"subject":str(subject[0]), "featured":str(featured)})
        return subjects

    def __str__(self):
        return self.title
