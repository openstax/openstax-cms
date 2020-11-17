from django.db.models.signals import post_save
from django.dispatch import receiver

from wagtail.core.signals import page_published

from .functions import invalidate_cloudfront_caches
from .models import StickyNote, Footer, GiveToday

def clear_cloudfront_on_page_publish(sender, **kwargs):
    invalidate_cloudfront_caches()
page_published.connect(clear_cloudfront_on_page_publish)

# These functions clear caches on non-page models that drive content on the website
@receiver(post_save, sender=StickyNote)
def clear_cloudfront_on_sticky_save(sender, **kwargs):
    invalidate_cloudfront_caches()

@receiver(post_save, sender=Footer)
def clear_cloudfront_on_footer_save(sender, **kwargs):
    invalidate_cloudfront_caches()

@receiver(post_save, sender=GiveToday)
def clear_cloudfront_on_give_save(sender, **kwargs):
    invalidate_cloudfront_caches()

