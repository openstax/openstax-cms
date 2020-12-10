from django.http import Http404
from django.shortcuts import redirect
from django.views.decorators.csrf import csrf_exempt
from .models import NewsIndex, NewsArticle, PressIndex, PressRelease


@csrf_exempt
def news_index(request):
    page = NewsIndex.objects.all()[0]
    return redirect('/apps/cms/api/v2/pages/{}/'.format(page.pk))

@csrf_exempt
def news_detail(request, slug):
    try:
        page = NewsArticle.objects.get(slug=slug)
        return redirect('/apps/cms/api/v2/pages/{}/'.format(page.pk))
    except NewsArticle.DoesNotExist:
        raise Http404('News article does not exist')

@csrf_exempt
def press_index(request):
    page = PressIndex.objects.all()[0]
    return redirect('/apps/cms/api/v2/pages/{}/'.format(page.pk))

@csrf_exempt
def press_detail(request, slug):
    page = PressRelease.objects.get(slug=slug)
    return redirect('/apps/cms/api/v2/pages/{}/'.format(page.pk))
