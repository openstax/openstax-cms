from django.core.management.base import BaseCommand

from snippets.models import ContentLicense
from books.models import Book

class Command(BaseCommand):
    help="add CC license to live books that do not have one"

    def handle(self, *args, **options):
        nc_sa_books = ['Cálculo volumen 1', 'Cálculo volumen 2', 'Cálculo volumen 3']
        books = Book.objects.filter(license_name=None, book_state='live')
        for book in books:
            if book.book_title in nc_sa_books:
                book.license_name = 'Creative Commons Attribution-NonCommercial-ShareAlike License'
            else:
                book.license_name = 'Creative Commons Attribution License'
            book.save()
            print('Updated license for ' + str(book.book_title))
