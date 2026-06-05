from django.db import models
from django.core.exceptions import ValidationError
from wagtail.admin.panels import FieldPanel, MultiFieldPanel
from wagtail.models import TranslatableMixin
from openstax.functions import build_image_url

COLOR_SCHEME_CHOICES = (
    ('red', 'Red'),
    ('deep-green', 'Deep Green'),
    ('green', 'Green'),
    ('orange', 'Orange'),
)

MESSAGE_TYPE_CHOICES = (
    ('goal', 'Goal'),
    ('message', 'Message'),
)


class ThankYouNote(models.Model):
    thank_you_note = models.TextField(default="", blank=True)
    first_name = models.CharField(max_length=255, default="", blank=True)
    last_name = models.CharField(max_length=255, default="", blank=True)
    institution = models.CharField(max_length=255, default="", blank=True)
    created = models.DateField(auto_now_add=True)
    consent_to_share_or_contact = models.BooleanField(default=False)
    contact_email_address = models.EmailField(blank=True, null=True)
    source = models.CharField(max_length=255, default="", blank=True)
    salesforce_id = models.CharField(max_length=255, default="", blank=True, help_text="Not null if uploaded to Salesforce")


    def __str__(self):
        return f'{self.first_name} {self.last_name}'

    class Meta:
        verbose_name = 'Thank You Note'
        verbose_name_plural = 'Thank You Notes'


class DonationPopup(models.Model):
    download_image = models.ImageField(null=True, blank=True)
    download_ready = models.TextField(default="", blank=True)
    header_image = models.ImageField(null=True, blank=True)
    header_title = models.TextField(default="", blank=True)
    header_subtitle = models.TextField(default="", blank=True)
    give_link_text = models.CharField(max_length=255)
    give_link = models.TextField(default="", blank=True)
    thank_you_link_text = models.CharField(max_length=255)
    thank_you_link = models.TextField(default="", blank=True)
    giving_optional = models.CharField(max_length=255)
    go_to_pdf_link_text = models.CharField(max_length=255)
    hide_donation_popup = models.BooleanField(default=False)

    def __str__(self):
        return 'Donation Popup'

    def save(self, *args, **kwargs):
        if DonationPopup.objects.exists() and not self.pk:
            raise ValidationError('There can be only one donation popup instance')
        return super(DonationPopup, self).save(*args, **kwargs)


class Fundraiser(models.Model):
    color_scheme = models.CharField(max_length=255,
                                             choices=COLOR_SCHEME_CHOICES,
                                             blank=True,
                                             default='')
    message_type = models.CharField(max_length=255,
                                    choices=MESSAGE_TYPE_CHOICES,
                                    blank=True,
                                    default='')
    headline = models.TextField(blank=True, null=True, default="")
    message = models.TextField(blank=True, null=True, default="")
    button_text = models.CharField(max_length=255)
    button_url = models.CharField(max_length=255)
    box_headline = models.TextField(blank=True, null=True, default="")
    box_html = models.TextField(blank=True, null=True, default="")
    fundraiser_image = models.ImageField(null=True, blank=True)
    goal_amount = models.IntegerField(blank=True, null=True)
    goal_time = models.DateTimeField(blank=True, null=True)


CONTEXT_FILTER_CHOICES = (
    ('all', 'All Pages'),
    ('subjects', 'Subjects Pages'),
    ('book_details', 'Book Details Pages'),
    ('blog', 'Blog Pages'),
    ('url_pattern', 'Specific URL Pattern'),
)


class SiteBanner(TranslatableMixin, models.Model):
    name = models.CharField(
        max_length=255,
        help_text="Admin-friendly name (e.g., 'Spring 2026 Campaign A')"
    )

    html_message = models.TextField(
        default='',
        help_text="HTML message to display in banner"
    )
    link_text = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        help_text="Text for the call-to-action link"
    )
    link_url = models.URLField(
        null=True,
        blank=True,
        help_text="URL for the call-to-action link"
    )
    thumbnail = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
        help_text="Optional thumbnail image for banner"
    )

    is_active = models.BooleanField(
        default=True,
        help_text="Enable/disable banner without deleting it"
    )
    start_date = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When to start showing this banner (optional)"
    )
    end_date = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When to stop showing this banner (optional)"
    )

    context_filter = models.CharField(
        max_length=100,
        default='all',
        choices=CONTEXT_FILTER_CHOICES,
        help_text="Where to display this banner"
    )
    url_pattern = models.CharField(
        max_length=500,
        blank=True,
        null=True,
        help_text="URL pattern for 'Specific URL Pattern' context (e.g., '/details/books/anatomy')"
    )

    def get_banner_thumbnail(self):
        return build_image_url(self.thumbnail)

    banner_thumbnail = property(get_banner_thumbnail)

    panels = [
        FieldPanel('name'),
        FieldPanel('is_active'),
        MultiFieldPanel([
            FieldPanel('start_date'),
            FieldPanel('end_date'),
        ], heading='Campaign Schedule'),
        MultiFieldPanel([
            FieldPanel('context_filter'),
            FieldPanel('url_pattern'),
        ], heading='Targeting'),
        MultiFieldPanel([
            FieldPanel('html_message'),
            FieldPanel('link_text'),
            FieldPanel('link_url'),
            FieldPanel('thumbnail'),
        ], heading='Content'),
    ]

    def __str__(self):
        return self.name

    class Meta(TranslatableMixin.Meta):
        verbose_name = 'Site Banner'
        verbose_name_plural = 'Site Banners'
        ordering = ['-start_date']
