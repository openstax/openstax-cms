from django.db.models.signals import post_save
from django.dispatch import receiver

from global_settings.functions import invalidate_cloudfront_caches
from .models import DonationPopup

@receiver(post_save, sender=DonationPopup)
def clear_cloudfront_on_donation_popup_save(sender, **kwargs):
    invalidate_cloudfront_caches()
