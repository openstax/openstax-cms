from django.db import models

class ThankYouNote(models.Model):
    thank_you_note = models.TextField(default="", blank=True)
    first_name = models.CharField(max_length=255, default="", blank=True)
    last_name = models.CharField(max_length=255, default="", blank=True)
    institution = models.CharField(max_length=255, default="", blank=True)
    created = models.DateField(auto_now_add=True)

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
