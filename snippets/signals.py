from django.db.models.signals import post_save
from django.dispatch import receiver

from global_settings.functions import invalidate_cloudfront_caches
from snippets.models import Subject, Role, ErrataContent, SubjectCategory, GiveBanner, BlogContentType, BlogCollection


@receiver(post_save, sender=Subject)
def clear_cloudfront_on_subject_save(sender, **kwargs):
    print('subjects cache cleared')
    invalidate_cloudfront_caches('snippets/subjects')


@receiver(post_save, sender=Role)
def clear_cloudfront_on_role_save(sender, **kwargs):
    invalidate_cloudfront_caches('snippets/roles')


@receiver(post_save, sender=ErrataContent)
def clear_cloudfront_on_errata_content_save(sender, **kwargs):
    invalidate_cloudfront_caches('snippets/erratacontent')


@receiver(post_save, sender=SubjectCategory)
def clear_cloudfront_on_subject_category_save(sender, **kwargs):
    invalidate_cloudfront_caches('snippets/subjectcategory')


@receiver(post_save, sender=GiveBanner)
def clear_cloudfront_on_give_banner_save(sender, **kwargs):
    invalidate_cloudfront_caches('snippets/givebanner')


@receiver(post_save, sender=BlogContentType)
def clear_cloudfront_on_blog_content_type_save(sender, **kwargs):
    invalidate_cloudfront_caches('snippets/blogcontenttype')


@receiver(post_save, sender=BlogCollection)
def clear_cloudfront_on_blog_collection_save(sender, **kwargs):
    invalidate_cloudfront_caches('snippets/blogcollection')
