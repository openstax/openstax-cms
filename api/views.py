from django.core import serializers
from django.http import JsonResponse, HttpResponse
from django.db.models import Q
from rest_framework import viewsets, generics
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.decorators import parser_classes
from rest_framework.parsers import JSONParser
from salesforce.models import Adopter, School, MapBoxDataset
from errata.models import ERRATA_RESOURCES
from global_settings.models import StickyNote, Footer, GiveToday
from wagtail.images.models import Image
from wagtail.documents.models import Document
from wagtail.core.models import Site
from .models import ProgressTracker
from .serializers import AdopterSerializer, ImageSerializer, DocumentSerializer, ProgressSerializer, CustomizationRequestSerializer
from flags.sources import get_flags

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


class ProgressViewSet(viewsets.ModelViewSet):
    queryset = ProgressTracker.objects.all()
    serializer_class = ProgressSerializer

    def get_queryset(self):
        queryset = ProgressTracker.objects.all()
        account_id = self.request.query_params.get('account_id', None)
        if account_id is not None:
            queryset = queryset.filter(account_id=account_id)
        return queryset

def sticky_note(request):
    sticky_note = StickyNote.for_site(Site.find_for_request(request))

    return JsonResponse({
        'start': sticky_note.start,
        'expires': sticky_note.expires,
        'show_popup': sticky_note.show_popup,
        'header': sticky_note.header,
        'body': sticky_note.body,
        'link_text': sticky_note.link_text,
        'link': sticky_note.link,
        'emergency_expires': sticky_note.emergency_expires,
        'emergency_content': sticky_note.emergency_content,
    })


def footer(request):
    footer = Footer.for_site(Site.find_for_request(request))

    return JsonResponse({
        'supporters': footer.supporters,
        'copyright': footer.copyright,
        'ap_statement': footer.ap_statement,
        'facebook_link': footer.facebook_link,
        'twitter_link': footer.twitter_link,
        'linkedin_link': footer.linkedin_link,
    })

def mapbox(request):
    mapbox = MapBoxDataset.objects.all()
    response = []

    for mapbox_instance in mapbox:
        response.append({
            'name': mapbox_instance.name,
            'style': mapbox_instance.style_url
        })

    return JsonResponse(response, safe=False)

def errata_fields(request):
    '''
    Return a JSON representation of fields from the errata.model.errata static options.
    For now this only works on resources but has the capability to be expanded in the future.
    '''
    response = []

    if request.GET.get('field', None) == 'resources':
        for field, verbose in ERRATA_RESOURCES:
            if field != 'OpenStax Concept Coach': # This is not my favorite way to do this but we need to keep the data on existing errata
                response.append({'field': field, 'verbose': verbose})

    return JsonResponse(response, safe=False)

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
    saved_one_million = request.GET.get('saved_one_million', None)
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
        if saved_one_million:
            schools = schools.filter(all_time_savings__gte = 1000000)
            
        if testimonial:
            schools = schools.filter(testimonial__isnull=False)

        if q:
            schools = schools.filter((Q(name__icontains=q) | Q(physical_city__icontains=q)| Q(physical_state_province__icontains=q)| Q(physical_country__icontains=q)))

        response = serializers.serialize("json", schools)
        return HttpResponse(response, content_type='application/json')
    else:
        return JsonResponse({'error': 'Invalid format requested.'})

def flags(request):
    q_flag = request.GET.get('flag', False)

    list_flags = get_flags(sources=None, ignore_errors=False)

    if not q_flag:
        # We return the list of all flags.
        data = []
        for (flag, fobject) in list_flags.items():
            data.append({
                'name': flag
            })
        return JsonResponse(data, safe=False)
    else:
        # We return the enabled settings for the set flag.
        if q_flag in list_flags:
            data = [{'name': q_flag, "conditions": []}]
            for condition in list_flags[q_flag].conditions:
                data[0]['conditions'].append({
                    'required': condition.__dict__['required'],
                    'type': condition.__dict__['condition'],
                    'value': condition.__dict__['value']
                })
            return JsonResponse(data, safe=False)
        else:
            return JsonResponse([{'error': 'The flag does not exist.'}], safe=False)



@api_view(['GET', 'POST'])
@parser_classes([JSONParser])
def customize_request(request):
    """
    Only allow posts to this endpoint.
    """
    if request.method == 'POST':
        serializer = CustomizationRequestSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    else:
        return Response({'message': 'Only post requests valid for this endpoint'})


def give_today(request):
    give_today = GiveToday.for_site(Site.find_for_request(request))

    return JsonResponse({
        'give_link_text': give_today.give_link_text,
        'give_link': give_today.give_link,
        'start': give_today.start,
        'expires': give_today.expires,
        'menu_start': give_today.menu_start,
        'menu_expires': give_today.menu_expires,
    })
