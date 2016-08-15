from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.renderers import JSONRenderer
from .models import NewsIndex, NewsArticle
from .serializers import NewsIndexSerializer, NewsArticleSerializer


class JSONResponse(HttpResponse):
    """
    An HttpResponse that renders its content into JSON.
    """
    def __init__(self, data, **kwargs):
        content = JSONRenderer().render(data)
        kwargs['content_type'] = 'application/json'
        super(JSONResponse, self).__init__(content, **kwargs)


@csrf_exempt
def news_index(request):
    page = NewsIndex.objects.all()[0]
    books = NewsArticle.objects.all()
    serializer = NewsIndexSerializer(page)
    return JSONResponse(serializer.data)


@csrf_exempt
def news_detail(request, slug):
    """
    Retrieve a pages JSON by slug.
    """

    try:
        page = NewsArticle.objects.get(slug=slug)
        serializer = NewsArticleSerializer(page)
        return JSONResponse(serializer.data)
    except NewsArticle.DoesNotExist:
        return HttpResponse(status=404)

