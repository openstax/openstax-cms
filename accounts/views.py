from django.shortcuts import redirect
from django.contrib.auth import logout as auth_logout
from django.conf import settings


def logout(request):
    """Logs out user redirects if in request"""
    redirect = request.GET.get('r', '')
    auth_logout(request)

    response = None

    if redirect:
        response = redirect('{}/?r={}'.format(settings.OPENSTAX_ACCOUNTS_LOGOUT_URL, redirect))
    else:
        response = redirect(settings.OPENSTAX_ACCOUNTS_LOGOUT_URL)

    response.delete_cookie('_accounts_session')
    return response
