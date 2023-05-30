from django.db import models
from wagtail import blocks
from wagtail.fields import RichTextField, StreamField
from wagtail.admin.edit_handlers import FieldPanel
from wagtail.api import APIField


class MenuItemBlock(blocks.StructBlock):
    label = blocks.CharBlock(max_length=255)
    partial_url = blocks.CharBlock(max_length=255)


class Menus(models.Model):
    name = models.CharField(max_length=255)
    menu = StreamField(
        blocks.StreamBlock([
            ('content', blocks.ListBlock(blocks.StructBlock([
                ('menu_name', blocks.CharBlock(max_length=255)),
                ('menu_items', blocks.ListBlock(MenuItemBlock(required=True)))
                 ])))
            ]), use_json_field=True)

    def __str__(self):
        return self.name

    content_panels = [
        FieldPanel('name'),
        FieldPanel('menu')
    ]

    api_fields = [
        APIField('name'),
        APIField('menu')
    ]