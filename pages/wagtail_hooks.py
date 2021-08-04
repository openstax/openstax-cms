from django.templatetags.static import static
from django.utils.html import format_html
from django.urls import reverse

from wagtail.core import hooks

@hooks.register('insert_editor_css')
def editor_css():
    return format_html(
        '<link rel="stylesheet" href="{}">',
        static("wagtail_hooks/css/page_wagtail_hooks.css")
    )


@hooks.register('insert_editor_js')
def editor_js():
    return format_html(
        """
        <script>
            window.chooserUrls.pageChooser = '{}';
        </script>
        """,
        reverse('wagtailadmin_choose_page_external_link')
    )