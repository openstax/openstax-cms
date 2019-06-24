from django.http import HttpResponse
from django.shortcuts import redirect
from django.views.decorators.csrf import csrf_exempt
from wagtail.core.models import Page


@csrf_exempt
def page_detail(request, slug):
    """
    Redirects the page api to the Wagtail API. This should eventually be removed as the FE moves to the new /api/v2/ endpoint
    """
    try:
        page = Page.objects.filter(slug=slug).first()
        return redirect('/apps/cms/api/v2/pages/{}/'.format(page.pk))
    except:
        return HttpResponse(status=404)
