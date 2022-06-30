from django.http import HttpResponseServerError

from global_settings.functions import invalidate_cloudfront_caches


def throw_error(request):
        # Return an "Internal Server Error" 500 response code.
        return HttpResponseServerError()


def clear_entire_cache(request):
        # clear all contents from the Cloudfront cache
        return invalidate_cloudfront_caches()
