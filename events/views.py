import json
import requests
from pprint import pprint
from eventbrite import Eventbrite

from django.shortcuts import render
from django.conf import settings
from django.http import JsonResponse

from rest_framework import viewsets

from .models import Event, Session
from .serializers import SessionSerializer

def check_reg_status(request):
    eventbrite = Eventbrite(settings.EVENTBRITE_API_PRIVATE_TOKEN)
    event_id = Event.objects.all()[0].eventbrite_event_id
    attendees = eventbrite.get_event_attendees(event_id=event_id)

    email = request.GET.get('email', None)

    attendee_emails = []
    for attendee in attendees['attendees']:
        attendee_emails.append(attendee['profile']['email'])

    return JsonResponse({'registered': email in attendee_emails})


class SessionViewSet(viewsets.ModelViewSet):
    queryset = Session.objects.all()
    serializer_class = SessionSerializer
