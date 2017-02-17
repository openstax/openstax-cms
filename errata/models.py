from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.timezone import now
from django.template.defaultfilters import truncatewords
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.template.loader import render_to_string

from wagtail.wagtailcore import hooks
from wagtail.wagtailadmin.menu import MenuItem

from books.models import Book
from openstax import settings


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

FACTUAL = 'Other factual inaccuracy in content'
PEDAGOGICAL = 'General/pedagogical suggestion or question'
CALCULATION = 'Incorrect calculation or solution'
LINK = 'Broken link'
TYPO = 'Typo'
OTHER = 'Other'
ERRATA_ERROR_TYPES = (
    (FACTUAL, 'Other factual inaccuracy in content'),
    (PEDAGOGICAL, 'General/pedagogical suggestion or question'),
    (CALCULATION, 'Incorrect calculation or solution'),
    (LINK, 'Broken link'),
    (TYPO, 'Typo'),
    (OTHER, 'Other'),
)

TEXTBOOK = 'Textbook'
IBOOKS = 'iBooks version'
INSTRUCTOR_SOLUTION = 'Instructor solution manual'
STUDENT_SOLUTION = 'Student solution manual'
TUTOR = 'OpenStax Tutor'
CONCEPT_COACH = 'OpenStax Concept Coach'
OTHER = 'Other'
ERRATA_RESOURCES = (
    (TEXTBOOK, 'Textbook'),
    (IBOOKS, 'iBooks version'),
    (INSTRUCTOR_SOLUTION, 'Instructor solution manual'),
    (STUDENT_SOLUTION, 'Student solution manual'),
    (TUTOR, 'OpenStax Tutor'),
    (CONCEPT_COACH, 'OpenStax Concept Coach'),
    (OTHER, 'Other'),
)


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
    error_type = models.CharField(
        max_length=100,
        choices=ERRATA_ERROR_TYPES,
        blank=True,
        null=True
    )
    error_type_other = models.CharField(max_length=255, blank=True, null=True)
    resource = models.CharField(
        max_length=100,
        choices=ERRATA_RESOURCES,
        blank=True,
        null=True
    )
    resource_other = models.CharField(max_length=255, blank=True, null=True)
    submitted_by = models.ForeignKey(User, blank=True, null=True)
    submitter_email_address = models.EmailField(blank=True, null=True)
    file_1 = models.FileField(upload_to='errata/user_uploads/1/', blank=True, null=True)
    file_2 = models.FileField(upload_to='errata/user_uploads/2/', blank=True, null=True)

    @property
    def short_detail(self):
        return truncatewords(self.detail, 15)

    def clean(self):
        if self.status == 'Completed' and not self.resolution or self.status == 'Reviewed' and not self.resolution:
            raise ValidationError({'resolution': 'Resolution is required if status is completed or reviewed.'})

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

@receiver(post_save, sender=Errata, dispatch_uid="send_status_update_email")
def send_status_update_email(sender, instance, created, **kwargs):
        send_email = False
        if created:
            subject = "We received your submission"
            body = "Thanks for your help! Your errata submissions help keep OpenStax resources high quality and up to date."
            send_email = True
        elif instance.status == 'Reviewed' and instance.resolution == 'Will Not Fix':
            subject = "We reviewed your erratum suggestion"
            body = "Thanks again for your submission. Our reviewers have evaluated it and have determined there will be no change made."
            send_email = True
        elif instance.status == 'Reviewed' and instance.resolution == 'Approved':
            subject = "We received your submission"
            body = "Thanks again for your submission. Our reviewers have evaluated it and have determined that a change will be made. We will email you again when the appropriate resource has been updated."
            send_email = True
        elif instance.status == 'Completed':
            subject = "Your correction is live"
            body = "The correction you suggested has been incorporated into the appropriate OpenStax resource. Thanks for your help!"
            send_email = True

        if instance.submitter_email_address:
            to = instance.submitter_email_address
        elif instance.submitted_by:
            to = instance.submitted_by.email
        else:
            send_email = False

        if send_email:
            errata_email_info = {
                'subject': subject,
                'body': body,
                'status': instance.status,
                'resolution': instance.resolution,
                'created': created,
                'id': instance.id,
                'title': instance.book.title,
                'source': instance.resource,
                'error_type': instance.error_type,
                'location': instance.location,
                'description': instance.detail,
                'date_submitted': instance.created,
                'host': settings.HOST_LINK,
            }
            msg_plain = render_to_string('templates/email.txt', errata_email_info)
            msg_html = render_to_string('templates/email.html', errata_email_info)

            send_mail(
                subject,
                msg_plain,
                'noreply@openstax.org',
                [to],
                html_message=msg_html,
            )


class InternalDocumentation(models.Model):
    errata = models.ForeignKey(Errata)
    file = models.FileField(upload_to='errata/internal/')
