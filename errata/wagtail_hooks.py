from wagtail import hooks
from .views import errata_viewset

@hooks.register("register_admin_viewset")
def register_viewset():
    return errata_viewset
