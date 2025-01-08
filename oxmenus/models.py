from django.db import models
from wagtail import blocks
from wagtail.fields import StreamField
from wagtail.admin.panels import FieldPanel
from wagtail.api import APIField


class MenuItemBlock(blocks.StructBlock):
    label = blocks.CharBlock(max_length=255)
    partial_url = blocks.CharBlock(max_length=255)


class MenuBlock(blocks.StructBlock):
    name = models.CharField(max_length=255)
    menu_items = blocks.ListBlock(MenuItemBlock(required=True))


class Menus(models.Model):
    name = models.CharField(max_length=255)
    menu = StreamField(
        blocks.StreamBlock([
            ('menu_block', MenuBlock(required=True))
            ]), use_json_field=True)

    def menu_block_json(self):
        prep_value = self.menu.get_prep_value()
        menu_json = []
        for m in prep_value:
            for x in m['value']['menu_items']:
                label = x['value']['label']
                partial_url = x['value']['partial_url']
                menu_json.append({"label": str(label), "partial_url": str(partial_url)})
        return menu_json

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Menu"
        verbose_name_plural = "Menus"

    panels = [
        FieldPanel('name'),
        FieldPanel('menu')
    ]

    api_fields = [
        APIField('name'),
        APIField('menu')
    ]
