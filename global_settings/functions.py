import logging
import uuid

import boto3
from botocore.exceptions import NoCredentialsError, ClientError
from django.db import transaction
from django.utils import timezone

from .models import CloudfrontDistribution

logger = logging.getLogger(__name__)

# Every API prefix a page publish can change. Kept constant so the throttle
# below only needs a dirty flag, not a queue of paths.
PAGE_PUBLISH_PATHS = ['v2/pages', 'spike', 'general', 'books/resources']

# Publishes closer together than this share one invalidation. Repeated
# invalidations of hot paths stampede the origin (each one empties the
# CloudFront cache for every visitor at once).
PAGE_INVALIDATION_WINDOW_SECONDS = 300


def invalidate_cloudfront_caches(paths=None, distribution=None):
    """Create one CloudFront invalidation covering the given API prefix(es).

    paths: a prefix string, a list of prefixes, or None to invalidate the
    whole API. Returns True if the invalidation was created.
    """
    if distribution is None:
        distribution = CloudfrontDistribution.objects.first()
    if distribution is None or not distribution.distribution_id:
        return False
    if paths is None:
        items = ['/apps/cms/api/*']
    else:
        if isinstance(paths, str):
            paths = [paths]
        items = ['/apps/cms/api/{}*'.format(path) for path in paths]
    try:
        client = boto3.client('cloudfront')
        client.create_invalidation(
            DistributionId=distribution.distribution_id,
            InvalidationBatch={
                'Paths': {
                    'Quantity': len(items),
                    'Items': items,
                },
                # Must be unique per call: CloudFront rejects a reused
                # reference with a different path batch.
                'CallerReference': str(uuid.uuid4()),
            }
        )
        return True
    except NoCredentialsError:
        logger.warning('No AWS credentials set - unable to invalidate cache')
    except ClientError:
        logger.exception('CloudFront invalidation failed for %s', items)
    return False


def request_page_invalidation():
    """Throttled invalidation of the page-serving API paths.

    The first publish invalidates immediately; publishes within
    PAGE_INVALIDATION_WINDOW_SECONDS of the last invalidation only mark the
    distribution dirty, and the flush_cloudfront_invalidations cron sends the
    trailing invalidation.
    """
    with transaction.atomic():
        distribution = CloudfrontDistribution.objects.select_for_update().first()
        if distribution is None or not distribution.distribution_id:
            return
        now = timezone.now()
        last = distribution.last_invalidated_at
        if last and (now - last).total_seconds() < PAGE_INVALIDATION_WINDOW_SECONDS:
            if not distribution.invalidation_pending:
                distribution.invalidation_pending = True
                distribution.save(update_fields=['invalidation_pending'])
            return
        # Claim the slot before the network call so the row lock is held only
        # for DB work; concurrent publishers see the fresh timestamp and just
        # mark pending.
        _claim(distribution, now)
    _send_page_invalidation(distribution)


def flush_pending_page_invalidation():
    """Send the trailing invalidation if any publish was throttled.

    Cron entry point (flush_cloudfront_invalidations); also retries
    invalidations that failed at publish time.
    """
    with transaction.atomic():
        distribution = CloudfrontDistribution.objects.select_for_update().first()
        if distribution is None or not distribution.distribution_id \
                or not distribution.invalidation_pending:
            return
        _claim(distribution, timezone.now())
    _send_page_invalidation(distribution)


def _claim(distribution, now):
    distribution.invalidation_pending = False
    distribution.last_invalidated_at = now
    distribution.save(update_fields=['invalidation_pending', 'last_invalidated_at'])


def _send_page_invalidation(distribution):
    if not invalidate_cloudfront_caches(PAGE_PUBLISH_PATHS, distribution=distribution):
        # Re-flag so the cron retries the failed invalidation.
        CloudfrontDistribution.objects.filter(pk=distribution.pk).update(invalidation_pending=True)
