from django.shortcuts import redirect
from django.contrib.auth import logout as auth_logout
from django.conf import settings


def logout(request):
    auth_logout(request)
    return redirect(settings.OPENSTAX_ACCOUNTS_LOGOUT_URL)


def post_logout(request):
    host = request.get_host()
    next = request.GET.get('next', '')

    # if next param and host matches next location, redirect to it
    # this should allow for relative or full urls in the next param
    if next:
        if host in next:
            return redirect(next)
        else:
            return redirect('/')
    else:
        return redirect('/')
