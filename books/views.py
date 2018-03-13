from django.shortcuts import redirect
from django.views.decorators.csrf import csrf_exempt
from .models import BookIndex, Book


@csrf_exempt
def book_index(request):
    page = BookIndex.objects.all()[0]
    return redirect('/api/v2/pages/{}'.format(page.pk))


@csrf_exempt
def book_detail(request, slug):
    page = Book.objects.get(slug=slug)
    return redirect('/api/v2/pages/{}'.format(page.pk))
