# Generated by Django 5.0.14 on 2025-05-08 05:14

import wagtail.fields
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("pages", "0155_alter_rootpage_layout"),
    ]

    operations = [
        migrations.AlterField(
            model_name="rootpage",
            name="body",
            field=wagtail.fields.StreamField(
                [("hero", 53), ("section", 55), ("divider", 62), ("html", 18)],
                block_lookup={
                    0: ("pages.custom_blocks.APIRichTextBlock", (), {}),
                    1: (
                        "wagtail.blocks.CharBlock",
                        (),
                        {"help_text": "Visible text of the link or button.", "required": True},
                    ),
                    2: (
                        "wagtail.blocks.CharBlock",
                        (),
                        {
                            "help_text": "Accessible label for the link or button. if provided, must begin with the visible text.",
                            "required": False,
                        },
                    ),
                    3: (
                        "wagtail.blocks.URLBlock",
                        (),
                        {"help_text": "External links are full urls that can go anywhere", "required": False},
                    ),
                    4: ("wagtail.blocks.PageChooserBlock", (), {"required": False}),
                    5: ("wagtail.documents.blocks.DocumentChooserBlock", (), {"required": False}),
                    6: (
                        "wagtail.blocks.CharBlock",
                        (),
                        {
                            "help_text": "Anchor links reference the ID of an element on the page, and scroll the page there.",
                            "required": False,
                        },
                    ),
                    7: (
                        "wagtail.blocks.StreamBlock",
                        [[("external", 3), ("internal", 4), ("document", 5), ("anchor", 6)]],
                        {"required": True},
                    ),
                    8: (
                        "wagtail.blocks.ChoiceBlock",
                        [],
                        {
                            "choices": [
                                ("orange", "Orange"),
                                ("white", "White"),
                                ("blue_outline", "Blue Outline"),
                                ("deep_green_outline", "Deep Green Outline"),
                            ],
                            "help_text": "Specifies the button style. Default unspecified, meaning the first button in the block is orange and the second is white.",
                        },
                    ),
                    9: (
                        "wagtail.blocks.StreamBlock",
                        [[("style", 8)]],
                        {"block_counts": {"style": {"max_num": 1}}, "required": False},
                    ),
                    10: (
                        "wagtail.blocks.StructBlock",
                        [[("text", 1), ("aria_label", 2), ("target", 7), ("config", 9)]],
                        {"label": "Link", "required": False},
                    ),
                    11: ("wagtail.blocks.ListBlock", (10,), {"default": [], "label": "Call To Action", "max_num": 1}),
                    12: ("wagtail.blocks.StructBlock", [[("text", 0), ("cta_block", 11)]], {}),
                    13: ("wagtail.blocks.ListBlock", (12,), {}),
                    14: (
                        "wagtail.blocks.IntegerBlock",
                        (),
                        {"help_text": "Sets the width of the individual cards. default 27.", "min_value": 0},
                    ),
                    15: (
                        "wagtail.blocks.ChoiceBlock",
                        [],
                        {
                            "choices": [("rounded", "Rounded"), ("square", "Square")],
                            "help_text": "The border style of the cards. default borderless.",
                        },
                    ),
                    16: (
                        "wagtail.blocks.StreamBlock",
                        [[("card_size", 14), ("card_style", 15)]],
                        {
                            "block_counts": {"card_size": {"max_num": 1}, "card_style": {"max_num": 1}},
                            "required": False,
                        },
                    ),
                    17: ("wagtail.blocks.StructBlock", [[("cards", 13), ("config", 16)]], {"label": "Cards Block"}),
                    18: ("wagtail.blocks.RawHTMLBlock", (), {}),
                    19: (
                        "wagtail.blocks.StructBlock",
                        [[("text", 1), ("aria_label", 2), ("target", 7), ("config", 9)]],
                        {"label": "Button", "required": False},
                    ),
                    20: ("wagtail.blocks.ListBlock", (19,), {"default": [], "label": "Actions", "max_num": 2}),
                    21: (
                        "wagtail.blocks.CharBlock",
                        (),
                        {"help_text": 'Sets the "analytics nav" field for links within this group.', "required": False},
                    ),
                    22: (
                        "wagtail.blocks.StreamBlock",
                        [[("analytics_label", 21)]],
                        {"block_counts": {"analytics_label": {"max_num": 1}}, "required": False},
                    ),
                    23: ("wagtail.blocks.StructBlock", [[("actions", 20), ("config", 22)]], {}),
                    24: (
                        "wagtail.blocks.StructBlock",
                        [[("text", 1), ("aria_label", 2), ("target", 7)]],
                        {"label": "Link", "required": False},
                    ),
                    25: ("wagtail.blocks.ListBlock", (24,), {"default": [], "label": "Links"}),
                    26: (
                        "wagtail.blocks.ChoiceBlock",
                        [],
                        {
                            "choices": [("white", "White"), ("blue", "Blue"), ("deep-green", "Deep Green")],
                            "help_text": "The color of the link buttons. Default white.",
                        },
                    ),
                    27: (
                        "wagtail.blocks.StreamBlock",
                        [[("color", 26), ("analytics_label", 21)]],
                        {
                            "block_counts": {"analytics_label": {"max_num": 1}, "color": {"max_num": 1}},
                            "required": False,
                        },
                    ),
                    28: ("wagtail.blocks.StructBlock", [[("links", 25), ("config", 27)]], {}),
                    29: ("pages.custom_blocks.APIImageChooserBlock", (), {}),
                    30: ("wagtail.blocks.RichTextBlock", (), {"help_text": "The quote content."}),
                    31: (
                        "wagtail.blocks.CharBlock",
                        (),
                        {"help_text": "The name of the person or entity to attribute the quote to."},
                    ),
                    32: (
                        "wagtail.blocks.CharBlock",
                        (),
                        {"help_text": "Additional title or label about the quotee.", "requred": False},
                    ),
                    33: (
                        "wagtail.blocks.StructBlock",
                        [[("image", 29), ("content", 30), ("name", 31), ("title", 32)]],
                        {},
                    ),
                    34: (
                        "wagtail.blocks.RichTextBlock",
                        (),
                        {"help_text": "The visible text of the question (does not collapse).", "required": True},
                    ),
                    35: (
                        "wagtail.blocks.CharBlock",
                        (),
                        {"help_text": "Not visible to user, must be unique in this FAQ.", "required": True},
                    ),
                    36: (
                        "wagtail.blocks.RichTextBlock",
                        (),
                        {
                            "help_text": "The answer to the question, is hidden until the question is expanded.",
                            "required": True,
                        },
                    ),
                    37: (
                        "wagtail.documents.blocks.DocumentChooserBlock",
                        (),
                        {"help_text": "Not sure this does anything.", "required": False},
                    ),
                    38: (
                        "wagtail.blocks.StructBlock",
                        [[("question", 34), ("slug", 35), ("answer", 36), ("document", 37)]],
                        {},
                    ),
                    39: ("wagtail.blocks.StreamBlock", [[("faq", 38)]], {}),
                    40: ("wagtail.blocks.StreamBlock", [[("books", 4)]], {}),
                    41: (
                        "wagtail.blocks.StreamBlock",
                        [
                            [
                                ("cards_block", 17),
                                ("text", 0),
                                ("html", 18),
                                ("cta_block", 23),
                                ("links_group", 28),
                                ("quote", 33),
                                ("faq", 39),
                                ("book_list", 40),
                            ]
                        ],
                        {},
                    ),
                    42: ("pages.custom_blocks.APIImageChooserBlock", (), {"required": False}),
                    43: ("wagtail.blocks.CharBlock", (), {"required": False}),
                    44: (
                        "wagtail.blocks.ChoiceBlock",
                        [],
                        {
                            "choices": [
                                ("left", "Left"),
                                ("right", "Right"),
                                ("top_left", "Top Left"),
                                ("top_right", "Top Right"),
                                ("bottom_left", "Bottom Left"),
                                ("bottom_right", "Bottom Right"),
                            ],
                            "help_text": "Controls if the image is on the left or right side of the content, and if it prefers to be at the top, center, or bottom of the available space.",
                        },
                    ),
                    45: (
                        "wagtail.blocks.RegexBlock",
                        (),
                        {
                            "error_mssages": {"invalid": "not a valid id."},
                            "help_text": "HTML id of this element. not visible to users, but is visible in urls and is used to link to a certain part of the page with an anchor link. eg: cool_section",
                            "regex": "[a-zA-Z0-9\\-_]",
                        },
                    ),
                    46: (
                        "wagtail.blocks.RegexBlock",
                        (),
                        {
                            "error_mssages": {"invalid": "not a valid hex color."},
                            "help_text": "Sets the background color of the section. value must be hex eg: #ff0000. Default grey.",
                            "regex": "#[a-zA-Z0-9]{6}",
                        },
                    ),
                    47: (
                        "wagtail.blocks.IntegerBlock",
                        (),
                        {"help_text": "Creates space above and below this section. default 0.", "min_value": 0},
                    ),
                    48: (
                        "wagtail.blocks.IntegerBlock",
                        (),
                        {"help_text": "Creates space above this section. default 0.", "min_value": 0},
                    ),
                    49: (
                        "wagtail.blocks.IntegerBlock",
                        (),
                        {"help_text": "Creates space below this section. default 0.", "min_value": 0},
                    ),
                    50: (
                        "wagtail.blocks.ChoiceBlock",
                        [],
                        {
                            "choices": [("center", "Center"), ("left", "Left"), ("right", "Right")],
                            "help_text": "Configures text alignment within the container. Default Left.",
                        },
                    ),
                    51: (
                        "wagtail.blocks.CharBlock",
                        (),
                        {
                            "help_text": 'Sets the "analytics nav" field for links within this section.',
                            "required": False,
                        },
                    ),
                    52: (
                        "wagtail.blocks.StreamBlock",
                        [
                            [
                                ("image_alignment", 44),
                                ("id", 45),
                                ("background_color", 46),
                                ("padding", 47),
                                ("padding_top", 48),
                                ("padding_bottom", 49),
                                ("text_alignment", 50),
                                ("analytics_label", 51),
                            ]
                        ],
                        {
                            "block_counts": {
                                "analytics_label": {"max_num": 1},
                                "background_color": {"max_num": 1},
                                "id": {"max_num": 1},
                                "image_alignment": {"max_num": 1},
                                "padding": {"max_num": 1},
                                "padding_bottom": {"max_num": 1},
                                "padding_top": {"max_num": 1},
                                "text_alignment": {"max_num": 1},
                            },
                            "required": False,
                        },
                    ),
                    53: (
                        "wagtail.blocks.StructBlock",
                        [[("content", 41), ("image", 42), ("image_alt", 43), ("config", 52)]],
                        {},
                    ),
                    54: (
                        "wagtail.blocks.StreamBlock",
                        [
                            [
                                ("id", 45),
                                ("background_color", 46),
                                ("padding", 47),
                                ("padding_top", 48),
                                ("padding_bottom", 49),
                                ("text_alignment", 50),
                                ("analytics_label", 51),
                            ]
                        ],
                        {
                            "block_counts": {
                                "analytics_label": {"max_num": 1},
                                "background_color": {"max_num": 1},
                                "id": {"max_num": 1},
                                "padding": {"max_num": 1},
                                "padding_bottom": {"max_num": 1},
                                "padding_top": {"max_num": 1},
                                "text_alignment": {"max_num": 1},
                            },
                            "required": False,
                        },
                    ),
                    55: ("wagtail.blocks.StructBlock", [[("content", 41), ("config", 54)]], {}),
                    56: (
                        "wagtail.blocks.ChoiceBlock",
                        [],
                        {
                            "choices": [
                                ("center", "Center"),
                                ("content_left", "Left side of content."),
                                ("content_right", "Right side of content."),
                                ("body_left", "Left side of window."),
                                ("body_right", "Right side of window."),
                            ],
                            "help_text": 'Sets the horizontal alignment of the image. can be further customized with the "Offset..." configurations. Default is Left side of window.',
                        },
                    ),
                    57: (
                        "wagtail.blocks.RegexBlock",
                        (),
                        {
                            "error_mssages": {"invalid": "not a valid size."},
                            "help_text": "Specifies the width of the image. Percentages are relative to the container (body or content, depending on alignment option). Must be valid css measurement. eg: 30px, 50%, 10rem. Default is the size of the image.",
                            "regex": "^[0-9]+(px|%|rem)$",
                            "required": False,
                        },
                    ),
                    58: (
                        "wagtail.blocks.RegexBlock",
                        (),
                        {
                            "error_mssages": {"invalid": "not a valid size."},
                            "help_text": "Specifies the height of the image. Percentages are relative to the container (body or content, depending on alignment option). Must be valid css measurement. eg: 30px, 50%, 10rem. Default is the size of the image.",
                            "regex": "^[0-9]+(px|%|rem)$",
                            "required": False,
                        },
                    ),
                    59: (
                        "wagtail.blocks.RegexBlock",
                        (),
                        {
                            "error_mssages": {"invalid": "not a valid size."},
                            "help_text": "Moves the image up or down. Percentages are relative to the image size. Must be valid css measurement. eg: 30px, 50%, 10rem. Default is -50%, which moves the image up by half its width (centering it vertically on the divider).",
                            "regex": "^\\-?[0-9]+(px|%|rem)$",
                            "required": False,
                        },
                    ),
                    60: (
                        "wagtail.blocks.RegexBlock",
                        (),
                        {
                            "error_mssages": {"invalid": "not a valid size."},
                            "help_text": "Moves the image left or right. Percentages are relative to the image size. Must be valid css measurement. eg: 30px, 50%, 10rem. Default is no offset, which means the image's outer edge will align with the container's edge for left and right alignment. or it'll be perfectly centered for centered alignment.",
                            "regex": "^\\-?[0-9]+(px|%|rem)$",
                            "required": False,
                        },
                    ),
                    61: (
                        "wagtail.blocks.StreamBlock",
                        [
                            [
                                ("alignment", 56),
                                ("width", 57),
                                ("height", 58),
                                ("offset_vertical", 59),
                                ("offset_horizontal", 60),
                            ]
                        ],
                        {
                            "block_counts": {
                                "alignment": {"max_num": 1},
                                "height": {"max_num": 1},
                                "offset_horizontal": {"max_num": 1},
                                "offset_vertical": {"max_num": 1},
                                "width": {"max_num": 1},
                            },
                            "required": False,
                        },
                    ),
                    62: ("wagtail.blocks.StructBlock", [[("image", 29), ("config", 61)]], {}),
                },
            ),
        ),
    ]
