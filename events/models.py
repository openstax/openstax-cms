from django.db import models
from wagtail.core.models import Page

class Event(models.Model):
    eventbrite_event_id = models.CharField(max_length=255)

    def __str__(self):
        return self.eventbrite_event_id


class Session(models.Model):
    event = models.ForeignKey(Event, on_delete=models.PROTECT)
    name = models.CharField(max_length=255)
    description = models.TextField(null=True, blank=True)
    date = models.DateTimeField()
    location = models.CharField(max_length=255, null=True, blank=True)
    seats_remaining = models.SmallIntegerField()

    def __str__(self):
        return self.name


class Registration(models.Model):
    session = models.ForeignKey(Session, on_delete=models.PROTECT)
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    registration_email = models.EmailField(max_length=255)
    checked_in = models.DateTimeField(blank=True, null=True)

    @property
    def full_name(self):
        return '%s %s' % (self.first_name, self.last_name)

    def __str__(self):
        return self.full_name

    def save(self, *args, **kwargs):
        if not self.pk:
            # reduce the number of seats on the session if this is a new registration
            self.session.seats_remaining = self.session.seats_remaining - 1
            self.session.save()
        super(Registration, self).save(*args, **kwargs)


class CreatorFestSession(Page):
    pass

