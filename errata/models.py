from django.db import models

from wagtail.wagtailcore import hooks
from wagtail.wagtailadmin.menu import MenuItem

from books.models import Book


NEW = 'New'
EDITORIAL_REVIEW = 'Editorial Review'
REVIEWED = 'Reviewed'
COMPLETED = 'Completed'
ERRATA_STATUS = (
    (NEW, 'New'),
    (EDITORIAL_REVIEW, 'Editorial Review'),
    (REVIEWED, 'Reviewed'),
    (COMPLETED, 'Completed'),
)

DUPLICATE = 'Duplicate'
NOT_AN_ERROR = 'Not An Error'
WILL_NOT_FIX = 'Will Not Fix'
PUBLISHED = 'Published'
MAJOR_BOOK_REVISION = 'Major Book Revision'
ERRATA_RESOLUTIONS = (
    (DUPLICATE, 'Duplicate'),
    (NOT_AN_ERROR, 'Not An Error'),
    (WILL_NOT_FIX, 'Will Not Fix'),
    (PUBLISHED, 'Published'),
    (MAJOR_BOOK_REVISION, 'Major Book Revision'),
)


class Resource(models.Model):
    name = models.CharField(max_length=250)

    def __str__(self):
        return self.name


class ErrorType(models.Model):
    name = models.CharField(max_length=250)

    def __str__(self):
        return self.name


class Errata(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)
    book = models.ForeignKey(Book)
    status = models.CharField(
        max_length=100,
        choices=ERRATA_STATUS,
        default=NEW,
    )
    resolution = models.CharField(
        max_length=100,
        choices=ERRATA_RESOLUTIONS,
        blank=True,
        null=True,
    )
    archived = models.BooleanField(default=False)
    location = models.CharField(max_length=250, blank=True, null=True)
    detail = models.TextField()
    resolution_notes = models.TextField(blank=True, null=True)
    resolution_date = models.DateField(blank=True, null=True)
    internal_notes = models.TextField(blank=True, null=True)
    error_type = models.ForeignKey(ErrorType, blank=True, null=True, on_delete=models.PROTECT)
    resource = models.ManyToManyField(Resource)
    submitter_email_address = models.EmailField(blank=True, null=True)

    def resources(self):
        return ", ".join([r.name for r in self.resource.all()])

    @hooks.register('register_admin_menu_item')
    def register_errata_menu_item():
        return MenuItem('Errata', '/django-admin/errata/errata', classnames='icon icon-openquote', order=10000)

    def __str__(self):
        return self.book.title
