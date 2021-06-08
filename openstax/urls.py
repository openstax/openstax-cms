from django.conf import settings
from django.conf.urls import include, url
from django.conf.urls.static import static
from django.contrib import admin
from django.views.generic.base import RedirectView
from wagtail.admin import urls as wagtailadmin_urls
from wagtail.core import urls as wagtail_urls
from wagtail.documents import urls as wagtaildocs_urls
from wagtail.images.views.serve import ServeView
from accounts import urls as accounts_urls

from .api import api_router
from news.search import search
from news.feeds import RssBlogFeed, AtomBlogFeed

from api import urls as api_urls
from global_settings.views import throw_error
from wagtail.contrib.sitemaps.views import sitemap

admin.site.site_header = 'OpenStax'

urlpatterns = [
    url(r'^django-admin/login', RedirectView.as_view(url='/admin/login')),
    url(r'^django-admin/', admin.site.urls),
    url(r'^admin/', include(wagtailadmin_urls)),


    url(r'^django-admin/error/', throw_error, name='throw_error'),

    url(r'^oxauth', include('oxauth.urls')), # new auth package
    url(r'^documents/', include(wagtaildocs_urls)),
    url(r'^images/([^/]*)/(\d*)/([^/]*)/[^/]*$', ServeView.as_view(action='redirect'), name='wagtailimages_serve'),
    url(r'^accounts', include(accounts_urls)), # non-CloudFront Accounts redirects

    url(r'^apps/cms/api/mail', include('mail.urls')),
    url(r'^apps/cms/api/', include(api_urls)),
    url(r'^apps/cms/api/search/$', search, name='search'),
    url(r'^apps/cms/api/v2/', api_router.urls),
    url(r'^apps/cms/api/salesforce/', include('salesforce.urls')),
    url(r'^apps/cms/api/snippets/', include('snippets.urls')),
    url(r'^apps/cms/api/books', include('books.urls')),
    url(r'^apps/cms/api', include('news.urls')),
    url(r'^blog-feed/rss/$', RssBlogFeed()),
    url(r'^blog-feed/atom/$', AtomBlogFeed()),
    url(r'^errata/', include('errata.urls')),
    url(r'^apps/cms/api/errata/', include('errata.urls')),
    url(r'^apps/cms/api/events/', include('events.urls')),
    url(r'^apps/cms/api/', include('webinars.urls')),
    url(r'^apps/cms/api/donations/', include('donations.urls')),

    # route everything to /api/spike also...
    url(r'^apps/cms/api/spike/', include(wagtail_urls)),
    url('^sitemap\.xml$', sitemap),

    # For anything not caught by a more specific rule above, hand over to
    # Wagtail's serving mechanism

    url(r'', include(wagtail_urls)),
]

if settings.DEBUG:
    from django.contrib.staticfiles.urls import staticfiles_urlpatterns
    from django.views.generic.base import RedirectView

    urlpatterns += staticfiles_urlpatterns()
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += [
        url(r'^favicon\.ico$', RedirectView.as_view(
            url=settings.STATIC_URL + 'pages/images/favicon.ico'))
    ]
