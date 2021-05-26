from django.db import models

class ThankYouNote(models.Model):
    thank_you_note = models.TextField(null=True, blank=True)
    user_info = models.TextField(null=True, blank=True)
    created = models.DateField(auto_now_add=True)

class DonationPopup(models.Model):
    download_image = models.ImageField(null=True, blank=True)
    download_ready = models.TextField(null=True, blank=True)
    header_image = models.ImageField(null=True, blank=True)
    header_title = models.TextField(null=True, blank=True)
    header_subtitle = models.TextField(null=True, blank=True)
    give_link_text = models.CharField(max_length=255)
    give_link = models.TextField(null=True, blank=True)
    thank_you_link_text = models.CharField(max_length=255)
    thank_you_link = models.TextField(null=True, blank=True)
    giving_optional = models.CharField(max_length=255)
    go_to_pdf_link_text = models.CharField(max_length=255)
    hide_donation_popup = models.BooleanField(default=False)
