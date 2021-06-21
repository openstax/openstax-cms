from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.timezone import now
from django.utils import timezone
from django.template.defaultfilters import truncatewords
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.core.validators import MinValueValidator
from django.utils.html import format_html
from wagtail.core import hooks
from wagtail.admin.menu import MenuItem

from books.models import Book
from django.conf import settings
from oxauth.functions import get_user_info
from global_settings.functions import invalidate_cloudfront_caches


YES = 'Yes'
NO = 'No'
YES_NO_CHOICES = (
    (YES, 'Yes'),
    (NO, 'No'),
)

NEW = 'New'
EDITORIAL_REVIEW = 'Editorial Review'
ANDREW_EDITORIAL_REVIEW = 'Andrew Editorial Review'
ANTHONY_EDITORIAL_REVIEW = 'Anthony Editorial Review'
REVIEWED = 'Reviewed'
COMPLETED = 'Completed'
ERRATA_STATUS = (
    (NEW, 'New'),
    (EDITORIAL_REVIEW, 'Editorial Review'),
    (ANDREW_EDITORIAL_REVIEW, 'Andrew Editorial Review'),
    (ANTHONY_EDITORIAL_REVIEW,'Anthony Editorial Review'),
    (REVIEWED, 'Reviewed'),
    (COMPLETED, 'Completed'),
)

DUPLICATE = 'Duplicate'
NOT_AN_ERROR = 'Not An Error'
WILL_NOT_FIX = 'Will Not Fix'
APPROVED = 'Approved'
MAJOR_BOOK_REVISION = 'Major Book Revision'
TECHNICAL_ERROR = 'Technical Error'
PARTNER_PRODUCT = 'Partner Product'
CUSTOMER_SUPPORT = 'Sent to Customer Support'
MORE_INFO_REQUESTED = 'More Information Requested'
ERRATA_RESOLUTIONS = (
    (DUPLICATE, 'Duplicate'),
    (NOT_AN_ERROR, 'Not An Error'),
    (WILL_NOT_FIX, 'Will Not Fix'),
    (APPROVED, 'Approved'),
    (MAJOR_BOOK_REVISION, 'Major Book Revision'),
    (TECHNICAL_ERROR, 'Technical Error'),
    (PARTNER_PRODUCT, 'Partner Product'),
    (CUSTOMER_SUPPORT, 'Sent to Customer Support'),
    (MORE_INFO_REQUESTED, 'More Information Requested'),
)

FACTUAL = 'Other factual inaccuracy in content'
PEDAGOGICAL = 'General/pedagogical suggestion or question'
CALCULATION = 'Incorrect answer, calculation, or solution'
LINK = 'Broken link'
TYPO = 'Typo'
OTHER = 'Other'
ERRATA_ERROR_TYPES = (
    (FACTUAL, 'Other factual inaccuracy in content'),
    (PEDAGOGICAL, 'General/pedagogical suggestion or question'),
    (CALCULATION, 'Incorrect answer, calculation, or solution'),
    (LINK, 'Broken link'),
    (TYPO, 'Typo'),
    (OTHER, 'Other'),
)

# These are served through the API using api.views.errata_fields
ERRATA_RESOURCES = (
    ('Textbook', 'Textbook'),
    ('iBooks version', 'iBooks version'),
    ('Instructor solution manual', 'Instructor solution manual'),
    ('Student solution manual', 'Student solution manual'),
    ('OpenStax Tutor', 'OpenStax Tutor'),
    ('OpenStax Concept Coach', 'OpenStax Concept Coach'),
    ('Rover by OpenStax', 'Rover by OpenStax'),
    ('OpenStax + SE', 'OpenStax + SE'),
    ('Kindle', 'Kindle'),
    ('Study guide in online view', 'Study guide in online view'),
    ('Other', 'Other'),
)

BLOCK_TYPES = (
    ('Shadown Ban', 'Shadow Ban'),
    ('Force Block', 'Force Block'),
)

EMAIL_CASES = (
    ('Created in Fall', 'Created in Fall'),
    ('Created in Spring', 'Created in Spring'),
    ('Reviewed and (will not fix, or duplicate, or not an error, or major book revision)', 'Reviewed and (will not fix, or duplicate, or not an error, or major book revision)'),
    ('Reviewed and Approved', 'Reviewed and Approved'),
    ('Completed and Sent to Customer Support', 'Completed and Sent to Customer Support'),
    ('More Information Requested', 'More Information Requested'),
    ('Getting New Edition', 'Getting New Edition'),
    ('Partner Product', 'Partner Product'),
    ('Generic Completed Response', 'Generic Completed Response'),
    ('Technical Error', 'Technical Error'),
)

def is_user_blocked(account_id):
    block_query = BlockedUser.objects.filter(account_id=account_id)

    if block_query and block_query[0].type == "Force Block":
        raise ValidationError('This account does not have privileges to submit an erratum.')

def is_user_shadow_blocked(account_id):
    block_query = BlockedUser.objects.filter(account_id=account_id)

    if block_query and block_query[0].type == "Shadown Ban":
        return True
    else:
        return False

class BlockedUser(models.Model):
    account_id = models.IntegerField(blank=True, null=True, validators=[MinValueValidator(0)])
    reason = models.TextField(blank=True, null=True)
    type = models.CharField(
        max_length=100,
        choices=BLOCK_TYPES,
        blank=True,
        null=True
    )

    @property
    def fullname(self):
        try:
            user = get_user_info(self.account_id)
            return user['fullname']
        except:
            return None

    def __str__(self):
        return str(self.account_id)

class Errata(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    # TODO: If we seperate the Errata application from the CMS, the books will need to be store differently. `book` will be removed, `openstax_book` will store as string
    book = models.ForeignKey(Book, on_delete=models.PROTECT)
    openstax_book = models.CharField(max_length=255, null=True, blank=True, editable=False)

    is_assessment_errata = models.CharField(
        max_length=100,
        choices=YES_NO_CHOICES,
        blank=True,
        null=True,
    )
    assessment_id = models.CharField(max_length=255, null=True, blank=True)
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
    duplicate_id = models.ForeignKey('self', related_name='duplicate_report', null=True, blank=True, on_delete=models.PROTECT)
    reviewed_date = models.DateField(blank=True, null=True, editable=False)
    corrected_date = models.DateField(blank=True, null=True)
    archived = models.BooleanField(default=False)
    junk = models.BooleanField(default=False, help_text='Flagging the erratum as junk will automatically flag it for archive as well.')
    location = models.TextField(blank=True, null=True)
    additional_location_information = models.TextField(blank=True, null=True)
    detail = models.TextField()
    resolution_notes = models.TextField(blank=True, null=True, help_text='Leaving the resolution notes blank will allow the field to auto-fill with the appropriate text based on status/resolution selections.')
    resolution_date = models.DateField(blank=True, null=True)
    internal_notes = models.TextField(blank=True, null=True, help_text='Only users with errata admin access can view and edit the contents of this field.')
    error_type = models.CharField(
        max_length=100,
        choices=ERRATA_ERROR_TYPES,
        blank=True,
        null=True
    )
    error_type_other = models.CharField(max_length=255, blank=True, null=True)
    number_of_errors = models.PositiveIntegerField(default=1)
    resource = models.CharField(
        max_length=100,
        choices=ERRATA_RESOURCES,
        blank=True,
        null=True
    )
    resource_other = models.CharField(max_length=255, blank=True, null=True)

    # TODO: We are keeping the Foreign Key to the local user until the migrations to production are complete, then remove submitted_by and submitter_email_address
    submitted_by = models.ForeignKey(User, blank=True, null=True, on_delete=models.SET_NULL)
    submitter_email_address = models.EmailField(blank=True, null=True)

    submitted_by_account_id = models.IntegerField(blank=True, null=True, validators=[MinValueValidator(0), is_user_blocked])
    accounts_user_email = models.CharField(max_length=255, null=True, blank=True)
    accounts_user_name = models.CharField(max_length=255, null=True, blank=True)
    accounts_user_faculty_status = models.CharField(max_length=255, null=True, blank=True)

    file_1 = models.FileField(upload_to='errata/user_uploads/1/', blank=True, null=True)
    file_2 = models.FileField(upload_to='errata/user_uploads/2/', blank=True, null=True)

    # @property
    # def user_email(self):
    #     try:
    #         user = get_user_info(self.submitted_by_account_id)
    #         return user['email']
    #     except:
    #         return None
    #
    # @property
    # def user_name(self):
    #     try:
    #         user = get_user_info(self.submitted_by_account_id)
    #         return user['fullname']
    #     except:
    #         return None
    #
    # @property
    # def user_faculty_status(self):
    #     try:
    #         user = get_user_info(self.submitted_by_account_id)
    #         return user['faculty_status']
    #     except:
    #         return None

    @property
    def accounts_link(self):
        try:
            return format_html('<a href="{}/admin/users/{}/edit" target="_blank">OpenStax Accounts Link</a>'.format(settings.ACCOUNTS_URL, self.submitted_by_account_id))
        except:
            return None

    @property
    def short_detail(self):
        return truncatewords(self.detail, 15)

    def clean(self):
        if self.status == 'Completed' and not self.resolution or self.status == 'Reviewed' and not self.resolution:
            raise ValidationError({'resolution': 'Resolution is required if status is completed or reviewed.'})
        if (self.status == 'Editorial Review' or self.status == 'Andrew Editorial Review' or self.status == 'Anthony Editorial Review' or self.status == 'Reviewed' or self.status == 'Completed') and not self.is_assessment_errata:
            raise ValidationError({'is_assessment_errata': 'You must specify if this is an assessment errata.'})
        if (self.status == 'Completed' and self.resolution == 'Duplicate') and not self.duplicate_id:
            raise ValidationError({'duplicate_id': 'You must specify the duplicate report ID when resolution is marked duplicate.'})

    def save(self, *args, **kwargs):
        # update instance dates
        if self.resolution:
            self.resolution_date = timezone.now()
        if self.status == "Reviewed":
            self.reviewed_date = timezone.now()
        if self.status == "Completed" and self.resolution != "Will Not Fix":
            self.corrected_date = timezone.now()
            # book updated field is being used front-end to show google the content is being maintained
            Book.objects.filter(pk=self.book.pk).update(updated=now())

        # prefill resolution notes based on certain status and resolutions
        if self.resolution == "Duplicate" and not self.resolution_notes:
            self.resolution_notes = "This is a duplicate of report <a href='https://openstax.org/errata/" + str(self.duplicate_id.id) + "'>" + str(self.duplicate_id.id) + "</a>."
        if self.resolution == "Not An Error" and not self.resolution_notes:
            self.resolution_notes = "Our reviewers determined this was not an error in the most current version of the book’s content. It’s possible that you are using an old version of the content via a PDF or printed text. If possible, please double check that you see the error in the web version of the book, and provide a screenshot and more detail if you believe we have made a mistake."
        if self.resolution == "Will Not Fix" and not self.resolution_notes:
            self.resolution_notes = "Our reviewers determined the textbook meets scope, sequence, and accuracy requirements as is.  No change will be made."
        if self.resolution == "Major Book Revision" and not self.resolution_notes:
            self.resolution_notes = "Our reviewers determined this would require a significant book revision.  While we cannot make this change at this time, we will consider it for future editions of this book."
        if (self.status == "Reviewed" or self.status == "Completed") and self.resolution == "Approved" and not self.resolution_notes:
            self.resolution_notes = "Our reviewers accepted this change, and it will be included in the next print cycle."
        if self.status == "Completed" and self.resolution == "Sent to Customer Support" and not self.resolution_notes:
            self.resolution_notes = "Thank you for this feedback. Your report has been escalated to our Customer Service team and they will contact you with further details."
        if self.resolution == 'Technical Error' and not self.resolution_notes:
            self.resolution_notes = 'This a technical error and the proper departments have been notified so that it can be fixed. Thank you for your submission.'
        if self.resolution == 'More Information Requested' and not self.resolution_notes:
            self.resolution_notes = 'Thank you for the feedback. Unfortunately, our reviewers were unable to locate this error. Please submit a new report with additional information, such as a link to the relevant content, or a screenshot.'
        if self.resolution == 'Partner Product' and not self.resolution_notes:
            self.resolution_notes = 'This issue is occurring on a platform that is not managed by OpenStax. We will make our best efforts to get this resolved; however, we suggest reporting this issue within the platform you are using.'

        #auto filling a couple of fields if it is clear that it is an assessment errata based on the text that tutor fills into the additional_location_information field
        if self.additional_location_information and self.resource == 'OpenStax Tutor' and ('@' in self.additional_location_information.split()[0]):
            self.is_assessment_errata = 'Yes'
            self.assessment_id = self.additional_location_information.split('@', )[0]

        # set to archived if user is shadow banned
        if(is_user_shadow_blocked(self.submitted_by_account_id)):
            self.archived = True

        # invalidate cloudfront cache so FE updates (remove when errata is no longer in CMS)
        invalidate_cloudfront_caches()

        super(Errata, self).save(*args, **kwargs)

    @hooks.register('register_admin_menu_item')
    def register_errata_menu_item():
        return MenuItem('Errata', '/django-admin/errata/errata', classnames='icon icon-form', order=10000)

    # @hooks.register('register_admin_menu_item')
    # def register_errata_menu_item():
    #     return MenuItem('Errata (beta)', '/api/errata/admin/dashboard/', classnames='icon icon-form', order=10000)

    def __str__(self):
        return self.book.book_title

    class Meta:
        verbose_name = "erratum"
        verbose_name_plural = "erratum"

class EmailText(models.Model):

    email_case = models.CharField(
        max_length=100,
        choices=EMAIL_CASES,
        blank=True,
        null=True
    )
    email_subject_text = models.CharField(max_length=255, blank=True, null=True)
    email_body_text = models.TextField()
    notes = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return self.email_case

    class Meta:
        verbose_name = "email text"
        verbose_name_plural = "email text"


@receiver(post_save, sender=Errata, dispatch_uid="send_status_update_email")
def send_status_update_email(sender, instance, created, **kwargs):
        send_email = False
        override_to = False

        if created:
            if instance.book.book_state == 'New Edition Forthcoming (Show new edition correction schedule)':
                email_text = EmailText.objects.get(email_case='Getting New Edition')
                subject = email_text.email_subject_text
                body = email_text.email_body_text
                send_email = True
            else:
                if instance.created.month in (11, 12, 1, 2):
                    email_text = EmailText.objects.get(email_case='Created in Fall')
                    subject = email_text.email_subject_text
                    body = email_text.email_body_text
                    send_email = True
                else:
                    email_text = EmailText.objects.get(email_case='Created in Spring')
                    subject = email_text.email_subject_text
                    body = email_text.email_body_text
                    send_email = True
        elif instance.status == 'Reviewed' and (instance.resolution == 'Will Not Fix' or instance.resolution == 'Duplicate' or instance.resolution == 'Not An Error' or instance.resolution == 'Major Book Revision'):
            email_text = EmailText.objects.get(email_case='Reviewed and (will not fix, or duplicate, or not an error, or major book revision)')
            subject = email_text.email_subject_text
            body = email_text.email_body_text
            send_email = True
        elif instance.status == 'Reviewed' and instance.resolution == 'Approved':
            email_text = EmailText.objects.get(email_case='Reviewed and Approved')
            subject = email_text.email_subject_text
            body = email_text.email_body_text
            send_email = True
        elif instance.status == 'Completed' and instance.resolution == 'Sent to Customer Support':
            email_text = EmailText.objects.get(email_case='Completed and Sent to Customer Support')
            subject = email_text.email_subject_text
            body = email_text.email_body_text
            send_email = True
            override_to = True
            to = "support@openstax.org"
        elif instance.status == 'Completed' and instance.resolution == 'Partner Product':
            email_text = EmailText.objects.get(email_case='Partner Product')
            subject = email_text.email_subject_text
            body = email_text.email_body_text
            send_email = True
        elif instance.status == 'Completed' and instance.resolution == 'Technical Error':
            email_text = EmailText.objects.get(email_case='Technical Error')
            subject = email_text.email_subject_text
            body = email_text.email_body_text
            send_email = True
        elif instance.resolution == 'More Information Requested':
            email_text = EmailText.objects.get(email_case='More Information Requested')
            subject = email_text.email_subject_text
            body = email_text.email_body_text
            send_email = True
        elif instance.status == 'Completed' and not send_email:
            email_text = EmailText.objects.get(email_case='Generic Completed Response')
            subject = email_text.email_subject_text
            body = email_text.email_body_text
            send_email = True

        if not override_to:
            if instance.submitted_by_account_id:
                user = get_user_info(instance.submitted_by_account_id)
                to = user['email']
            elif instance.submitter_email_address:
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
    errata = models.ForeignKey(Errata, on_delete=models.PROTECT)
    file = models.FileField(upload_to='errata/internal/')

    def __str__(self):
        return self.file.name
