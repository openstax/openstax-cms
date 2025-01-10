from django.db import models
from django.core.exceptions import ValidationError

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


