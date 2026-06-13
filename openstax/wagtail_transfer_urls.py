"""Hardened mount of wagtail-transfer's *export* (source-side) API.

This mirrors ``wagtail_transfer.urls`` (the package's top-level urlconf) but
wraps each export view with the guards in ``wagtail_transfer_security``:
``block_if_insecure_key`` on everything, and ``restrict_exportable_models`` on
the two endpoints that will otherwise serialize arbitrary models.

The admin UI + menu (``choose/``, ``import/`` …) come from the package's
``register_admin_urls`` hook and are unaffected by this module.
"""
from django.urls import path, re_path
from wagtail.utils.urlpatterns import decorate_urlpatterns

from wagtail_transfer import views
from wagtail_transfer.auth import check_get_digest_wrapper
from wagtail_transfer.vendor.wagtail_api_v2.router import WagtailAPIRouter
from wagtail_transfer.vendor.wagtail_api_v2.views import ModelsAPIViewSet

from .wagtail_transfer_security import block_if_insecure_key, restrict_exportable_models

chooser_api = WagtailAPIRouter('wagtail_transfer_page_chooser_api')
chooser_api.register_endpoint('pages', views.PageChooserAPIViewSet)
chooser_api.register_endpoint('models', ModelsAPIViewSet)

urlpatterns = [
    re_path(
        r'^api/pages/(\d+)/$',
        block_if_insecure_key(views.pages_for_export),
        name='wagtail_transfer_pages',
    ),
    path(
        'api/models/<str:model_path>/',
        block_if_insecure_key(restrict_exportable_models(views.models_for_export)),
        name='wagtail_transfer_model',
    ),
    path(
        'api/models/<str:model_path>/<int:object_id>/',
        block_if_insecure_key(restrict_exportable_models(views.models_for_export)),
        name='wagtail_transfer_model_object',
    ),
    path(
        'api/objects/',
        block_if_insecure_key(restrict_exportable_models(views.objects_for_export)),
        name='wagtail_transfer_objects',
    ),
    re_path(
        r'^api/chooser/',
        # (patterns, app_namespace, instance_namespace) — namespaces must match
        # the package's so reverse() lookups resolve.
        (
            decorate_urlpatterns(
                chooser_api.get_urlpatterns(),
                lambda v: block_if_insecure_key(check_get_digest_wrapper(v)),
            ),
            chooser_api.url_namespace,
            chooser_api.url_namespace,
        ),
    ),
]
