from django.templatetags.static import static
from django.utils.html import format_html
from wagtail import hooks


@hooks.register('insert_editor_js')
def conditional_school_field_js():
    """Inject JavaScript to conditionally show school field only for landing pages"""
    return format_html(
        '<script src="{}"></script>',
        static('pages/conditional-school-field.js')
    )

