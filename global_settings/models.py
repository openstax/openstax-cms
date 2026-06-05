from django.db import models
from wagtail.admin.panels import FieldPanel, MultiFieldPanel
from wagtail.contrib.settings.models import BaseSiteSetting, register_setting


@register_setting(icon='warning')
class EmergencyMessaging(BaseSiteSetting):
    emergency_expires = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When active, displays emergency banner instead of regular banners"
    )
    emergency_content = models.CharField(
        max_length=500,
        blank=True,
        help_text="Emergency message to display"
    )

    panels = [
        MultiFieldPanel([
            FieldPanel('emergency_expires'),
            FieldPanel('emergency_content'),
        ], heading='Emergency Override'),
    ]

    class Meta:
        verbose_name = 'Emergency Messaging'


@register_setting(icon='collapse-down')
class Footer(BaseSiteSetting):
    supporters = models.TextField()
    copyright = models.TextField()
    ap_statement = models.TextField()
    facebook_link =models.URLField()
    twitter_link = models.URLField()
    linkedin_link = models.URLField()

    class Meta:
        verbose_name = 'Footer'

@register_setting(icon='cogs')
class CloudfrontDistribution(BaseSiteSetting):
    distribution_id = models.CharField(max_length=255, null=True, blank=True)

    class Meta:
        verbose_name = 'CloudFront Distribution'


class GiveToday(BaseSiteSetting):
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
