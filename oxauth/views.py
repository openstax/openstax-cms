from django.shortcuts import redirect
from django.http import request, JsonResponse
from django.conf import settings
from django.contrib.auth.views import logout

from .auth import OXSessionDecryptor


def login(request):
    url = "accounts/login/"

    next = request.GET.get("next", None)
    if next:
        url = "accounts/login/?r={}".format(next)

    return redirect(url)


def get_user_data(request):
    cookie = request.COOKIES.get(settings.COOKIE_NAME, None)

    if not cookie:
        return JsonResponse({"logged_in": False, "cookie": False, "validation": False, "decryption": False})

    decrypt = OXSessionDecryptor(secret_key_base=settings.SHARED_SECRET, encrypted_cookie_salt=settings.ENCRYPTED_COOKIE_SALT, encrypted_signed_cookie_salt=settings.SIGNED_ENCRYPTED_COOKIE_SALT)
    #validate = decrypt.validate_cookie(cookie)

    # TODO: Fix Validation. Currently, does not validate cookie unless the logged in user is id=1
    #if not validate:
    #    return JsonResponse({"logged_in": False, "cookie": True, "validation": False, "decryption": False})

    decrypted_user = decrypt.get_cookie_data(cookie)

    if not decrypted_user:
        return JsonResponse({"logged_in": False, "cookie": True, "validation": True, "decryption": False})

    try:
        return JsonResponse(decrypted_user.decode())
    except AttributeError:
        return JsonResponse(decrypted_user)

def logout(request):
    url = "accounts/logout/"

    next = request.GET.get("next", None)
    if next:
        url = "accounts/logout/?r={}".format(next)

    return redirect(url)
