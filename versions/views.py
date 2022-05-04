from django.conf import settings
from django.shortcuts import render

from urllib.request import urlopen
from urllib.error import URLError


def versions(request):
    try:
        with urlopen('{}/dist/fe-version.txt'.format(settings.BASE_URL)) as connection:
            osweb_version = connection.read().decode('utf-8')
    except URLError:
        osweb_version = 'local'

    return render(request, 'versions.html', {
        'cms_version': settings.RELEASE_VERSION or 'local',
        'deployment_version': settings.DEPLOYMENT_VERSION or 'none',
        'osweb_version': osweb_version,
        'title': "OpenStax CMS Deployment Versions ({})".format(settings.ENVIRONMENT or 'local')
    })
