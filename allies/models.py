from django.db import models
from wagtail.models import Page
from snippets.models import Subject

#TODO: remove this app after all migrations have been applied
class AllySubject(models.Model):
    pass


class Ally(Page):
    pass

