from django.db.models.signals import post_save
from django.dispatch import receiver

from global_settings.functions import invalidate_cloudfront_caches
from .models import Menus


@receiver(post_save, sender=Menus)
def clear_cloudfront_on_oxmenus_save(sender, **kwargs):
    invalidate_cloudfront_caches('oxmenus')