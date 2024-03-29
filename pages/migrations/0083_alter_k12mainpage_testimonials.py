# Generated by Django 4.2.8 on 2024-01-03 22:26

from django.db import migrations
import pages.custom_blocks
import wagtail.blocks
import wagtail.fields


class Migration(migrations.Migration):
    dependencies = [
        ("pages", "0082_remove_webinarpage_description_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="k12mainpage",
            name="testimonials",
            field=wagtail.fields.StreamField(
                [
                    (
                        "testimonials",
                        wagtail.blocks.StructBlock(
                            [
                                ("author_icon", pages.custom_blocks.APIImageChooserBlock(required=False)),
                                ("author_name", wagtail.blocks.CharBlock(required=True)),
                                ("author_title", wagtail.blocks.CharBlock(required=True)),
                                ("testimonial", wagtail.blocks.RichTextBlock(required=True)),
                            ]
                        ),
                    )
                ],
                use_json_field=True,
            ),
        ),
    ]
