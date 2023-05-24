from django.db import models
from wagtail import blocks
from wagtail.fields import RichTextField, StreamField
from wagtail.api import APIField


class MenuItemBlock(blocks.StructBlock):
    label = blocks.CharBlock(max_length=255)
    partial_url = blocks.CharBlock(max_length=255)

class MenuBlock(blocks.StructBlock):
    menu_name = blocks.CharBlock(max_length=255)
    ('menu_items', blocks.ListBlock(blocks.StructBlock([
        ('items', MenuItemBlock()),
    ])))

class Menus(models.Model):
    menu = StreamField(
        blocks.StreamBlock([
            ('menu_structure', blocks.ListBlock(blocks.StructBlock([
                ('menu', MenuBlock()),
            ])))]), use_json_field=True)