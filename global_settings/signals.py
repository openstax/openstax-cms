from wagtail.core.signals import page_published
from .functions import invalidate_cloudfront_caches

def clear_cloudfront_on_page_publish(sender, **kwargs):
    invalidate_cloudfront_caches()

# Register a receiver
page_published.connect(clear_cloudfront_on_page_publish)
