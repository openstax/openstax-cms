from django.db.models.signals import post_save
from django.dispatch import receiver

from global_settings.functions import invalidate_cloudfront_caches
from .models import Webinar


@receiver(post_save, sender=Webinar)
def clear_cloudfront_on_webinar_save(sender, **kwargs):
    invalidate_cloudfront_caches('webinars')
