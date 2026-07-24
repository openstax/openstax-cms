from wagtail import blocks



from pages.custom_blocks import APIImageChooserBlock, \
    FAQBlock, \
    DividerBlock, \
    APIRichTextBlock, \
    CTAButtonBarBlock, \
    LinksGroupBlock, \
    QuoteBlock, \
    BookBlock, \
    PersonBlock, \
    CARDS_STYLE_CHOICES, \
    CARDS_LAYOUT_CHOICES, \
    TEXT_ALIGNMENT_CHOICES, \
    WELL_LAYOUT_CHOICES, \
    WELL_HEADING_STYLE_CHOICES, \
    FLEX_CHOICES

from pages.shared_blocks import CTALinkBlock, OpenStaxColorBlock, hex_color_block, \
    gradient_config_options, gradient_block_counts, id_config_block, CollapsedHTMLBlock

from pages.table_block import TableBlock



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
                ('config', blocks.StreamBlock([
                    ('accent_color', OpenStaxColorBlock(help_text='Accent color for this card: the border on rounded style, the top accent bar on square (needs Accent Size). Leave unset for the default palette.')),
                    ('divider_color', OpenStaxColorBlock(help_text='Color for divider lines in this card. Leave unset for the default palette.')),
                ], block_counts={
                    'accent_color': {'max_num': 1},
                    'divider_color': {'max_num': 1},
                }, required=False, collapsed=True)),
            ]),
        )),
        ('config', blocks.StreamBlock([
            ('card_size', blocks.IntegerBlock(min_value=0, help_text='Sets the width of the individual cards. default 27.')),
            ('card_style', blocks.ChoiceBlock(choices=CARDS_STYLE_CHOICES, help_text='The border style of the cards. default borderless.')),
            ('layout', blocks.ChoiceBlock(choices=CARDS_LAYOUT_CHOICES,
                help_text='Grid aligns cards into rows (default); Masonry packs them into columns by height, for decorative card walls.')),
            ('card_columns', blocks.IntegerBlock(min_value=1, max_value=6, help_text='Number of columns for the cards grid. default auto.')),
            ('background_color', hex_color_block('Background color for the cards block. Must be hex eg: #ff0000.')),
            ('border_size', blocks.IntegerBlock(min_value=0, help_text='Outer border width in px (all sides). Omit to use the style default; 0 = no border.')),
            ('accent_size', blocks.IntegerBlock(min_value=0, help_text='Top accent bar height in px, independent of the border. Color comes from each card\'s Accent Color.')),
            ('padding', blocks.IntegerBlock(min_value=0, help_text='Top and bottom spacing around the block, in 10px increments.')),
            ('padding_top', blocks.IntegerBlock(min_value=0, help_text='Top spacing around the block, in 10px increments.')),
            ('padding_bottom', blocks.IntegerBlock(min_value=0, help_text='Bottom spacing around the block, in 10px increments.')),
        ], block_counts={
            'card_size': {'max_num': 1},
            'card_style': {'max_num': 1},
            'layout': {'max_num': 1},
            'card_columns': {'max_num': 1},
            'background_color': {'max_num': 1},
            'border_size': {'max_num': 1},
            'accent_size': {'max_num': 1},
            'padding': {'max_num': 1},
            'padding_top': {'max_num': 1},
            'padding_bottom': {'max_num': 1},
        }, required=False, collapsed=True)),
    ], label="Cards Block")),
    ('text', APIRichTextBlock()),
    ('html', CollapsedHTMLBlock()),
    ('cta_block', CTAButtonBarBlock()),
    ('links_group', LinksGroupBlock()),
    ('quote', QuoteBlock()),
    ('big_number', blocks.StructBlock([
        ('number', blocks.CharBlock(help_text='The statistic to display large, e.g. 8M+.')),
        ('caption', blocks.CharBlock(required=False, help_text='Optional supporting text shown below the number.')),
        ('color', blocks.ChoiceBlock(required=False, choices=[
            ('blue', 'Blue'),
            ('green', 'Green'),
            ('orange', 'Orange'),
        ], help_text='Brand color for the number. Defaults to the inherited text color.')),
    ], label="Big Number")),
    ('faq', blocks.StreamBlock([
        ('faq', FAQBlock()),
    ])),
    ('accordion', blocks.StructBlock([
        ('items', blocks.ListBlock(
            blocks.StructBlock([
                ('header', blocks.CharBlock(required=True, help_text='The visible text of the item.')),
                ('content', APIRichTextBlock(required=True, help_text='Hidden until the item is expanded.')),
                ('id', id_config_block()),
            ]),
            label='Items',
        )),
        ('config', blocks.StreamBlock([
            ('heading_level', blocks.ChoiceBlock(choices=[
                ('2', 'H2'),
                ('3', 'H3'),
                ('4', 'H4'),
            ], help_text='Heading level for each item, for the document outline and screen-reader navigation. Default H3.')),
            ('allow_multiple', blocks.ChoiceBlock(choices=[
                ('false', 'No'),
                ('true', 'Yes'),
            ], help_text='Allow more than one item to be open at the same time. Default No.')),
            ('accent_color', hex_color_block('Hex color for the expand/collapse icon and item divider.')),
            ('accent_colors', blocks.RegexBlock(
                regex=r'^#[0-9a-fA-F]{6}(\s*,\s*#[0-9a-fA-F]{6})*$', required=False,
                label='Accent Colors',
                help_text='Comma-separated hex colors cycled per item, e.g. #ff0000,#00ff00. Overrides Accent Color.',
                error_messages={'invalid': 'Must be comma-separated hex colors. eg: #ff0000,#00ff00.'},
            )),
            ('top_border_color', hex_color_block('Adds a colored border above the whole accordion.')),
        ], block_counts={
            'heading_level': {'max_num': 1},
            'allow_multiple': {'max_num': 1},
            'accent_color': {'max_num': 1},
            'accent_colors': {'max_num': 1},
            'top_border_color': {'max_num': 1},
        }, required=False, collapsed=True)),
    ], label="Accordion")),
    ('book_list', blocks.StructBlock([
        ('books', blocks.ListBlock(BookBlock(required=True))),
    ], label="Books Block")),
    ('person', PersonBlock()),
    ('table', TableBlock()),
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
                error_messages={'invalid': 'not a valid size.'}
            )),
            ('text_alignment', blocks.ChoiceBlock(choices=TEXT_ALIGNMENT_CHOICES, help_text='Text alignment inside the well. Default left.')),
            ('layout', blocks.ChoiceBlock(choices=WELL_LAYOUT_CHOICES,
                help_text='How the well lays out its content blocks. "Wrap" puts them side by side (e.g. a row of Big Numbers), reflowing to fewer per row as the screen narrows. Default stack.')),
            ('heading_style', blocks.ChoiceBlock(choices=WELL_HEADING_STYLE_CHOICES,
                help_text='Renders a Text block\'s h6 headings as a large, fluid-sized display quote (e.g. a testimonial pull-quote) instead of regular heading size. Default normal.')),
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
            'layout': {'max_num': 1},
            'heading_style': {'max_num': 1},
            'analytics_label': {'max_num': 1},
            'id': {'max_num': 1},
        }, required=False, collapsed=True)),
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
            ('image_overhang', blocks.RegexBlock(
                regex=r'^[0-9]+(px|%|rem)$', required=False,
                help_text='How much the image overhangs the section boundary. Must be a valid css measurement. eg: 30px, 50%, 10rem.',
                error_messages={'invalid': 'not a valid size.'},
            )),
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
        }, required=False, collapsed=True))
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
        }, required=False, collapsed=True))
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
        }, required=False, collapsed=True)),
    ], label="Columns")),
    ('divider', DividerBlock()),
    ('html', CollapsedHTMLBlock()),
]

# we have one RootPage, which is the parent of all other pages
# this is the only page that should be created at the top level of the page tree
# this should be the homepage
