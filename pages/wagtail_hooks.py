import os

from django.contrib.staticfiles import finders
from django.templatetags.static import static
from django.utils.html import format_html
from wagtail import hooks
from wagtail.models import Page

from pages.models import FlexPage


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

