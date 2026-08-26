from django.core.management.base import BaseCommand

from global_settings.functions import flush_pending_page_invalidation


class Command(BaseCommand):
    help = 'Send any CloudFront invalidation deferred by the page-publish throttle'

    def handle(self, *args, **options):
        flush_pending_page_invalidation()
