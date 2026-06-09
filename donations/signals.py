from django.db.models.signals import post_save
from django.dispatch import receiver

from global_settings.functions import invalidate_cloudfront_caches
from .models import DonationPopup, Fundraiser, SiteBanner


@receiver(post_save, sender=DonationPopup)
def clear_cloudfront_on_donation_popup_save(sender, **kwargs):
    invalidate_cloudfront_caches('donations/donation-popup')


@receiver(post_save, sender=Fundraiser)
def clear_cloudfront_on_fundraiser_save(sender, **kwargs):
    invalidate_cloudfront_caches('donations/fundraiser')


@receiver(post_save, sender=SiteBanner)
def clear_cloudfront_on_site_banner_save(sender, **kwargs):
    invalidate_cloudfront_caches('donations/sitebanner')
