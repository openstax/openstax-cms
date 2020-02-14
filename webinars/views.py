from rest_framework import viewsets

from django.shortcuts import render
from django.http import JsonResponse
from django.conf import settings

from .models import Webinar
from .serializers import WebinarSerializer


class WebinarViewSet(viewsets.ModelViewSet):
    queryset = Webinar.objects.all()
    serializer_class = WebinarSerializer
