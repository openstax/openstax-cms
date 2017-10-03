import json

from oauthlib.oauth2 import BackendApplicationClient
from requests_oauthlib import OAuth2Session
from urllib.parse import urlencode
from urllib.request import urlopen

from django.conf import settings
from django.contrib.auth.models import User, Group

from social.apps.django_app.default.models import \
    DjangoStorage as SocialAuthStorage
from .models import Profile


def get_or_create_user_profile(user):
    profile, created = Profile.objects.get_or_create(user=user)

    return profile


def get_token():
    client = BackendApplicationClient(client_id=settings.SOCIAL_AUTH_OPENSTAX_KEY)
    oauth = OAuth2Session(client=client)
    token = oauth.fetch_token(token_url=settings.ACCESS_TOKEN_URL,
                              client_id=settings.SOCIAL_AUTH_OPENSTAX_KEY,
                              client_secret=settings.SOCIAL_AUTH_OPENSTAX_SECRET)

    return token


def update_user_status(user):
    token = get_token()
    profile = get_or_create_user_profile(user)

    social_user = SocialAuthStorage.user.objects.filter(user_id=user.id)
    accounts_id = social_user[0].uid

    url = settings.USERS_QUERY + urlencode({
        'q': 'id:{}'.format(accounts_id),
        'access_token': token['access_token']
    })

    with urlopen(url) as url:
        data = json.loads(url.read().decode())

        print(data)

        # update user profile with faculty status
        faculty_status = data['items'][0]['faculty_status']
        profile.faculty_status = faculty_status

        #update user profile with uuid
        uuid = data['items'][0]['uuid']
        profile.uuid = uuid

        profile.save()

        #update email address if possible
        try:
            contact_infos = data['items'][0]['contact_infos']
            most_recent_email = max(contact_infos, key=lambda x: x['id'])
            email = most_recent_email['value']
        except ValueError:
            pass #no saved emails

        #update user groups
        self_reported_role = data['items'][0]['self_reported_role']
        faculty_status = data['items'][0]['faculty_status']
        applications = data['items'][0]['applications']

        if self_reported_role == 'student':
            group, created = Group.objects.get_or_create(name=self_reported_role.title())
            group.user_set.add(user)

        if faculty_status == 'confirmed_faculty':
            group, created = Group.objects.get_or_create(name='Faculty')
            group.user_set.add(user)

        if applications and 'OpenStax Tutor' in [app['name'] for app in applications]:
            group, created = Group.objects.get_or_create(name='Tutor')
            group.user_set.add(user)

        return user
