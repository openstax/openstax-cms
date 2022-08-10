from django.db.models.signals import post_save
from django.dispatch import receiver

from global_settings.functions import invalidate_cloudfront_caches
from .models import FeatureFlag, WebviewSettings


@receiver(post_save, sender=FeatureFlag)
def clear_cloudfront_on_feature_flag_save(sender, **kwargs):
    invalidate_cloudfront_caches('flags')


@receiver(post_save, sender=WebviewSettings)
def clear_cloudfront_on_webview_settings_save(sender, **kwargs):
    invalidate_cloudfront_caches('webview-settings')
