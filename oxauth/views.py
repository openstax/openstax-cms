import urllib.parse
from django.shortcuts import redirect
from django.http import request, HttpResponse
from django.conf import settings
from django.contrib.auth import login as auth_login
from django.contrib.auth import logout as auth_logout
from django.contrib.auth.models import User, Permission
from django.urls import reverse
from .functions import decrypt_cookie
from .models import OpenStaxUserProfile

def create_sso_profile(decrypted_cookie):
    user, _ = User.objects.get_or_create(
        username=decrypted_cookie['name'].replace(" ", ""),
        first_name=decrypted_cookie['first_name'],
        last_name=decrypted_cookie['last_name']
    )
    openstax_user, _ = OpenStaxUserProfile.objects.get_or_create(
        openstax_accounts_id=decrypted_cookie['id'],
        openstax_accounts_uuid=decrypted_cookie['uuid'],
        defaults={'user': user}
    )
    openstax_user.save()

    # Assign/remove admin permissions if they are an admin in the Accounts admin SSO cookie
    if decrypted_cookie['is_administrator'] == True:
        user.is_superuser = True
        user.is_staff = True
        permission = Permission.objects.get(codename='access_admin')
        user.user_permissions.add(permission)
        user.save()
    elif decrypted_cookie['is_administrator'] == False:  # to handle when no longer an admin in accounts
        user.is_superuser = False
        user.is_staff = False
        permission = Permission.objects.get(codename='access_admin')
        user.user_permissions.remove(permission)
        user.save()

    return user

def login(request):
    try:
        decrypted_cookie = decrypt_cookie(request.COOKIES.get(settings.SSO_COOKIE_NAME)).payload_dict['sub']
        user = create_sso_profile(decrypted_cookie)
    except AttributeError:
        next = request.GET.get("next", None)
        return redirect(settings.ACCOUNTS_URL + '/login/?r={}'.format(urllib.parse.quote(next)))

    # we only authenticate admins for the CMS, so everyone else gets a 401
    if user is not None and user.is_superuser:
        auth_login(request, user, 'oxauth.backend.OpenStaxAccountsBackend')
        return redirect(reverse('wagtailadmin_explore_root'))
    else:
        return HttpResponse('Unauthorized', status=401)


def logout(request):
    url = settings.ACCOUNTS_URL + '/logout/'

    next = request.GET.get("next", None)
    if next:
        url = settings.ACCOUNTS_URL + "/logout/?r={}".format(urllib.parse.quote(next))

    auth_logout(request)

    return redirect(url)
