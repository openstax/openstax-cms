from django.urls import resolve, Resolver404
from django.core.handlers.base import BaseHandler
from django.test.client import RequestFactory
from django.http.response import HttpResponsePermanentRedirect
from django.contrib.auth import login as auth_login
from django.contrib.auth.models import User
from oxauth.functions import decrypt_cookie
from oxauth.views import create_sso_profile

def assertPathDoesNotRedirectToTrailingSlash(test, path):
    try:
        resolve(path)
    except Resolver404:
        test.fail('The path {} cannot be found'.format(path))

    response = test.client.get(path)

    if (isinstance(response, HttpResponsePermanentRedirect)):
       test.assertNotEqual(response.url, path + "/")

def mock_user_login():
    cookie = 'eyJhbGciOiJkaXIiLCJlbmMiOiJBMjU2R0NNIn0..mktqRLloaCze0VeT.0WU9d20PI1Iu6zajuQMiIJ5GQJVy0DQ1H3BINxkYIS56f1X6p_mesuujHphLcukQny6q0_rmvZUkKLEyojpo14p3czXXu0GF2EWtxprPmfOnPdAig0GXCBJxYVbxKIuZdR4FYodIZaDuDUjXC_hJohHuVoiTQW7jJEGIFj8m9dgAqP-3hOnqaO0C0OvKWoXi0sLb3CvTraT2AGRgj69jkg4B-2y1sUZn_yZO6o2HekGlxzhnKT7ILEAl7cd68W6LmmN0vk4V4nNFkcg0XQ3i1MzWLZroGSjD_9HrhALdHcofBC39UClOzxnbpynFlZk0gr7m0_MmCUFqWKSL8G0eRT9sgOIW6THsl0jpT4KyUFREVdGkTWxaS2qYRqZEQBk9wZlAHuHkE8s6UNZNYhvU5RJkGC1m4faHnM_umTEFQq5aBvRe7gq_8OtOGASXtmFggapuUSfxWX8Bxh8IgA4BT_DuxQbC4biO7FauOT0glZ0Dk4ZXIjbhxBnedtjmeH02xa4RpcKOSOv4UMy1ajCc4KLp9K5drQTKs1PeShAUg1aN58ZwgQq1w4MdjXHkMqnJFiFWt9abF3WYG2EywhTogxIcgq6IrrAIzW4NSptnQVAcxTPxp7hb3OT1mY9dcK138h0GtBR6Z562VbDRaSwplXCLvwcqKoGJyhotcl2m78ESmu1kIO_AJVstlaZprEA0Ji0A7uJlL03JAeTvlJptcouFGax8LGlxq9Ekpz_zifUxLR52MJ8otKcapsZvmtOpc8A70p7V-ceinzKdL5Jq_zA0teJ1Qk2gjMJ7IdeyG3VZ0QIFOQ_FffGkbdW1Ow-nHFHLVfHbkyEF65HIGHEN_RqL0OKUa1HcPlmL5c1S4w5zgdA-2ZAda6ASnY1clwGufFek5AwMp5SAUmdNUBYIDdQm6hbzn0Xe2VB5Y-jqKBOq4yk-M4rmwAf-tD5NJiKaYLZwT-Zst2eG8InRUOmQt6lBJtGNIYnk_a__rX8rfJpvKIJ-Ws8b9fHvSjzSQOroqM3KmfLrevucaJA7jM7CydgOOnt3VQGXKnYqgnhD6jii0zjR3sGAJHF24tQIVtoFCQGBJZly_MQL2Y-EeLqz64Z7AZDptM9oXK035cbvMMuzG9b1jH3XE2o3gO5ekixDpMwTKT8uI1wH9gOqbf9ehirExYgxEh-EVXTlT6t-kk4N-tu83zCLi8MZNTAVqlisakFlnkn4o53Bj5nn9bRQT61HJG_cLxs.Sz3rB-YyqatRUpekkxpyfw'
    decrypted_cookie = decrypt_cookie(cookie).payload_dict['sub']

    user = create_sso_profile(decrypted_cookie)
    return user

class RequestMock(RequestFactory):
    def request(self, **request):
        "Construct a generic request object."
        request = RequestFactory.request(self, **request)
        handler = BaseHandler()
        handler.load_middleware()
        for middleware_method in handler._request_middleware:
            if middleware_method(request):
                raise Exception("Couldn't create request mock object - request middleware returned a response")
        return request
