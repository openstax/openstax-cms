from eventbrite import Eventbrite

from django.shortcuts import render
from django.conf import settings
from django.http import JsonResponse

from rest_framework import viewsets

from .models import Event, Session
from .serializers import SessionSerializer

def eventbrite(request):
    eventbrite = Eventbrite(settings.EVENTBRITE_API_PRIVATE_TOKEN)
    event_id = Event.objects.all()[0].eventbrite_event_id
    event = eventbrite.get_event(event_id)
    attendees = eventbrite.get_event_attendees(event_id=event_id)




    return JsonResponse(attendee)


class SessionViewSet(viewsets.ModelViewSet):
    queryset = Session.objects.all()
    serializer_class = SessionSerializer