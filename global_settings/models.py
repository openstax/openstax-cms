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
        help_text='Social links shown in the footer, in order. Add, remove and reorder '
                  'them here; the frontend maps each platform to its icon.')

    panels = [
        FieldPanel('supporters'),
        FieldPanel('copyright'),
        FieldPanel('ap_statement'),
        FieldPanel('social_links'),
        MultiFieldPanel(
            [
                FieldPanel('facebook_link'),
                FieldPanel('twitter_link'),
                FieldPanel('linkedin_link'),
            ],
            heading='Legacy social links (do not edit)',
            classname='collapsed',
            help_text='Only read by a frontend released before Social links existed. '
                      'Kept so a cached response cannot leave the footer without icons, '
                      'and removable once that release is out.',
        ),
    ]

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
    default_give_link = models.URLField(
        "Default give link",
        blank=True,
        help_text="Used by the header Give button outside the Give Today campaign window. The "
                  "campaign link above takes over between the menu start and menu expiry dates."
    )
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
