from wagtail.api.v2.endpoints import PagesAPIEndpoint, BaseAPIEndpoint
from wagtail.api.v2.router import WagtailAPIRouter
from wagtail.images.api.v2.endpoints import ImagesAPIEndpoint
from wagtail.documents.api.v2.endpoints import DocumentsAPIEndpoint
from wagtail.core.models import Page

## TODO: This can be removed when Wagtail fixes admin API
from collections import OrderedDict
from wagtail.admin.api.endpoints import PagesAdminAPIEndpoint
from wagtail.api.v2.filters import (
    ChildOfFilter, DescendantOfFilter, FieldsFilter, OrderingFilter,
    SearchFilter, ForExplorerFilter)
from wagtail.admin.api.serializers import AdminPageSerializer
from wagtail.admin.api.filters import HasChildrenFilter
from wagtail.api.v2.utils import BadRequestError, filter_page_type, page_models_from_string
from wagtail.core import hooks
from wagtail.core.models import Page, UserPagePermissionsProxy
## TODO: END

from oxauth.views import get_user_data
from oxauth.functions import get_user_info

from django.utils import timezone

from .functions import remove_locked_links_listing, remove_locked_links_detail

from flags.state import flag_state

import json


# Create the router. "wagtailapi" is the URL namespace
api_router = WagtailAPIRouter('wagtailapi')
admin_api = WagtailAPIRouter('wagtailadmin_api_v1')

#TODO: This is fixed in an upcoming version of Wagtail, and should be removed.
# If the API is causing errors after an upgrade - this is likely the first two classes to remove!
class ImagesAPIEndpoint(ImagesAPIEndpoint):

    body_fields = ImagesAPIEndpoint.body_fields + [
        'file',
    ]

    listing_default_fields = ImagesAPIEndpoint.listing_default_fields + [
        'file',
    ]

class DocumentsAPIEndpoint(DocumentsAPIEndpoint):
    body_fields = DocumentsAPIEndpoint.body_fields + [
        'file',
    ]

    listing_default_fields = DocumentsAPIEndpoint.listing_default_fields + [
        'file',
    ]

        
class PagesAPIEndpoint(PagesAPIEndpoint):
    def listing_view(self, request):

        response = super().listing_view(request)
        
        # Implementing User Authentication
        auth_user = json.loads(get_user_data(request).content.decode())

        # Fetching User Information and Overwriting auth_user
        if "user" in auth_user:
            auth_user = get_user_info(auth_user["user"]["id"])
        
        # Overwriting the Response if ox credential does not
        # authorize faculty access.
        if "faculty_status" not in auth_user or auth_user["faculty_status"] != "confirmed_faculty":
            if flag_state('hide_faculty_resources', bool=True):
                remove_locked_links_listing(response)

        return response

    def detail_view(self, request, pk):

        any_hidden = False

        response = super().detail_view(request, pk)
        page = Page.objects.get(pk=pk)

        # Implementing User Authentication
        auth_user = json.loads(get_user_data(request).content.decode())

        # Fetching User Information and Overwriting auth_user
        if "user" in auth_user:
            auth_user = get_user_info(auth_user["user"]["id"])

        # Overwriting the Response if ox credential does not
        # authorize faculty access.
        if "faculty_status" not in auth_user or auth_user["faculty_status"] != "confirmed_faculty":
            if flag_state('hide_faculty_resources', bool=True):
                any_hidden = remove_locked_links_detail(response)

        # Implementing Caching
        response['Cache-Control'] = 'no-cache'

        # If we ended up revealing a link, then force the content to be loaded.
        if not any_hidden or request.GET.get('force-reload'):
            response['Last-Modified'] = timezone.now()

        
        return response


## TODO: This can be removed when Wagtail fixes admin API
class ForExplorerFilter(ForExplorerFilter):
    def filter_queryset(self, request, queryset, view):
        if request.GET.get('for_explorer'):
            if not hasattr(queryset, '_filtered_by_child_of'):
                raise BadRequestError("filtering by for_explorer without child_of is not supported")

            parent_page = queryset._filtered_by_child_of
            ##TODO: This is where the code is broken, see: https://github.com/wagtail/wagtail/blob/17e541715a80a43bc4eb1f1b07183bf22bb1869a/wagtail/contrib/modeladmin/options.py#L49
            # for hook in hooks.get_hooks('construct_explorer_page_queryset'):
            #     queryset = hook(parent_page, queryset, request)

            user_perms = UserPagePermissionsProxy(request.user)
            # This is returning an empty list! WRONG!
            #print(user_perms.explorable_pages())
            queryset = queryset & user_perms.explorable_pages()


        return queryset


class PagesAdminAPIEndpoint(PagesAdminAPIEndpoint):
    base_serializer_class = AdminPageSerializer

    # Use unrestricted child_of/descendant_of filters
    # Add has_children filter
    filter_backends = [
        FieldsFilter,
        ChildOfFilter,
        DescendantOfFilter,
        #ForExplorerFilter, # uncomment this and use the filter class in this file to debug further
        HasChildrenFilter,
        OrderingFilter,
        SearchFilter,
    ]

    meta_fields = PagesAPIEndpoint.meta_fields + [
        'latest_revision_created_at',
        'status',
        'children',
        'descendants',
        'parent',
    ]

    body_fields = PagesAPIEndpoint.body_fields + [
        'admin_display_title',
    ]

    listing_default_fields = PagesAPIEndpoint.listing_default_fields + [
        'latest_revision_created_at',
        'status',
        'children',
        'admin_display_title',
    ]

    # Allow the parent field to appear on listings
    detail_only_fields = []

    known_query_parameters = PagesAPIEndpoint.known_query_parameters.union([
        'for_explorer',
        'has_children'
    ])

    def get_queryset(self):
        request = self.request

        # Allow pages to be filtered to a specific type
        try:
            models = page_models_from_string(request.GET.get('type', 'wagtailcore.Page'))
        except (LookupError, ValueError):
            raise BadRequestError("type doesn't exist")

        if not models:
            models = [Page]

        if len(models) == 1:
            queryset = models[0].objects.all()
        else:
            queryset = Page.objects.all()

            # Filter pages by specified models
            queryset = filter_page_type(queryset, models)

        # Hide root page
        # TODO: Add "include_root" flag
        queryset = queryset.exclude(depth=1).specific()

        return queryset

    def get_type_info(self):
        types = OrderedDict()

        for name, model in self.seen_types.items():
            types[name] = OrderedDict([
                ('verbose_name', model._meta.verbose_name),
                ('verbose_name_plural', model._meta.verbose_name_plural),
            ])

        return types

    def listing_view(self, request):
        response = super().listing_view(request)
        response.data['__types'] = self.get_type_info()
        return response

    def detail_view(self, request, pk):
        response = super().detail_view(request, pk)
        response.data['__types'] = self.get_type_info()
        return response

## TODO: End (Remove URLs too)

# Add the three endpoints using the "register_endpoint" method.
# The first parameter is the name of the endpoint (eg. pages, images). This
# is used in the URL of the endpoint
# The second parameter is the endpoint class that handles the requests
admin_api.register_endpoint('pages', PagesAdminAPIEndpoint)
api_router.register_endpoint('pages', PagesAPIEndpoint)
api_router.register_endpoint('images', ImagesAPIEndpoint)
api_router.register_endpoint('documents', DocumentsAPIEndpoint)
api_router.register_endpoint('documents', DocumentsAPIEndpoint)