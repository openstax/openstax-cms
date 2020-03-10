from eventbrite import Eventbrite
from collections import OrderedDict

from django.conf import settings
from django.http import JsonResponse

from rest_framework import viewsets

from .models import Session, Registration
from .serializers import SessionSerializer, RegistrationSerializer
from .functions import check_eventbrite_registration

def check_reg_status(request):
    email = request.GET.get('email', None)
    session_registrations = Registration.objects.filter(registration_email__iexact=email)

    response = OrderedDict(eventbrite_registered=check_eventbrite_registration(email),
                           session_registered=session_registrations.exists())

    return JsonResponse(response)


class SessionViewSet(viewsets.ModelViewSet):
    queryset = Session.objects.all()
    serializer_class = SessionSerializer


class RegistrationViewSet(viewsets.ModelViewSet):
    queryset = Registration.objects.all()
    serializer_class = RegistrationSerializer
