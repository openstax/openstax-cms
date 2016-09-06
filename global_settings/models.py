from django.db import models
from wagtail.contrib.settings.models import BaseSetting, register_setting


@register_setting(icon='doc-empty')
class StickyNote(BaseSetting):
    show_sticky = models.BooleanField(default=False)
    sticky_content = models.TextField()
    give_sticky_expires = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = 'Sticky Note'
