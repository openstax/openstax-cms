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
from django.conf import settings


YES = 'Yes'
NO = 'No'
YES_NO_CHOICES = (
    (YES, 'Yes'),
    (NO, 'No'),
)

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
CUSTOMER_SUPPORT = 'Sent to Customer Support'
ERRATA_RESOLUTIONS = (
    (DUPLICATE, 'Duplicate'),
    (NOT_AN_ERROR, 'Not An Error'),
    (WILL_NOT_FIX, 'Will Not Fix'),
    (APPROVED, 'Approved'),
    (MAJOR_BOOK_REVISION, 'Major Book Revision'),
    (CUSTOMER_SUPPORT, 'Sent to Customer Support'),
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
KINDLE = 'Kindle'
OTHER = 'Other'
ERRATA_RESOURCES = (
    (TEXTBOOK, 'Textbook'),
    (IBOOKS, 'iBooks version'),
    (INSTRUCTOR_SOLUTION, 'Instructor solution manual'),
    (STUDENT_SOLUTION, 'Student solution manual'),
    (TUTOR, 'OpenStax Tutor'),
    (CONCEPT_COACH, 'OpenStax Concept Coach'),
    (KINDLE, 'Kindle'),
    (OTHER, 'Other'),
)


class Errata(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)
    book = models.ForeignKey(Book)
    is_assessment_errata = models.CharField(
        max_length=100,
        choices=YES_NO_CHOICES,
        blank=True,
        null=True,
    )
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
    duplicate_id = models.OneToOneField('self', related_name='duplicate_report', null=True, blank=True)
    reviewed_date = models.DateField(blank=True, null=True, editable=False)
    corrected_date = models.DateField(blank=True, null=True)
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
        if (self.status == 'Editorial Review' or self.status == 'Reviewed' or self.status == 'Completed') and not self.is_assessment_errata:
            raise ValidationError({'is_assessment_errata': 'You must specify if this is an assessment errata.'})
        if (self.status == 'Completed' and self.resolution == 'Duplicate') and not self.duplicate_id:
            raise ValidationError({'duplicate_id': 'You must specify the duplicate report ID when resolution is marked duplicate.'})

    def save(self, *args, **kwargs):
        # update instance dates
        if self.resolution:
            self.resolution_date = now()
        if self.status == "Editorial Review" or self.status == "Reviewed":
            self.reviewed_date = now()
        if self.status == "Completed" and self.resolution != "Will Not Fix":
            self.corrected_date = now()

        # prefill resolution notes based on certain status and resolutions
        if self.resolution == "Duplicate" and not self.resolution_notes:
            self.resolution_notes = "This is a duplicate of another report for this book."
        if self.resolution == "Not An Error" and not self.resolution_notes:
            self.resolution_notes = "Our reviewers determined this was not an error."
        if self.resolution == "Will Not Fix" and not self.resolution_notes:
            self.resolution_notes = "Our reviewers determined the textbook meets scope, sequence, and accuracy requirements as is.  No change will be made."
        if self.resolution == "Major Book Revision" and not self.resolution_notes:
            self.resolution_notes = "Our reviewers determined this would require a significant book revision.  While we cannot make this change at this time, we will consider it for future editions of this book."
        if (self.status == "Reviewed" or self.status == "Completed") and self.resolution == "Approved" and not self.resolution_notes:
            self.resolution_notes = "Our reviewers accepted this change."
        if self.status == "Completed" and self.resolution == "Sent to Customer Support" and not self.resolution_notes:
            self.resolution_notes = "Forwarded to customer support."

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
        override_to = False
        if created:
            subject = "We received your submission"
            body = "Thanks for your help! Your errata submissions help keep OpenStax resources high quality and up to date."
            send_email = True
        elif instance.status == 'Reviewed' and (instance.resolution == 'Will Not Fix' or instance.resolution == 'Duplicate' or instance.resolution == 'Not An Error' or instance.resolution == 'Major Book Revision'):
            subject = "We reviewed your erratum suggestion"
            body = "Thanks again for your submission. Our reviewers have evaluated it and have determined there will be no change made."
            send_email = True
        elif instance.status == 'Reviewed' and instance.resolution == 'Approved':
            subject = "We received your submission"
            body = "Thanks again for your submission. Our reviewers have evaluated it and have determined that a change will be made. We will email you again when the appropriate resource has been updated."
            send_email = True
        elif instance.status == 'Completed' and instance.resolution == 'Approved':
            subject = "Your correction is live"
            body = "The correction you suggested has been incorporated into the appropriate OpenStax resource. Thanks for your help!"
            send_email = True
        elif instance.status == 'Completed' and instance.resolution == 'Sent to Customer Support':
            subject = "Errata report for Customer Support"
            body = "An errata report has been submitted that requires customer support attention."
            send_email = True
            override_to = True
            to = "support@openstax.org"

        if not override_to:
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
                'status': "In review",
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
