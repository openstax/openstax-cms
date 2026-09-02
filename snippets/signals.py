from django.db.models.signals import post_save
from django.dispatch import receiver

from global_settings.functions import invalidate_cloudfront_caches, request_page_invalidation
from snippets.models import ContentWarning, FacultyResource, StudentResource, Subject, Role, ErrataContent, \
    SubjectCategory, BlogContentType, BlogCollection, \
    WebinarCollection, AmazonBookBlurb, PromoteSnippet


@receiver(post_save, sender=Subject)
def clear_cloudfront_on_subject_save(sender, **kwargs):
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


@receiver(post_save, sender=BlogContentType)
def clear_cloudfront_on_blog_content_type_save(sender, **kwargs):
    invalidate_cloudfront_caches('snippets/blogcontenttype')


@receiver(post_save, sender=BlogCollection)
def clear_cloudfront_on_blog_collection_save(sender, **kwargs):
    invalidate_cloudfront_caches('snippets/blogcollection')


@receiver(post_save, sender=WebinarCollection)
def clear_cloudfront_on_webinar_collection_save(sender, **kwargs):
    invalidate_cloudfront_caches('snippets/webinarcollection')

@receiver(post_save, sender=PromoteSnippet)
def clear_cloudfront_on_assignable_available_save(sender, **kwargs):
    invalidate_cloudfront_caches('snippets/promotesnippet')

@receiver(post_save, sender=AmazonBookBlurb)
def clear_cloudfront_on_amazon_book_blurb_save(sender, **kwargs):
    invalidate_cloudfront_caches('snippets/amazonbookblurb')

@receiver(post_save, sender=ContentWarning)
def clear_cloudfront_on_content_warning_save(sender, **kwargs):
    invalidate_cloudfront_caches('snippets/contentwarning')


# Resource snippets surface inside book page payloads and the book-resources
# table source, not just a snippets endpoint, so invalidate the page paths.
@receiver(post_save, sender=FacultyResource)
def clear_cloudfront_on_faculty_resource_save(sender, **kwargs):
    request_page_invalidation()


@receiver(post_save, sender=StudentResource)
def clear_cloudfront_on_student_resource_save(sender, **kwargs):
    request_page_invalidation()
