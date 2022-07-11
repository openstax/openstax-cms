from random import randrange
from urllib.parse import urlparse

from django.shortcuts import redirect
from django.http import Http404
from django.views.decorators.csrf import csrf_exempt
from .models import BookIndex, Book


@csrf_exempt
def book_index(request):
    page = BookIndex.objects.all()[0]
    return redirect('/apps/cms/api/v2/pages/{}/'.format(page.pk))


@csrf_exempt
def book_detail(request, slug):
    x_param = request.GET.get('x', False)
    print(str(request))
    print('x_param: ' + str(x_param))
    # print('request.path: ' + str(request.path))
    # if '?' in request.path:
    #     query = urlparse(request.path).query
    #     print('query:' + str(query))
    try:
        page = Book.objects.get(slug=slug)
        if x_param == 'y':
            return redirect('/apps/cms/api/v2/pages/{}/?x=y'.format(page.pk))
        else:
            return redirect('/apps/cms/api/v2/pages/{}/'.format(page.pk))
    except Book.DoesNotExist:
        raise Http404("Book does not exist.")
