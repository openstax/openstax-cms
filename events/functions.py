from eventbrite import Eventbrite

from django.conf import settings

from .models import Event

def check_eventbrite_registration(email):
    eventbrite = Eventbrite(settings.EVENTBRITE_API_PRIVATE_TOKEN)
    event_id = Event.objects.all()[0].eventbrite_event_id

    attendees = eventbrite.get_event_attendees(event_id=event_id, page=1)
    number_of_pages = (int(attendees.pagination['page_count']))

    attendee_emails = []
    for page in range(1, number_of_pages + 1):
        attendees = eventbrite.get_event_attendees(event_id=event_id, page=page)

        for attendee in attendees['attendees']:
            attendee_emails.append(attendee['profile']['email'].lower())

    return email.lower() in attendee_emails
