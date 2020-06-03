from django.conf import settings
from django.conf.urls import include, url
from django.urls import path, re_path
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

admin.site.site_header = 'OpenStax'

urlpatterns = [
    # django admin/auth urls
    re_path(r'^django-admin/login/?', RedirectView.as_view(url='/admin/login')),
    re_path(r'^django-admin/?', admin.site.urls),
    re_path(r'^admin/?', include(wagtailadmin_urls)),
    re_path(r'^django-admin/error/?', throw_error, name='throw_error'),

    re_path(r'^oxauth/?', include('oxauth.urls')), # new auth package
    re_path(r'^documents/?', include(wagtaildocs_urls)),
    re_path(r'^images/([^/]*)/(\d*)/([^/]*)/[^/]*$/?', ServeView.as_view(action='redirect'), name='wagtailimages_serve'),
    re_path(r'^accounts/?', include(accounts_urls)), # non-CloudFront Accounts redirects
    re_path(r'^errata/?', include('errata.urls')),

    #api urls
    re_path(r'^apps/cms/api/mail', include('mail.urls')),
    re_path(r'^apps/cms/api/?', include(api_urls)),
    re_path(r'^apps/cms/api/search/$', search, name='search'),
    re_path(r'^apps/cms/api/v2/?', api_router.urls),
    re_path(r'^apps/cms/api/salesforce/?', include('salesforce.urls')),
    re_path(r'^apps/cms/api/snippets/?', include('snippets.urls')),
    re_path(r'^apps/cms/api/books/?', include('books.urls')),
    re_path(r'^apps/cms/api/?', include('news.urls')),
    re_path(r'^blog-feed/rss/$', RssBlogFeed()),
    re_path(r'^blog-feed/atom/$', AtomBlogFeed()),
    re_path(r'^apps/cms/api/errata/?', include('errata.urls')),
    re_path(r'^apps/cms/api/events/?', include('events.urls')),
    re_path(r'^apps/cms/api/?', include('webinars.urls')),
    re_path(r'^apps/cms/api/spike/?', include(wagtail_urls)),

    # everything else to wagtail serve mechanism
    path(r'', include(wagtail_urls)),
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
