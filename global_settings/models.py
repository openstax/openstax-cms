from django.db import models
from wagtail import blocks
from wagtail.admin.panels import FieldPanel, MultiFieldPanel
from wagtail.contrib.settings.models import BaseSiteSetting, register_setting
from wagtail.fields import StreamField

SOCIAL_PLATFORM_CHOICES = (
    ('facebook', 'Facebook'),
    ('twitter', 'Twitter/X'),
    ('linkedin', 'LinkedIn'),
    ('instagram', 'Instagram'),
    ('youtube', 'YouTube'),
    ('tiktok', 'TikTok'),
    ('threads', 'Threads'),
    ('bluesky', 'Bluesky'),
    ('mastodon', 'Mastodon'),
)


class SocialLinkBlock(blocks.StructBlock):
    platform = blocks.ChoiceBlock(choices=SOCIAL_PLATFORM_CHOICES,
        help_text='Which platform this link is for. The frontend maps this to an icon.')
    url = blocks.URLBlock(help_text='Full URL to the OpenStax profile/page on this platform.')


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
    social_links = StreamField(
        blocks.StreamBlock([('social_link', SocialLinkBlock())]),
        use_json_field=True, blank=True, default='[]',
        help_text='Social links shown in the footer, in order. facebook_link/twitter_link/'
                  'linkedin_link above are kept for backward compatibility with older '
                  'frontends and are not read once a frontend uses this field.')

    def social_links_json(self):
        return [
            {'platform': str(block.value['platform']), 'url': str(block.value['url'])}
            for block in self.social_links
        ]

    class Meta:
        verbose_name = 'Footer'

@register_setting(icon='cogs')
class CloudfrontDistribution(BaseSiteSetting):
    distribution_id = models.CharField(max_length=255, null=True, blank=True)
    # Throttle state for page-publish invalidations (see global_settings.functions).
    last_invalidated_at = models.DateTimeField(null=True, blank=True, editable=False)
    invalidation_pending = models.BooleanField(default=False, editable=False)

    class Meta:
        verbose_name = 'CloudFront Distribution'


@register_setting(icon='date')
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
