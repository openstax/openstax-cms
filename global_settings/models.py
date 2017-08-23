from django.db import models
from wagtail.contrib.settings.models import BaseSetting, register_setting


@register_setting(icon='doc-empty')
class StickyNote(BaseSetting):
    show = models.BooleanField(default=False)
    expires = models.DateTimeField(null=True, blank=True)
    content = models.CharField(max_length=255)
    emergency_expires = models.DateTimeField(null=True, blank=True)
    emergency_content = models.CharField(max_length=255)

    class Meta:
        verbose_name = 'Sticky Note'


@register_setting(icon='collapse-down')
class Footer(BaseSetting):
    supporters = models.TextField()
    copyright = models.TextField()
    ap_statement = models.TextField()
    facebook_link =models.URLField()
    twitter_link = models.URLField()
    linkedin_link = models.URLField()

    class Meta:
        verbose_name = 'Footer'
