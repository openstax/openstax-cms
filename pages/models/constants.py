from wagtail import blocks



from pages.custom_blocks import APIImageChooserBlock, \
    FAQBlock, \
    DividerBlock, \
    APIRichTextBlock, \
    CTAButtonBarBlock, \
    LinksGroupBlock, \
    QuoteBlock, \
    CTALinkBlock, \
    BookBlock, \
    CARDS_STYLE_CHOICES, \
    TEXT_ALIGNMENT_CHOICES, \
    FLEX_CHOICES, \
    hex_color_block, \
    gradient_config_options, \
    gradient_block_counts, \
    id_config_block



# Constants for styling options on Root/Flex pages
HERO_IMAGE_ALIGNMENT_CHOICES = [
    ('left', 'Left'),
    ('right', 'Right'),
    ('top_left', 'Top Left'),
    ('top_right', 'Top Right'),
    ('bottom_left', 'Bottom Left'),
    ('bottom_right', 'Bottom Right'),
]

# Layer 1: Flat content blocks (no containers)
BASE_CONTENT_BLOCKS = [
    ('cards_block', blocks.StructBlock([
        ('cards', blocks.ListBlock(
            blocks.StructBlock([
                ('text', APIRichTextBlock()),
                ('cta_block', blocks.ListBlock(CTALinkBlock(required=False, label="Link"),
                    default=[],
                    max_num=1,
                    label='Call To Action'
                )),
            ]),
        )),
        ('config', blocks.StreamBlock([
            ('card_size', blocks.IntegerBlock(min_value=0, help_text='Sets the width of the individual cards. default 27.')),
            ('card_style', blocks.ChoiceBlock(choices=CARDS_STYLE_CHOICES, help_text='The border style of the cards. default borderless.')),
            ('card_columns', blocks.IntegerBlock(min_value=1, max_value=6, help_text='Number of columns for the cards grid. default auto.')),
            ('accent_colors', blocks.ListBlock(
                hex_color_block('Accent color for a card. Must be hex eg: #ff0000.'),
                default=[], label='Accent Colors',
            )),
            ('divider_colors', blocks.ListBlock(
                hex_color_block('Divider color between cards. Must be hex eg: #ff0000.'),
                default=[], label='Divider Colors',
            )),
            ('background_color', hex_color_block('Background color for the cards block. Must be hex eg: #ff0000.')),
            ('border_size', blocks.IntegerBlock(min_value=0, help_text='Border size in pixels for the cards. default 0.')),
        ], block_counts={
            'card_size': {'max_num': 1},
            'card_style': {'max_num': 1},
            'card_columns': {'max_num': 1},
            'accent_colors': {'max_num': 1},
            'divider_colors': {'max_num': 1},
            'background_color': {'max_num': 1},
            'border_size': {'max_num': 1},
        }, required=False)),
    ], label="Cards Block")),
    ('text', APIRichTextBlock()),
    ('html', blocks.RawHTMLBlock()),
    ('cta_block', CTAButtonBarBlock()),
    ('links_group', LinksGroupBlock()),
    ('quote', QuoteBlock()),
    ('faq', blocks.StreamBlock([
        ('faq', FAQBlock()),
    ])),
    ('book_list', blocks.StructBlock([
        ('books', blocks.ListBlock(BookBlock(required=True))),
    ], label="Books Block")),
]

# Layer 2: Content blocks + well (well references BASE, not itself)
SECTION_CONTENT_BLOCKS = BASE_CONTENT_BLOCKS + [
    ('well', blocks.StructBlock([
        ('content', blocks.StreamBlock(BASE_CONTENT_BLOCKS)),
        ('config', blocks.StreamBlock([
            ('background_color', hex_color_block('Background color of the well. Must be hex eg: #ff0000.')),
        ] + gradient_config_options() + [
            ('border_radius', blocks.IntegerBlock(min_value=0, help_text='Border radius in pixels. default 0.')),
            ('border_color', hex_color_block('Border color. Must be hex eg: #ff0000.')),
            ('border_size', blocks.IntegerBlock(min_value=0, help_text='Border size in pixels. default 0.')),
            ('padding', blocks.IntegerBlock(min_value=0, help_text='Padding inside the well. default 0.')),
            ('margin', blocks.IntegerBlock(help_text='Margin outside the well. default 0.')),
            ('pull_up', blocks.IntegerBlock(help_text='Pulls the well up by this many pixels (negative margin-top). default 0.')),
            ('width', blocks.RegexBlock(
                regex=r'^[0-9]+(px|%|rem)$', required=False,
                help_text='Width of the well. Must be valid css measurement. eg: 30px, 50%, 10rem.',
                error_mssages={'invalid': 'not a valid size.'}
            )),
            ('text_alignment', blocks.ChoiceBlock(choices=TEXT_ALIGNMENT_CHOICES, help_text='Text alignment inside the well. Default left.')),
            ('analytics_label', blocks.CharBlock(required=False, help_text='Sets the "analytics nav" field for links within this well.')),
            ('id', id_config_block()),
        ], block_counts={
            'background_color': {'max_num': 1},
            **gradient_block_counts(),
            'border_radius': {'max_num': 1},
            'border_color': {'max_num': 1},
            'border_size': {'max_num': 1},
            'padding': {'max_num': 1},
            'margin': {'max_num': 1},
            'pull_up': {'max_num': 1},
            'width': {'max_num': 1},
            'text_alignment': {'max_num': 1},
            'analytics_label': {'max_num': 1},
            'id': {'max_num': 1},
        }, required=False)),
    ], label="Well")),
]

# Layer 3: Structural blocks (used in body + tabbed_content tabs)
BODY_BLOCKS = [
    ('hero', blocks.StructBlock([
        ('content', blocks.StreamBlock(SECTION_CONTENT_BLOCKS)),
        ('image', APIImageChooserBlock(required=False)),
        ('image_alt', blocks.CharBlock(required=False)),
        ('config', blocks.StreamBlock([
            ('image_alignment', blocks.ChoiceBlock(choices=HERO_IMAGE_ALIGNMENT_CHOICES, help_text='Controls if the image is on the left or right side of the content, and if it prefers to be at the top, center, or bottom of the available space.')),
            ('id', id_config_block()),
            ('background_color', hex_color_block('Sets the background color of the section. value must be hex eg: #ff0000. Default grey.')),
        ] + gradient_config_options() + [
            ('padding', blocks.IntegerBlock(min_value=0, help_text='Creates space above and below this section. default 0.')),
            ('padding_top', blocks.IntegerBlock(min_value=0, help_text='Creates space above this section. default 0.')),
            ('padding_bottom', blocks.IntegerBlock(min_value=0, help_text='Creates space below this section. default 0.')),
            ('text_alignment', blocks.ChoiceBlock(choices=TEXT_ALIGNMENT_CHOICES, default='left', help_text='Configures text alignment within the container. Default Left.')),
            ('analytics_label', blocks.CharBlock(required=False, help_text='Sets the "analytics nav" field for links within this section.')),
            ('image_border_radius', blocks.IntegerBlock(min_value=0, help_text='Border radius for the hero image in pixels. default 0.')),
            ('image_border_color', hex_color_block('Border color for the hero image. Must be hex eg: #ff0000.')),
            ('image_border_size', blocks.IntegerBlock(min_value=0, help_text='Border size for the hero image in pixels. default 0.')),
            ('image_overhang', blocks.IntegerBlock(help_text='How much the image overhangs the section boundary in pixels. default 0.')),
            ('rendering_condition', blocks.CharBlock(required=False, help_text='Condition that determines if this block should render. eg: defined by the frontend.')),
        ], block_counts={
            'image_alignment': {'max_num': 1},
            'id': {'max_num': 1},
            'background_color': {'max_num': 1},
            **gradient_block_counts(),
            'padding': {'max_num': 1},
            'padding_top': {'max_num': 1},
            'padding_bottom': {'max_num': 1},
            'text_alignment': {'max_num': 1},
            'analytics_label': {'max_num': 1},
            'image_border_radius': {'max_num': 1},
            'image_border_color': {'max_num': 1},
            'image_border_size': {'max_num': 1},
            'image_overhang': {'max_num': 1},
            'rendering_condition': {'max_num': 1},
        }, required=False))
    ])),
    ('section', blocks.StructBlock([
        ('content', blocks.StreamBlock(SECTION_CONTENT_BLOCKS)),
        ('config', blocks.StreamBlock([
            ('id', id_config_block()),
            ('background_color', hex_color_block('Sets the background color of the section. value must be hex eg: #ff0000. Default grey.')),
        ] + gradient_config_options() + [
            ('padding', blocks.IntegerBlock(min_value=0, help_text='Creates space above and below this section. default 0.')),
            ('padding_top', blocks.IntegerBlock(min_value=0, help_text='Creates space above this section. default 0.')),
            ('padding_bottom', blocks.IntegerBlock(min_value=0, help_text='Creates space below this section. default 0.')),
            ('text_alignment', blocks.ChoiceBlock(choices=TEXT_ALIGNMENT_CHOICES, default='left', help_text='Configures text alignment within the container. Default Left.')),
            ('analytics_label', blocks.CharBlock(required=False, help_text='Sets the "analytics nav" field for links within this section.')),
            ('flex', blocks.ChoiceBlock(choices=FLEX_CHOICES, help_text='Flex behavior of this section. Default none.')),
            ('rendering_condition', blocks.CharBlock(required=False, help_text='Condition that determines if this block should render. eg: defined by the frontend.')),
        ], block_counts={
            'id': {'max_num': 1},
            'background_color': {'max_num': 1},
            **gradient_block_counts(),
            'padding': {'max_num': 1},
            'padding_top': {'max_num': 1},
            'padding_bottom': {'max_num': 1},
            'text_alignment': {'max_num': 1},
            'analytics_label': {'max_num': 1},
            'flex': {'max_num': 1},
            'rendering_condition': {'max_num': 1},
        }, required=False))
    ])),
    ('columns', blocks.StructBlock([
        ('left_content', blocks.StreamBlock(SECTION_CONTENT_BLOCKS)),
        ('right_content', blocks.StreamBlock(SECTION_CONTENT_BLOCKS)),
        ('config', blocks.StreamBlock([
            ('background_color', hex_color_block('Background color of the columns container. Must be hex eg: #ff0000.')),
        ] + gradient_config_options() + [
            ('padding', blocks.IntegerBlock(min_value=0, help_text='Padding for the columns container. default 0.')),
            ('padding_top', blocks.IntegerBlock(min_value=0, help_text='Padding above the columns container. default 0.')),
            ('padding_bottom', blocks.IntegerBlock(min_value=0, help_text='Padding below the columns container. default 0.')),
            ('flex', blocks.ChoiceBlock(choices=FLEX_CHOICES, help_text='Flex behavior. Default none.')),
            ('analytics_label', blocks.CharBlock(required=False, help_text='Sets the "analytics nav" field for links within this block.')),
            ('id', id_config_block()),
            ('gap', blocks.IntegerBlock(min_value=0, help_text='Gap between the two columns in pixels. default 0.')),
            ('left_size', blocks.IntegerBlock(min_value=1, help_text='Relative size of the left column. default 1.')),
            ('right_size', blocks.IntegerBlock(min_value=1, help_text='Relative size of the right column. default 1.')),
        ], block_counts={
            'background_color': {'max_num': 1},
            **gradient_block_counts(),
            'padding': {'max_num': 1},
            'padding_top': {'max_num': 1},
            'padding_bottom': {'max_num': 1},
            'flex': {'max_num': 1},
            'analytics_label': {'max_num': 1},
            'id': {'max_num': 1},
            'gap': {'max_num': 1},
            'left_size': {'max_num': 1},
            'right_size': {'max_num': 1},
        }, required=False)),
    ], label="Columns")),
    ('divider', DividerBlock()),
    ('html', blocks.RawHTMLBlock()),
]

# we have one RootPage, which is the parent of all other pages
# this is the only page that should be created at the top level of the page tree
# this should be the homepage
