from django.conf import settings
from django.shortcuts import render

from urllib.request import urlopen
from urllib.error import URLError


def versions(request):
    try:
        osweb_version = urlopen('{}/dist/fe-version.txt'.format(settings.BASE_URL)).read()
    except URLError:
        osweb_version = 'local'

    return render(request, 'versions.html', {
        'cms_version': settings.RELEASE_VERSION or 'local',
        'deployment_version': settings.DEPLOYMENT_VERSION or 'local',
        'osweb_version': osweb_version,
        'title': "OpenStax CMS Deployment Versions ({})".format(settings.ENVIRONMENT or 'local')
    })
