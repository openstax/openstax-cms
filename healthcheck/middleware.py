# https://stackoverflow.com/a/64623669
from django.http import HttpResponse

class HealthCheckMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.path in ['/ping', '/ping/']:
            return HttpResponse(status=204)
        return self.get_response(request)
