from wagtail.api.v2.endpoints import PagesAPIEndpoint, BaseAPIEndpoint
from wagtail.api.v2.router import WagtailAPIRouter
from wagtail.images.api.v2.endpoints import ImagesAPIEndpoint
from wagtail.documents.api.v2.endpoints import DocumentsAPIEndpoint
from wagtail.core.models import Page

from oxauth.views import get_user_data
from oxauth.functions import get_user_info

from django.utils import timezone

from .functions import remove_locked_links_listing, remove_locked_links_detail

from flags.state import flag_state

import json


# Create the router. "wagtailapi" is the URL namespace
api_router = WagtailAPIRouter('wagtailapi')

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

        #TODO: Removing all caches to try and fix issues, put back in after a few releases
        # # Implementing Caching
        # response['Cache-Control'] = 'max-age=290304000, public'
        # response['Last-Modified'] = page.last_published_at
        #
        # # If we ended up revealing a link, then force the content to be loaded.
        # if not any_hidden or request.GET.get('force-reload'):
        #     response['Last-Modified'] = timezone.now()
        
        return response


# Add the three endpoints using the "register_endpoint" method.
# The first parameter is the name of the endpoint (eg. pages, images). This
# is used in the URL of the endpoint
# The second parameter is the endpoint class that handles the requests
api_router.register_endpoint('pages', PagesAPIEndpoint)
api_router.register_endpoint('images', ImagesAPIEndpoint)
api_router.register_endpoint('documents', DocumentsAPIEndpoint)