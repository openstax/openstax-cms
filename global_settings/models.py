from django.db import models
from wagtail.contrib.settings.models import BaseSetting, register_setting


@register_setting(icon='doc-empty')
class StickyNote(BaseSetting):
    show = models.BooleanField(default=False)
    expires = models.DateTimeField(null=True, blank=True)
    content = models.CharField(max_length=255)

    class Meta:
        verbose_name = 'Sticky Note'
