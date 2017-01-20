from django.shortcuts import redirect
from django.contrib.auth import logout as auth_logout
from django.conf import settings


def logout(request):
    auth_logout(request)
    return redirect(settings.OPENSTAX_ACCOUNTS_LOGOUT_URL)
