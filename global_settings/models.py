from django.db import models
from wagtail.contrib.settings.models import BaseSetting, register_setting


@register_setting
class GiveStickySetting(BaseSetting):
    show_give_sticky = models.BooleanField()
    give_sticky_expires = models.DateTimeField(null=True, blank=True)
