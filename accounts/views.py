from django.shortcuts import redirect
from django.contrib.auth import logout as auth_logout
from django.conf import settings


def logout(request):
    """Logs out user redirects if in request"""
    next = request.GET.get('next', '')
    auth_logout(request)

    response = None

    if next:
        response = redirect('{}/?next={}'.format(settings.OPENSTAX_ACCOUNTS_LOGOUT_URL, next))
    else:
        response = redirect(settings.OPENSTAX_ACCOUNTS_LOGOUT_URL)

    response.delete_cookie('_accounts_session')
    return response
