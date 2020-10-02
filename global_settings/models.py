from django.db import models
from wagtail.contrib.settings.models import BaseSetting, register_setting


@register_setting(icon='doc-empty')
class StickyNote(BaseSetting):
    start = models.DateTimeField(null=True, help_text="Set the start date to override the content of the Give Sticky. Set the header and body below to change.")
    expires = models.DateTimeField(null=True, help_text="Set the date to expire overriding the content of the Give Sticky.")
    show_popup = models.BooleanField(default=False, help_text="Replaces the top banner with a popup, start and expire dates still control timing.")
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


@register_setting(icon='date')
class GiveToday(BaseSetting):
    give_link_text = models.CharField(max_length=255)
    give_link = models.URLField("Give link", blank=True, help_text="URL to Rice Give page or something similar")
    start = models.DateTimeField(null=True,
                                 help_text="Set the start date for Give Today to display")
    expires = models.DateTimeField(null=True,
                                   help_text="Set the date to expire displaying Give Today")
    menu_start = models.DateTimeField(null=True,
                                 help_text="Set the start date for Give Today to display in the menu")
    menu_expires = models.DateTimeField(null=True,
                                   help_text="Set the date to expire displaying Give Today in the menu")

    class Meta:
        verbose_name = 'Give Today'
