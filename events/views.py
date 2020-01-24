from eventbrite import Eventbrite

from django.conf import settings
from django.http import JsonResponse

from rest_framework import viewsets

from .models import Session, Registration
from .serializers import SessionSerializer, RegistrationSerializer
from .functions import check_eventbrite_registration

def check_reg_status(request):
    email = request.GET.get('email', None)

    return JsonResponse({'registered': check_eventbrite_registration(email)})


class SessionViewSet(viewsets.ModelViewSet):
    queryset = Session.objects.all()
    serializer_class = SessionSerializer


class RegistrationViewSet(viewsets.ModelViewSet):
    queryset = Registration.objects.all()
    serializer_class = RegistrationSerializer
