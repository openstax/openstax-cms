try:
    from wagtail.admin import messages
    from wagtail.admin.menu import MenuItem
    from wagtail.admin.widgets import AdminPageChooser
    from wagtail.core import hooks
    from wagtail.core.models import Page

    WAGTAIL_VERSION_2_OR_GREATER = True
except ImportError:  # fallback for Wagtail <2.0
    from wagtail.wagtailadmin import messages
    from wagtail.wagtailadmin.menu import MenuItem
    from wagtail.wagtailadmin.widgets import AdminPageChooser
    from wagtail.wagtailcore import hooks
    from wagtail.wagtailcore.models import Page

    WAGTAIL_VERSION_2_OR_GREATER = False
