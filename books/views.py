from random import randrange
from django.shortcuts import redirect
from django.http import Http404
from django.views.decorators.csrf import csrf_exempt
from .models import BookIndex, Book


@csrf_exempt
def book_index(request):
    page = BookIndex.objects.all()[0]
    return redirect('/apps/cms/api/v2/pages/{}/?cache={}'.format(page.pk, randrange(100000)))


@csrf_exempt
def book_detail(request, slug):
    try:
        page = Book.objects.get(slug=slug)
        return redirect('/apps/cms/api/v2/pages/{}/?cache={}'.format(page.pk, randrange(100000)))
    except Book.DoesNotExist:
        raise Http404("Book does not exist.")
