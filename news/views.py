from django.shortcuts import redirect
from django.views.decorators.csrf import csrf_exempt
from .models import NewsIndex, NewsArticle


@csrf_exempt
def news_index(request):
    page = NewsIndex.objects.all()[0]
    return redirect('/api/v2/pages/{}'.format(page.pk))


@csrf_exempt
def news_detail(request, slug):
    page = NewsArticle.objects.get(slug=slug)
    return redirect('/api/v2/pages/{}'.format(page.pk))
