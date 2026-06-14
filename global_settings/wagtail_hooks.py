import wagtail.admin.rich_text.editors.draftail.features as draftail_features
from wagtail.admin.rich_text.converters.html_to_contentstate import InlineStyleElementHandler
from wagtail import hooks
from django.urls import path, reverse
from wagtail.admin.menu import Menu, MenuItem, SubmenuMenuItem

from global_settings import views


# A nested "Tools" menu for developer/operations utilities (Import, Versions, …)
# so they stop cluttering the top level. Other apps add items by registering for
# the ``register_tools_menu_item`` hook (see versions/wagtail_hooks.py).
tools_menu = Menu(
    register_hook_name="register_tools_menu_item",
    construct_hook_name="construct_tools_menu",
)


@hooks.register("register_admin_menu_item")
def register_tools_menu():
    return SubmenuMenuItem("Tools", tools_menu, icon_name="cogs", order=9000)


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


@hooks.register('register_admin_urls')
def register_experiments_guide_url():
    return [path('experiments/', views.experiments_guide, name='experiments_guide')]


@hooks.register('register_settings_menu_item')
def register_experiments_menu_item():
    return MenuItem(
        'Experiments & Measurement',
        reverse('experiments_guide'),
        icon_name='bulb',
        order=9000,
    )
# --- Wagtail Transfer "Import" menu ----------------------------------------
# The package only shows its Import menu item once WAGTAILTRANSFER_SOURCES is
# configured, so it is invisible on a fresh/local environment with no sources.
# We show it for any staff member who holds the import permission (the page
# itself lists whatever sources are configured, or none), and drop the
# package's own item to avoid a duplicate when sources ARE set.
class WagtailTransferImportMenuItem(MenuItem):
    def is_shown(self, request):
        return request.user.has_perm('wagtail_transfer.wagtailtransfer_can_import')


@hooks.register('register_tools_menu_item')
def register_wagtail_transfer_import_menu_item():
    return WagtailTransferImportMenuItem(
        'Import',
        reverse('wagtail_transfer_admin:choose_page'),
        name='wagtail-transfer-import',
        icon_name='doc-empty-inverse',
        order=100,
    )


@hooks.register('construct_main_menu')
def remove_duplicate_wagtail_transfer_import_item(request, menu_items):
    # The package registers its item with name 'import' pointing at the same
    # choose_page URL as ours ('wagtail-transfer-import'). When sources ARE
    # configured both pass is_shown, so drop the package's to avoid a duplicate.
    # Match on name AND url so we never remove an unrelated 'import' item.
    transfer_url = reverse('wagtail_transfer_admin:choose_page')
    menu_items[:] = [
        item for item in menu_items
        if not (item.name == 'import' and getattr(item, 'url', None) == transfer_url)
    ]
