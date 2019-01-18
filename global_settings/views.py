from django.http import HttpResponseServerError

def throw_error(request):
        # Return an "Internal Server Error" 500 response code.
        return HttpResponseServerError()