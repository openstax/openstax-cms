from django.db import models
from wagtail.core.models import Page

class Event(models.Model):
    eventbrite_event_id = models.CharField(max_length=255)

    def __str__(self):
        return self.eventbrite_event_id


class Session(models.Model):
    event = models.ForeignKey(Event, on_delete=models.PROTECT)
    name = models.CharField(max_length=255)
    date = models.DateTimeField()
    location = models.CharField(max_length=255, null=True, blank=True)
    seats_remaining = models.SmallIntegerField()

    def __str__(self):
        return self.name


class Registration(models.Model):
    session = models.ForeignKey(Session, on_delete=models.PROTECT)

    def __str__(self):
        return self.session


class CreatorFestSession(Page):
    pass

