from django.templatetags.static import static
from django.utils.html import format_html
from wagtail import hooks
from pages.models import RootPage

@hooks.register('insert_editor_js')
def conditional_school_field_js(request):
    """Inject JavaScript to conditionally show school field only for RootPage edit views"""
    # Only inject JS if editing a RootPage instance
    if hasattr(request, 'instance') and isinstance(getattr(request, 'instance', None), RootPage):
        return format_html(
            '<script src="{}"></script>',
            static('pages/conditional-school-field.js')
        )
    return ''
