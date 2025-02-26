from django.conf import settings
from django.urls import include, path, re_path
from django.conf.urls.static import static
from django.contrib import admin
from wagtail.admin import urls as wagtailadmin_urls
from wagtail import urls as wagtail_urls
from wagtail.documents import urls as wagtaildocs_urls
from accounts import urls as accounts_urls

from .api import api_router
from news.search import search
from news.feeds import RssBlogFeed, AtomBlogFeed

from api import urls as api_urls
from global_settings.views import throw_error, clear_entire_cache, sitemap

admin.site.site_header = 'OpenStax'

urlpatterns = [
    path('admin/', include(wagtailadmin_urls)),

    path('django-admin/error/', throw_error, name='throw_error'),
    path('django-admin/clear_cache/', clear_entire_cache, name='clear_entire_cache'),
    path('django-admin/', admin.site.urls),

    path('documents/', include(wagtaildocs_urls)),

    re_path(r'^accounts', include(accounts_urls)),  # non-CloudFront Accounts redirects

    path('apps/cms/api/', include(api_urls)),
    path('apps/cms/api/search/', search, name='search'),
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
        path('__debug__/', include('debug_toolbar.urls'))
    ]
