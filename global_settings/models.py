from django.db import models
from wagtail.contrib.settings.models import BaseSetting, register_setting


@register_setting(icon='doc-empty')
class StickyNote(BaseSetting):
    start = models.DateTimeField(null=True, help_text="Set the start date to override the content of the Give Sticky. Set the header and body below to change.")
    expires = models.DateTimeField(null=True, help_text="Set the date to expire overriding the content of the Give Sticky.")
    header = models.TextField(max_length=255)
    body = models.TextField()
    link_text = models.CharField(max_length=255)
    link = models.URLField()
    emergency_expires = models.DateTimeField(null=True, blank=True, help_text="When active, the Sticky Note will not be displayed until the emergency expires.")
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

@register_setting(icon='cogs')
class CloudfrontDistribution(BaseSetting):
    distribution_id = models.CharField(max_length=255, null=True, blank=True)

    class Meta:
        verbose_name = 'CloudFront Distribution'