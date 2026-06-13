from django.db import models
from wagtail import blocks
from wagtail.fields import StreamField
from wagtail.admin.panels import FieldPanel
from wagtail.api import APIField


class MenuItemBlock(blocks.StructBlock):
    label = blocks.CharBlock(max_length=255)
    partial_url = blocks.CharBlock(max_length=255)
    key = blocks.CharBlock(max_length=255, required=False,
        help_text="Stable identifier for targeting/experiments; survives label changes.")
    feature_flag = blocks.CharBlock(max_length=255, required=False,
        help_text="PostHog flag key that gates this item. Leave blank to always show.")
    flag_value = blocks.CharBlock(max_length=255, required=False,
        help_text="Show only when the flag equals this value. Blank = show when the flag is on.")


class MenuBlock(blocks.StructBlock):
    name = models.CharField(max_length=255)
    menu_items = blocks.ListBlock(MenuItemBlock(required=True))


class Menus(models.Model):
    name = models.CharField(max_length=255)
    key = models.CharField(max_length=255, blank=True, default='',
        help_text="Stable identifier for this dropdown; survives name changes.")
    feature_flag = models.CharField(max_length=255, blank=True, default='',
        help_text="PostHog flag key that gates this whole dropdown. Blank = always show.")
    flag_value = models.CharField(max_length=255, blank=True, default='',
        help_text="Show only when the flag equals this value. Blank = show when the flag is on.")
    partial_url = models.CharField(max_length=255, blank=True, default='',
        help_text="If set, this menu renders as a single top-level link (not a dropdown).")
    menu = StreamField(
        blocks.StreamBlock([
            ('menu_block', MenuBlock(required=True))
            ]), use_json_field=True)

    def menu_block_json(self):
        prep_value = self.menu.get_prep_value()
        menu_json = []
        for m in prep_value:
            for x in m['value']['menu_items']:
                v = x['value']
                menu_json.append({
                    "label": str(v['label']),
                    "partial_url": str(v['partial_url']),
                    "key": str(v.get('key', '')),
                    "feature_flag": str(v.get('feature_flag', '')),
                    "flag_value": str(v.get('flag_value', '')),
                })
        return menu_json

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Menu"
        verbose_name_plural = "Menus"

    panels = [
        FieldPanel('name'),
        FieldPanel('key'),
        FieldPanel('feature_flag'),
        FieldPanel('flag_value'),
        FieldPanel('partial_url'),
        FieldPanel('menu'),
    ]

    api_fields = [
        APIField('name'),
        APIField('key'),
        APIField('feature_flag'),
        APIField('flag_value'),
        APIField('partial_url'),
        APIField('menu'),
    ]
