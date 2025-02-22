from django.db import models
from wagtail import blocks
from wagtail.fields import StreamField

from news.models import SubjectBlock, BlogCollectionChooserBlock
from snippets.models import Subject, WebinarCollection


class WebinarCollectionBlock(blocks.StructBlock):
    collection = BlogCollectionChooserBlock(required=True, label='Webinar Collection', target_model='snippets.WebinarCollection')
    featured = blocks.BooleanBlock(label="Featured", required=False)
    popular = blocks.BooleanBlock(label="Popular", required=False)

    class Meta:
        icon = 'placeholder'


def webinar_subject_search(subject):
    webinars = Webinar.objects.all().order_by('-start')
    webinars_to_return = []
    for webinar in webinars:
        webinar_subjects = webinar.selected_subjects
        if subject in webinar_subjects:
            webinars_to_return.append(webinar)

    return webinars_to_return


def webinar_collection_search(collection):
    webinars = Webinar.objects.all().order_by('-start')
    webinars_to_return = []
    for webinar in webinars:
        webinar_collections = webinar.selected_collections
        if collection in webinar_collections:
            webinars_to_return.append(webinar)

    return webinars_to_return


class Webinar(models.Model):
    start = models.DateTimeField()
    end = models.DateTimeField()
    title = models.CharField(max_length=255)
    description = models.TextField()
    speakers = models.CharField(max_length=255)
    spaces_remaining = models.PositiveIntegerField(blank=True, null=True)
    registration_url = models.URLField()
    registration_link_text = models.CharField(max_length=255)
    display_on_tutor_page = models.BooleanField(default=False)
    webinar_subjects = StreamField(blocks.StreamBlock([
        ('subject', blocks.ListBlock(SubjectBlock())
         )]), null=True, blank=True, use_json_field=True)
    webinar_collections = StreamField(blocks.StreamBlock([
        ('collection', blocks.ListBlock(WebinarCollectionBlock())
         )]), null=True, blank=True, use_json_field=True)

    @property
    def selected_subjects(self):
        prep_value = self.webinar_subjects.get_prep_value()
        subject_ids = [x['value']['subject'] for s in prep_value for x in s['value']]

        subjects_map = {
            subj.id: str(subj) for subj in Subject.objects.filter(id__in=subject_ids)
        }

        subjects = [subjects_map[x['value']['subject']] for s in prep_value for x in s['value']]
        return subjects

    @property
    def selected_collections(self):
        prep_value = self.webinar_collections.get_prep_value()
        cols = []
        for c in prep_value:
            if len(c['value']) > 0:
                if 'value' in c['value'][0]:
                    collection_id = c['value'][0]['value']['collection']
                    collection = WebinarCollection.objects.filter(id=collection_id)
                    cols.append(str(collection[0]))
        return cols

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

    def selected_collections_json(self):
        prep_value = self.webinar_collections.get_prep_value()
        cols = []
        for c in prep_value:
            if len(c['value']) > 0:
                if 'value' in c['value'][0]:
                    collection_id = c['value'][0]['value']['collection']
                    featured = c['value'][0]['value']['featured']
                    popular = c['value'][0]['value']['popular']
                    collection = WebinarCollection.objects.filter(id=collection_id)
                    cols.append({"collection": str(collection[0]), "featured": str(featured), "popular": str(popular)})
        return cols

    def __str__(self):
        return self.title
