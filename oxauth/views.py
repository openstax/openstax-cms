from django.shortcuts import redirect
from django.http import request, JsonResponse
from django.conf import settings
from django.contrib.auth.views import logout

from .auth import OXSessionDecryptor
from .models import AuthSettings


def login(request):
    url = "{}login/".format(settings.ACCOUNTS_SERVER_URL)

    next = request.GET.get("next", None)
    if next:
        url = "{}login/?r={}".format(settings.ACCOUNTS_SERVER_URL, next)

    return redirect(url)


def get_user_data(request):
    auth_settings = AuthSettings.objects.latest('id')

    cookie = request.COOKIES.get(auth_settings.cookie_name, None)

    if not cookie:
        return JsonResponse({"logged_in": False, "cookie": False, "validation": False, "decryption": False})

    decrypt = OXSessionDecryptor(secret_key_base=auth_settings.secret_base_key, encrypted_cookie_salt=auth_settings.encrypted_salt, encrypted_signed_cookie_salt=auth_settings.signed_encrypted_salt)
    validate = decrypt.validate_cookie(cookie)

    if not validate:
        return JsonResponse({"logged_in": False, "cookie": True, "validation": False, "decryption": False})
    
    decrypted_user = decrypt.get_cookie_data(cookie)

    if not decrypted_user:
        return JsonResponse({"logged_in": False, "cookie": True, "validation": True, "decryption": False})

    try:
        return JsonResponse(decrypted_user.decode())
    except AttributeError:
        return JsonResponse(decrypted_user)

def logout(request):
    url = "{}logout/".format(settings.ACCOUNTS_SERVER_URL)

    next = request.GET.get("next", None)
    if next:
        url = "{}logout/?r={}".format(settings.ACCOUNTS_SERVER_URL, next)

    return redirect(url)
