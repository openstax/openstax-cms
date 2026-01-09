from django.templatetags.static import static
from django.utils.html import format_html
from wagtail import hooks
from wagtail.models import Page

from pages.models import FlexPage


@hooks.register('before_edit_page')
def attach_page_instance_to_request(request, page):
    """Attach the page instance to the request object for use in other hooks"""
    request.page_instance = page


@hooks.register('insert_editor_js')
def conditional_school_field_js(request):
    """Inject JavaScript to conditionally show school field only for landing pages"""
    # Check if we have a page instance attached via before_edit_page hook
    if hasattr(request, 'page_instance'):
        page = request.page_instance
    else:
        # Fallback: Try to extract page ID from URL for edit pages
        # This handles cases where before_edit_page might not have run yet
        try:
            path_parts = request.path.strip('/').split('/')
            if 'pages' in path_parts and 'edit' in path_parts:
                page_idx = path_parts.index('pages')
                if page_idx + 1 < len(path_parts):
                    page_id = int(path_parts[page_idx + 1])
                    page = Page.objects.get(id=page_id).specific
                else:
                    page = None
            else:
                page = None
        except (ValueError, IndexError, Page.DoesNotExist):
            page = None

    # Only load the JavaScript when editing RootPage instances
    if page and isinstance(page, FlexPage):
        return format_html(
            '<script src="{}"></script>',
            static('pages/conditional-school-field.js')
        )
    return format_html('')

