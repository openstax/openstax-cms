from django.db.models.signals import post_save
from django.dispatch import receiver

from global_settings.functions import invalidate_cloudfront_caches
from salesforce.models import Partner

@receiver(post_save, sender=Partner)
def clear_cloudfront_on_partner_save(sender, instance, **kwargs):
    # only invalidate if from admin
    if getattr(instance, 'from_admin_site', False):
        invalidate_cloudfront_caches('salesforce/partners')