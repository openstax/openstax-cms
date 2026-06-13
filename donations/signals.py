from django.db.models.signals import post_save
from django.dispatch import receiver

from global_settings.functions import invalidate_cloudfront_caches
from shared.analytics import capture as posthog_capture
from .models import DonationPopup, Fundraiser, SiteBanner, ThankYouNote


@receiver(post_save, sender=DonationPopup)
def clear_cloudfront_on_donation_popup_save(sender, **kwargs):
    invalidate_cloudfront_caches('donations/donation-popup')


@receiver(post_save, sender=Fundraiser)
def clear_cloudfront_on_fundraiser_save(sender, **kwargs):
    invalidate_cloudfront_caches('donations/fundraiser')


@receiver(post_save, sender=SiteBanner)
def clear_cloudfront_on_site_banner_save(sender, **kwargs):
    invalidate_cloudfront_caches('donations/sitebanner')


@receiver(post_save, sender=ThankYouNote)
def capture_thank_you_note(sender, instance, created, **kwargs):
    if not created:
        return
    posthog_capture(
        'thank_you_note_submitted',
        properties={'form_type': 'donation_thank_you'},
    )
