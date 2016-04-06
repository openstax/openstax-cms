from django.shortcuts import redirect
from django.contrib.auth import logout as auth_logout
from django.conf import settings


def logout(request):
    """Logs out user redirects if in request"""
    next = request.GET.get('next', '')
    auth_logout(request)

    if next:
        return redirect('{}/?next={}'.format(settings.OPENSTAX_ACCOUNTS_LOGOUT_URL, next))
    else:
        return redirect(settings.OPENSTAX_ACCOUNTS_LOGOUT_URL)
