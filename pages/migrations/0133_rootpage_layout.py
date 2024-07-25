# Generated by Django 5.0.7 on 2024-07-24 23:47

import wagtail.blocks
import wagtail.documents.blocks
import wagtail.fields
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("pages", "0132_remove_rootpage_layout"),
    ]

    operations = [
        migrations.AddField(
            model_name="rootpage",
            name="layout",
            field=wagtail.fields.StreamField(
                [
                    (
                        "landing",
                        wagtail.blocks.StructBlock(
                            [
                                (
                                    "nav_links",
                                    wagtail.blocks.ListBlock(
                                        wagtail.blocks.StructBlock(
                                            [
                                                ("text", wagtail.blocks.CharBlock(required=True)),
                                                ("aria_label", wagtail.blocks.CharBlock(required=False)),
                                                (
                                                    "target",
                                                    wagtail.blocks.StreamBlock(
                                                        [
                                                            ("external", wagtail.blocks.URLBlock(required=False)),
                                                            (
                                                                "internal",
                                                                wagtail.blocks.PageChooserBlock(required=False),
                                                            ),
                                                            (
                                                                "document",
                                                                wagtail.documents.blocks.DocumentChooserBlock(
                                                                    required=False
                                                                ),
                                                            ),
                                                        ],
                                                        required=True,
                                                    ),
                                                ),
                                            ],
                                            label="Link",
                                            required=False,
                                        ),
                                        default=[],
                                        label="Nav Links",
                                        max_num=1,
                                    ),
                                )
                            ]
                        ),
                    )
                ],
                default=[],
                use_json_field=True,
            ),
        ),
    ]