from django.core import serializers
from django.http import JsonResponse, HttpResponse
from rest_framework import viewsets
from salesforce.models import Adopter
from social.apps.django_app.default.models import \
    DjangoStorage as SocialAuthStorage
from global_settings.models import StickyNote, Footer
from wagtail.images.models import Image
from wagtail.documents.models import Document

from .serializers import AdopterSerializer, ImageSerializer, DocumentSerializer
from accounts.functions import update_user_status, get_or_create_user_profile

from salesforce.models import School


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


def user_api(request):
    user = request.user
    profile = get_or_create_user_profile(user)

    if profile:
        if not profile.uuid or profile.faculty_status == 'no_faculty_info' or profile.faculty_status == 'pending_faculty':
            try:
                update_user_status(user)
            except IndexError:
                print("[error] cannot find account instance for that user")

    try:
        social_auth = SocialAuthStorage.user.get_social_auth_for_user(user)
        user.accounts_id = social_auth[0].uid
    except:
        user.accounts_id = None

    try:
        return JsonResponse({
            'id': user.pk,
            'email': user.email,
            'username': user.username,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'is_staff': user.is_staff,
            'is_superuser': user.is_superuser,
            'groups': list(user.groups.values_list('name', flat=True)),
            'accounts_id': user.accounts_id,
            'accounts_uuid': profile.uuid,
            'faculty_status': profile.faculty_status,
            'pending_verification': profile.faculty_status == 'pending_faculty'
        })
    except:
        return JsonResponse({
            'id': False,
            'email': '',
            'username': '',
            'first_name': '',
            'last_name': '',
            'is_staff': False,
            'is_superuser': False,
            'groups': [],
            'accounts_id': None,
            'accounts_uuid': None,
            'faculty_status': None,
            'pending_verification': False
        })


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
    name = request.GET.get('name', False)
    id = request.GET.get('id', False)

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
            schools = School.objects.filter(name__icontains=name)
            print(schools.count())
        if id:
            schools = School.objects.filter(pk=id)

        response = serializers.serialize("json", schools)
        return HttpResponse(response, content_type='application/json')
    else:
        return JsonResponse({'error': 'Invalid format requested.'})
