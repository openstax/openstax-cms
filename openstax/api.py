from wagtail.api.v2.views import PagesAPIViewSet
from wagtail.images.api.v2.views import ImagesAPIViewSet
from wagtail.documents.api.v2.views import DocumentsAPIViewSet
from wagtail.api.v2.router import WagtailAPIRouter
#from wagtail.core.models import Page
from wagtail.admin.api.views import PagesAdminAPIViewSet

# # Create the router. "wagtailapi" is the URL namespace
api_router = WagtailAPIRouter('wagtailapi')
admin_api = WagtailAPIRouter('wagtailadmin_api_v1')


# Add the three endpoints using the "register_endpoint" method.
# The first parameter is the name of the endpoint (eg. pages, images). This
# is used in the URL of the endpoint
# The second parameter is the endpoint class that handles the requests
admin_api.register_endpoint('pages', PagesAdminAPIViewSet)
api_router.register_endpoint('pages', PagesAPIViewSet)
api_router.register_endpoint('images', ImagesAPIViewSet)
api_router.register_endpoint('documents', DocumentsAPIViewSet)