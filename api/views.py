from django.core import serializers
from django.http import JsonResponse, HttpResponse, Http404
from django.forms.models import model_to_dict
from django.db.models import Q
from rest_framework import viewsets
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
from wagtail.models import Site
from .models import FeatureFlag, WebviewSettings
from .serializers import AdopterSerializer, ImageSerializer, DocumentSerializer, CustomizationRequestSerializer


class AdopterViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Adopter.objects.all()
    serializer_class = AdopterSerializer


class ImageViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Image.objects.all()
    serializer_class = ImageSerializer


class DocumentViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Document.objects.all()
    serializer_class = DocumentSerializer

    def get_queryset(self):
        search = self.request.query_params.get('search')
        if search:
            return Document.objects.filter(title__icontains=search)
        return Document.objects.all()


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
            # This is not my favorite way to do this but we need to keep the data on existing errata
            if field != 'OpenStax Concept Coach' and field != 'Rover by OpenStax' and field != 'OpenStax Tutor':
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
            

        if q:
            schools = schools.filter((Q(name__icontains=q) | Q(physical_city__icontains=q)| Q(physical_state_province__icontains=q)| Q(physical_country__icontains=q)))

        response = serializers.serialize("json", schools)
        return HttpResponse(response, content_type='application/json')
    else:
        return JsonResponse({'error': 'Invalid format requested.'})


def flags(request):
    flag_name_query_string = request.GET.get('flag', False)

    if not flag_name_query_string:
        data = list(FeatureFlag.objects.values('name', 'feature_active'))
        return JsonResponse({"all_flags": data})
    else:
        try:
            data = model_to_dict(FeatureFlag.objects.get(name=flag_name_query_string))
            return JsonResponse(data, safe=False)
        except FeatureFlag.DoesNotExist:
            raise Http404('Flag does not exist')


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


def webview_settings(request):
    data = list(WebviewSettings.objects.values('name', 'value'))
    return JsonResponse({"settings": data})

