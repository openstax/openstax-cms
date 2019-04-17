from wagtail.api.v2.endpoints import PagesAPIEndpoint
from wagtail.api.v2.router import WagtailAPIRouter
from wagtail.images.api.v2.endpoints import ImagesAPIEndpoint
from wagtail.documents.api.v2.endpoints import DocumentsAPIEndpoint
from wagtail.core.models import Page

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
    def detail_view(self, request, pk):
        response = super().detail_view(request, pk)
        response['Cache-Control'] = 'max-age=290304000, public'

        page = Page.objects.get(pk=pk)
        response['Last-Modified'] = page.last_published_at

        return response


# Add the three endpoints using the "register_endpoint" method.
# The first parameter is the name of the endpoint (eg. pages, images). This
# is used in the URL of the endpoint
# The second parameter is the endpoint class that handles the requests
api_router.register_endpoint('pages', CachedPagesAPIEndpoint)
api_router.register_endpoint('images', ImagesAPIEndpoint)
api_router.register_endpoint('documents', DocumentsAPIEndpoint)