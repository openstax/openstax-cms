from django.db import models
from wagtail import blocks
from wagtail.fields import StreamField
from wagtail.admin.panels import FieldPanel
from wagtail.api import APIField


class MenuItemBlock(blocks.StructBlock):
    label = blocks.CharBlock(max_length=255,
        help_text='Text shown for this item in the nav, e.g. "About Us" or "For K12 Teachers".')
    partial_url = blocks.CharBlock(max_length=255,
        help_text='Where the item links. Usually a path on openstax.org, e.g. "/about" or '
                  '"/subjects/math". Use a full "https://..." URL only for external links.')
    key = blocks.CharBlock(max_length=255, required=False,
        help_text='Stable identifier for targeting/experiments; survives label changes. '
                  'Lowercase + hyphens, e.g. "about-us-link".')
    feature_flag = blocks.CharBlock(max_length=255, required=False,
        help_text='PostHog flag key that gates this item, e.g. "nav-k12-item". '
                  'Leave blank to always show.')
    flag_value = blocks.CharBlock(max_length=255, required=False,
        help_text='Show this item only when the flag equals this value, e.g. "variant-b". '
                  'Blank = show whenever the flag is on.')


class MenuBlock(blocks.StructBlock):
    name = blocks.CharBlock(max_length=255, required=False,
        help_text='Optional heading for this group of items within the dropdown, '
                  'e.g. "By Subject". Leave blank for an ungrouped list.')
    menu_items = blocks.ListBlock(MenuItemBlock(required=True))


class Menus(models.Model):
    name = models.CharField(max_length=255,
        help_text='Top-level nav label, e.g. "What we do" or "Subjects".')
    sort_order = models.IntegerField(default=0,
        help_text='Controls the order menus appear in the nav (lowest first), e.g. 10, 20, 30. '
                  'Leaving gaps makes it easy to insert a menu later without renumbering.')
    key = models.CharField(max_length=255, blank=True, default='',
        help_text='Stable identifier for this dropdown; survives name changes, '
                  'e.g. "subjects-dropdown".')
    feature_flag = models.CharField(max_length=255, blank=True, default='',
        help_text='PostHog flag key that gates this whole dropdown, e.g. "nav-new-subjects". '
                  'Blank = always show.')
    flag_value = models.CharField(max_length=255, blank=True, default='',
        help_text='Show only when the flag equals this value, e.g. "variant-b". '
                  'Blank = show whenever the flag is on.')
    partial_url = models.CharField(max_length=255, blank=True, default='',
        help_text='If set, this menu renders as a single top-level link (not a dropdown), '
                  'e.g. "/k12". Leave blank for a dropdown with items below.')
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
        ordering = ['sort_order']

    panels = [
        FieldPanel('name'),
        FieldPanel('sort_order'),
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
