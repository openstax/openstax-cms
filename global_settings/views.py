import inspect
from django.contrib.sitemaps import views as sitemap_views
from django.http import HttpResponseServerError, HttpResponse
from wagtail.contrib.sitemaps.sitemap_generator import Sitemap
from global_settings.functions import invalidate_cloudfront_caches


def throw_error(request):
        # Return an "Internal Server Error" 500 response code.
        return HttpResponseServerError()


def clear_entire_cache(request):
        # clear all contents from the Cloudfront cache
        invalidate_cloudfront_caches()
        response = '<html><body><p>All Caches Invalidated</p></body></html>'
        return HttpResponse(response)


def index(request, sitemaps, **kwargs):
    sitemaps = prepare_sitemaps(request, sitemaps)
    return sitemap_views.index(request, sitemaps, **kwargs)


def sitemap(request, sitemaps=None, **kwargs):
    if sitemaps:
        sitemaps = prepare_sitemaps(request, sitemaps)
    else:
        sitemaps = {"wagtail": Sitemap(request)}
    return sitemap_views.sitemap(request, sitemaps, **kwargs)


def prepare_sitemaps(request, sitemaps):
    initialised_sitemaps = {}
    for name, sitemap_cls in sitemaps.items():
        if inspect.isclass(sitemap_cls) and issubclass(sitemap_cls, Sitemap):
            sitemap_instance = sitemap_cls(request)
            sitemap_instance.sitemap_urls = [url.rstrip('/') for url in sitemap_instance.sitemap_urls]
            initialised_sitemaps[name] = sitemap_instance
        else:
            initialised_sitemaps[name] = sitemap_cls
    return initialised_sitemaps
