from django.db import models
from django.utils.timezone import now
from django.template.defaultfilters import truncatewords
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User

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
APPROVED = 'Approved'
MAJOR_BOOK_REVISION = 'Major Book Revision'
ERRATA_RESOLUTIONS = (
    (DUPLICATE, 'Duplicate'),
    (NOT_AN_ERROR, 'Not An Error'),
    (WILL_NOT_FIX, 'Will Not Fix'),
    (APPROVED, 'Approved'),
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
    location = models.TextField(blank=True, null=True)
    detail = models.TextField()
    resolution_notes = models.TextField(blank=True, null=True)
    resolution_date = models.DateField(blank=True, null=True)
    internal_notes = models.TextField(blank=True, null=True)
    error_type = models.ForeignKey(ErrorType, blank=True, null=True, on_delete=models.PROTECT)
    resource = models.ManyToManyField(Resource)
    submitted_by = models.ForeignKey(User, blank=True, null=True)
    submitter_email_address = models.EmailField(blank=True, null=True)

    @property
    def short_detail(self):
        return truncatewords(self.detail, 15)

    def resources(self):
        return ", ".join([r.name for r in self.resource.all()])

    def clean(self):
        if self.status == 'Completed' and not self.resolution:
            raise ValidationError({'resolution': 'Resolution is required if status is complete.'})

    def save(self, *args, **kwargs):
        if self.resolution:
            self.resolution_date = now()
        super(Errata, self).save(*args, **kwargs)

    @hooks.register('register_admin_menu_item')
    def register_errata_menu_item():
        return MenuItem('Errata', '/django-admin/errata/errata', classnames='icon icon-openquote', order=10000)

    def __str__(self):
        return self.book.book_title

    class Meta:
        verbose_name = "erratum"
        verbose_name_plural = "erratum"


class InternalDocumentation(models.Model):
    errata = models.ForeignKey(Errata)
    file = models.FileField(upload_to='errata/internal/')


class ExternalDocumentation(models.Model):
    errata = models.ForeignKey(Errata)
    file = models.FileField(upload_to='errata/external/')