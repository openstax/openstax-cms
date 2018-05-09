from django.conf import settings
from django.conf.urls import include, url
from django.conf.urls.static import static
from django.contrib import admin
from wagtail.admin import urls as wagtailadmin_urls
from wagtail.core import urls as wagtail_urls
from wagtail.documents import urls as wagtaildocs_urls
from wagtail.images import urls as wagtailimages_urls
from .api import api_router

from news.search import search
from news.feeds import RssBlogFeed, AtomBlogFeed

from api import urls as api_urls

admin.site.site_header = 'OpenStax'

urlpatterns = [
    url(r'^django-admin/', admin.site.urls),

    url(r'^admin/', include(wagtailadmin_urls)),
    url(r'^accounts/', include('accounts.urls')),
    url(r'^documents/', include(wagtaildocs_urls)),
    url(r'^images/', include(wagtailimages_urls)),

    url(r'^api/mail/', include('mail.urls')),
    url(r'^api/', include(api_urls)),
    url(r'^api/search/$', search, name='search'),
    url(r'^api/v2/', api_router.urls),
    url(r'^api/salesforce/', include('salesforce.urls')),

    url(r'^api/pages/', include('pages.urls')),
    url(r'^api/snippets/', include('snippets.urls')),
    url(r'^api/books/', include('books.urls')),
    url(r'^api/', include('news.urls')),
    url(r'^blog-feed/rss/$', RssBlogFeed()),
    url(r'^blog-feed/atom/$', AtomBlogFeed()),
    url(r'^api/errata/', include('errata.urls')),

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
