import wagtail.admin.rich_text.editors.draftail.features as draftail_features
from wagtail.admin.rich_text.converters.html_to_contentstate import InlineStyleElementHandler
from wagtail import hooks
from django.urls import reverse
from wagtail.admin.menu import MenuItem


@hooks.register('register_rich_text_features')
def register_strikethrough_feature(features):
    """
    Registering the `superscript` feature, which uses the `SUPERSCRIPT` Draft.js inline style type,
    and is stored as HTML with an `<sup>` tag.
    """
    feature_name = 'superscript'
    type_ = 'SUPERSCRIPT'
    tag = 'sup'

    control = {
        'type': type_,
        'label': '^',
        'description': 'Superscript',
    }

    features.register_editor_plugin(
        'draftail', feature_name, draftail_features.InlineStyleFeature(control)
    )

    db_conversion = {
        'from_database_format': {tag: InlineStyleElementHandler(type_)},
        'to_database_format': {'style_map': {type_: tag}},
    }
    features.default_features.append(feature_name)
    features.register_converter_rule('contentstate', feature_name, db_conversion)


@hooks.register('register_settings_menu_item')
def register_500_menu_item():
    return MenuItem('Generate 500', reverse('throw_error'), classname='icon icon-warning', order=10000)


@hooks.register('register_settings_menu_item')
def register_clear_cache_menu_item():
    return MenuItem('Clear Cloudfront Cache', reverse('clear_entire_cache'), classname='icon icon-bin', order=11000)
