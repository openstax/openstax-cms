import os

from django.contrib.staticfiles import finders
from django.templatetags.static import static
from django.urls import path, reverse
from django.utils.html import format_html
from wagtail import hooks
from wagtail.admin import widgets as wagtailadmin_widgets
from wagtail.snippets.models import register_snippet
from wagtail.snippets.views.snippets import SnippetViewSet

from pages.models import FlexPage, PersonTag
from pages.views_promote import promote_to_home_view


def _versioned(path):
    """Return the static URL with an mtime cache-buster so admin asset edits
    are picked up without a manual hard refresh (the admin caches these URLs).
    Falls back to the plain URL if the file can't be located, so a lookup
    problem can never break the editor."""
    url = static(path)
    try:
        abs_path = finders.find(path)
        if abs_path and os.path.exists(abs_path):
            url = '{}?v={}'.format(url, int(os.path.getmtime(abs_path)))
    except (OSError, TypeError, ValueError):
        # Any static lookup/mtime issue should not break the editor; use plain URL.
        return url
    return url


@hooks.register('insert_editor_js')
def conditional_school_field_js():
    """Inject JavaScript to conditionally show school field only for landing pages"""
    return format_html(
        '<script src="{}"></script>',
        _versioned('pages/conditional-school-field.js'),
    )


# The brand-swatch picker's CSS/JS now ship via OpenStaxColorInputWidget.media
# (pages/custom_blocks.py) — the idiomatic Wagtail mechanism, loaded only when a
# colour field is on the page. Note: insert_editor_css is NOT rendered in
# Wagtail 7.4, so widget Media (not that hook) is the correct home for this.


class PersonTagViewSet(SnippetViewSet):
    model = PersonTag
    icon = "tag"
    menu_label = "Person Tags"


register_snippet(PersonTagViewSet)


@hooks.register('register_admin_urls')
def register_promote_to_home_url():
    return [
        path('promote-to-home/<int:page_id>/', promote_to_home_view, name='promote_to_home'),
    ]


def _is_flex_page(page):
    # specific_class (content-type lookup) instead of .specific (extra query per row) —
    # these hooks run once per listing row, so avoid fetching the full instance.
    return page.specific_class is FlexPage


@hooks.register('register_page_listing_more_buttons')
def promote_to_home_listing_button(page, user, next_url=None):
    if _is_flex_page(page):
        yield wagtailadmin_widgets.Button(
            'Promote to home page',
            reverse('promote_to_home', args=[page.id]),
            icon_name='upload',
            priority=70,
        )


@hooks.register('register_page_header_buttons')
def promote_to_home_header_button(page, user, view_name, next_url=None):
    if _is_flex_page(page):
        yield wagtailadmin_widgets.Button(
            'Promote to home page',
            reverse('promote_to_home', args=[page.id]),
            icon_name='upload',
            priority=80,
        )

