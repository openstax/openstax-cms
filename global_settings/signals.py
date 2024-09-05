from django.db.models.signals import post_save
from django.dispatch import receiver

from wagtail.signals import page_published

from .functions import invalidate_cloudfront_caches
from .models import StickyNote, Footer, GiveToday


def clear_cloudfront_on_page_publish(sender, **kwargs):
    invalidate_cloudfront_caches('v2/pages')
    # clear general pages
    invalidate_cloudfront_caches('spike')
    invalidate_cloudfront_caches('general')
    # clear resources
    invalidate_cloudfront_caches('books/resources')


page_published.connect(clear_cloudfront_on_page_publish)


# These functions clear caches on non-page models that drive content on the website
@receiver(post_save, sender=StickyNote)
def clear_cloudfront_on_sticky_save(sender, **kwargs):
    invalidate_cloudfront_caches('sticky')
    # this should not be needed, but we had an issue with it not clearing
    invalidate_cloudfront_caches('sticky/')


@receiver(post_save, sender=Footer)
def clear_cloudfront_on_footer_save(sender, **kwargs):
    invalidate_cloudfront_caches('footer')


@receiver(post_save, sender=GiveToday)
def clear_cloudfront_on_give_save(sender, **kwargs):
    invalidate_cloudfront_caches('give-today')

