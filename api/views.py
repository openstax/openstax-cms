from django.core import serializers
from django.http import JsonResponse, HttpResponse
from django.db.models import Q
from rest_framework import viewsets
from salesforce.models import Adopter, School
from global_settings.models import StickyNote, Footer
from wagtail.images.models import Image
from wagtail.documents.models import Document
from .serializers import AdopterSerializer, ImageSerializer, DocumentSerializer


class AdopterViewSet(viewsets.ModelViewSet):
    queryset = Adopter.objects.all()
    serializer_class = AdopterSerializer


class ImageViewSet(viewsets.ModelViewSet):
    queryset = Image.objects.all()
    serializer_class = ImageSerializer


class DocumentViewSet(viewsets.ModelViewSet):
    queryset = Document.objects.all()
    serializer_class = DocumentSerializer

    def get_queryset(self):
        queryset = Document.objects.all()
        search = self.request.query_params.get('search', None)
        if search is not None:
            queryset = queryset.filter(title__icontains=search)
        return queryset


def sticky_note(request):
    sticky_note = StickyNote.for_site(request.site)

    return JsonResponse({
        'show': sticky_note.show,
        'expires': sticky_note.expires,
        'content': sticky_note.content,
        'emergency_expires': sticky_note.emergency_expires,
        'emergency_content': sticky_note.emergency_content,
    })


def footer(request):
    footer = Footer.for_site(request.site)

    return JsonResponse({
        'supporters': footer.supporters,
        'copyright': footer.copyright,
        'ap_statement': footer.ap_statement,
        'facebook_link': footer.facebook_link,
        'twitter_link': footer.twitter_link,
        'linkedin_link': footer.linkedin_link,
    })

def schools(request):
    format = request.GET.get('format', 'json')
    q = request.GET.get('q', False)
    name = request.GET.get('name', False)
    id = request.GET.get('id', False)
    type = request.GET.get('type', False)
    physical_country = request.GET.get('physical_country', False)
    physical_state_province = request.GET.get('physical_state_province', False)
    physical_city = request.GET.get('physical_city', False)
    key_institutional_partner = request.GET.get('key_institutional_partner', None)
    achieving_the_dream_school = request.GET.get('achieving_the_dream_school', None)
    testimonial = request.GET.get('testimonial', None)

    schools = School.objects.filter(long__isnull=False, lat__isnull=False)

    if format == 'geojson':
        data = []
        for school in schools:
            if school.lat and school.long:
                item = {
                    'type': 'Feature',
                    'geometry': {
                        'type': 'Point',
                        'coordinates': [float(school.long), float(school.lat)]
                    },
                    'properties': {
                        'name': school.name
                    }
                }
                data.append(item)
        return JsonResponse(data, safe=False)
    elif format == 'json':
        if name:
            schools = schools.filter(name__icontains=name)
        if id:
            schools = schools.filter(pk=id)
        if type:
            schools = schools.filter(type__icontains=type)
        if physical_city:
            schools = schools.filter(physical_city=physical_city)
        if physical_state_province:
            schools = schools.filter(physical_state_province=physical_state_province)
        if physical_country:
            schools = schools.filter(physical_country=physical_country)
        if key_institutional_partner:
            schools = schools.filter(key_institutional_partner=True)
        if achieving_the_dream_school:
            schools = schools.filter(achieving_the_dream_school=True)
        if testimonial:
            schools = schools.filter(testimonial__isnull=False)

        if q:
            schools = schools.filter((Q(name__icontains=q) | Q(physical_city__icontains=q)| Q(physical_state_province__icontains=q)| Q(physical_country__icontains=q)))

        response = serializers.serialize("json", schools)
        return HttpResponse(response, content_type='application/json')
    else:
        return JsonResponse({'error': 'Invalid format requested.'})
