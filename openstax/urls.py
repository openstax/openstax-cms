from django.conf import settings
from django.urls import include, path, re_path
from django.conf.urls.static import static
from django.contrib import admin
from wagtail.admin import urls as wagtailadmin_urls
from wagtailautocomplete.urls.admin import urlpatterns as autocomplete_admin_urls
from wagtail import urls as wagtail_urls
from wagtail.documents import urls as wagtaildocs_urls
from accounts import urls as accounts_urls

from .api import api_router
from news.search import search
from news.feeds import RssBlogFeed, AtomBlogFeed

from api import urls as api_urls
from global_settings.views import throw_error, clear_entire_cache, sitemap, robots

from pages.flex_api import FlexPageDraftView
from pages.views import HeadlessUserbarView

admin.site.site_header = 'OpenStax'

urlpatterns = [
    path('admin/autocomplete/', include(autocomplete_admin_urls)),
    path('admin/', include(wagtailadmin_urls)),

    path('django-admin/error/', throw_error, name='throw_error'),
    path('django-admin/clear_cache/', clear_entire_cache, name='clear_entire_cache'),
    path('django-admin/', admin.site.urls),

    path('documents/', include(wagtaildocs_urls)),

    re_path(r'^accounts', include(accounts_urls)),  # non-CloudFront Accounts redirects

    # Headless userbar endpoint: the decoupled front-end fetches this while
    # previewing a draft so the accessibility/content checker, content metrics,
    # and wagtail-ai's content checks work on the front-end. Must live under
    # /apps/cms/api/ — that's the only /apps/cms/ path the production nginx
    # routes to this backend (everything else is proxied to the front-end).
    # Declared before the apps/cms/api/ include so the include doesn't swallow it.
    path('apps/cms/api/userbar/', HeadlessUserbarView.as_view(), name='wagtail_userbar'),

    # TEMPORARY: the dedicated apps/cms/api/userbar/* CloudFront behavior (cookies
    # forwarded, no cache) isn't deployed yet, so apps/cms/api/* still strips the
    # session cookie and the userbar comes back blank. The existing (now-unused)
    # apps/cms/api/salesforce/reviews/* behavior already forwards cookies + skips
    # caching, so we ride it to test end-to-end. Declared before the salesforce
    # include so it isn't swallowed. REMOVE once the CloudFront change ships.
    path('apps/cms/api/salesforce/reviews/userbar/', HeadlessUserbarView.as_view(), name='wagtail_userbar_temp'),

    path('apps/cms/api/', include(api_urls)),
    path('apps/cms/api/search/', search, name='search'),
    path('apps/cms/api/v2/pages/flex/', FlexPageDraftView.as_view(), name='flex-draft-create'),
    path('apps/cms/api/v2/pages/flex/<int:page_id>/', FlexPageDraftView.as_view(), name='flex-draft-update'),
    path('apps/cms/api/v2/', api_router.urls),
    path('apps/cms/api/salesforce/', include('salesforce.urls')),
    path('apps/cms/api/snippets/', include('snippets.urls')),
    path('apps/cms/api/books', include('books.urls')),
    path('apps/cms/api/', include('news.urls')),
    path('blog-feed/rss/', RssBlogFeed()),
    path('blog-feed/atom/', AtomBlogFeed()),
    path('errata/', include('errata.urls')),
    path('apps/cms/api/errata/', include('errata.urls')),
    path('apps/cms/api/webinars/', include('webinars.urls')),
    path('apps/cms/api/donations/', include('donations.urls')),
    path('apps/cms/api/oxmenus/', include('oxmenus.urls')),

    # route everything to /api/spike also...
    path('apps/cms/api/spike/', include(wagtail_urls)),
    path('sitemap.xml', sitemap),
    path('robots.txt', robots),

    # For anything not caught by a more specific rule above, hand over to Wagtail's serving mechanism
    path('', include(wagtail_urls)),
]

if settings.DEBUG:
    from django.contrib.staticfiles.urls import staticfiles_urlpatterns
    from django.views.generic.base import RedirectView

    urlpatterns += staticfiles_urlpatterns()
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += [
        path('favicon.ico', RedirectView.as_view(url=settings.STATIC_URL + 'pages/images/favicon.ico')),
    ]

# debug_toolbar is a dev-only dependency; only wire it up when it's actually installed
# (DEBUG is also True under test settings, where debug_toolbar is not in INSTALLED_APPS)
if settings.DEBUG and 'debug_toolbar' in settings.INSTALLED_APPS:
    urlpatterns += [
        path('__debug__/', include('debug_toolbar.urls'))
    ]
