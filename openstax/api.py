from wagtail.api.v2.endpoints import PagesAPIEndpoint, BaseAPIEndpoint
from wagtail.api.v2.router import WagtailAPIRouter
from wagtail.images.api.v2.endpoints import ImagesAPIEndpoint
from wagtail.documents.api.v2.endpoints import DocumentsAPIEndpoint
from wagtail.core.models import Page

from oxauth.views import get_user_data
from oxauth.functions import get_user_info

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

        
class CachedPagesAPIEndpoint(PagesAPIEndpoint):
    def listing_view(self, request):

        response = super().listing_view(request)
        
        # Implementing User Authentication
        auth_user = json.loads(get_user_data(request).content.decode())

        # Fetching User Information and Overwriting auth_user
        if "user_id" in auth_user:
            auth_user = get_user_info(auth_user["user_id"])

        # Overwriting the Response if ox credential does not
        # authorize faculty access.
        if "book_faculty_resources" in response.data:
            if "faculty_status" not in auth_user or auth_user["faculty_status"] != "confirmed_faculty":
                for res_id in range(len(response.data["book_faculty_resources"])):
                    if not response.data["book_faculty_resources"][res_id]["resource_unlocked"]:
                        response.data["book_faculty_resources"][res_id]["link_document_url"] = ""
                        response.data["book_faculty_resources"][res_id]["link_external"] = ""

        return response

    def detail_view(self, request, pk):

        response = super().detail_view(request, pk)
        page = Page.objects.get(pk=pk)

        # Implementing Caching
        response['Cache-Control'] = 'max-age=290304000, public'
        response['Last-Modified'] = page.last_published_at

        # Implementing User Authentication
        auth_user = json.loads(get_user_data(request).content.decode())

        # Fetching User Information and Overwriting auth_user
        if "user_id" in auth_user:
            auth_user = get_user_info(auth_user["user_id"])

        # Overwriting the Response if ox credential does not
        # authorize faculty access.
        if "book_faculty_resources" in response.data:
            if "faculty_status" not in auth_user or auth_user["faculty_status"] != "confirmed_faculty":
                for res_id in range(len(response.data["book_faculty_resources"])):
                    if not response.data["book_faculty_resources"][res_id]["resource_unlocked"]:
                        response.data["book_faculty_resources"][res_id]["link_document_url"] = ""
                        response.data["book_faculty_resources"][res_id]["link_external"] = ""

        return response


# Add the three endpoints using the "register_endpoint" method.
# The first parameter is the name of the endpoint (eg. pages, images). This
# is used in the URL of the endpoint
# The second parameter is the endpoint class that handles the requests
api_router.register_endpoint('pages', CachedPagesAPIEndpoint)
api_router.register_endpoint('images', ImagesAPIEndpoint)
api_router.register_endpoint('documents', DocumentsAPIEndpoint)