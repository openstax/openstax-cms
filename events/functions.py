from eventbrite import Eventbrite

from django.conf import settings

from .models import Event

def check_eventbrite_registration(email):
    eventbrite = Eventbrite(settings.EVENTBRITE_API_PRIVATE_TOKEN)
    event_id = Event.objects.all()[0].eventbrite_event_id
    attendees = eventbrite.get_event_attendees(event_id=event_id)

    attendee_emails = []
    for attendee in attendees['attendees']:
        attendee_emails.append(attendee['profile']['email'])

    return email in attendee_emails
