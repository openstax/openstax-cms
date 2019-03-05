from django.shortcuts import redirect
from django.http import request, JsonResponse
from django.conf import settings

from .auth import OXSessionDecryptor

def login(request):
    url = "{}login/".format(settings.ACCOUNTS_SERVER_URL)

    next = request.GET.get('next', None)
    if next:
        url = "{}login/?r={}".format(settings.ACCOUNTS_SERVER_URL, next)

    print(request.COOKIES)

    print(url)
    return redirect(url)


def get_user_data(request):
    cookie = request.COOKIES.get(settings.COOKIE_NAME, None)
    if not cookie:
        return JsonResponse({'logged_in': False})

    decrypt = OXSessionDecryptor(secret_key_base=settings.SHARED_SECRET)
    decrypted_user = decrypt.get_cookie_data(cookie)
    return JsonResponse(decrypted_user)
