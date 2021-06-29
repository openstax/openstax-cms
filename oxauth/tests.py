import json
from urllib.parse import urlencode
from urllib.request import urlopen

from django.test import TestCase, Client
from django.conf import settings
from django.urls import reverse

from shared.test_utilities import RequestMock
from oxauth.functions import get_token, decrypt_cookie, get_logged_in_user_id
from oxauth.views import login, logout
from .auth import OXSessionDecryptor


class AccountsTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.sso_cookie = "eyJhbGciOiJkaXIiLCJlbmMiOiJBMjU2R0NNIn0..nPz-NXrgnVh9SyFJ.zQD5yD7RHQMNxJF1rpALVPlcaJv181Cc1ZTK-UUERWp8FM0ChbzfxUwCw3-5LOnHubnF2VJlLRdI3pPoNdcRXoHpnq5cwPX4z6NvTPeDt86r4zZwsgcW9iwrMos5077WEie91y1ruonnjU49BZWA5Ugk0fm82VSFkhGnXvjuDirJuBorZq6-Xp9-YiF5QEksUE_sT7DYTrGzSz_pa0fSlXMYMyslKDLlCuEihFurHTQnoMcA9LM6cZQ6TkAUC10so81wD44HabYz7cD5Q57aYM5GLh2sNrUKL1xBXGdaHipa_YuSc36JObGaZc9BS-t_nPv1aQpGeirLYRSWH06w9YwUEgAtR4fvZ5SbgdGkdxz15yVLyA8HD-BYz8SBflNRw91ZI3HnZbeY9M_Cpk_ejnujfsLyPsXSTa6mr8hKE3z8wtqcP-SodBvW2l75Ydg2MGkSo7_mcLLuXPGU7SqfVuwF1wIs8PV_Zg3ECjXlzeQ9WcTFzU-iF2wVpLZcMLOsy2o3WzJT4cWbWdva4RBp0Vp0JT-Bra6jPxS3TTKQIOHnqKfA4jpF_Szz2xIg_vwWAXQcejjMDpGbggCdvjvQqys1cP4Xb8vcZGfjKVzbYgJ_x4SKJw8LDDn294-HD9gTHroNqXv65Je1mp63M_QaF8hXLWTyIYTTfPema8sEO2HEB70X4UPV3qRICD6bwQi3KD4TveSU_q434n50mbU9W9EOZr2Fsc8jjJNfW0BRT_Z2lluC8aqvAkegS_abWboLdoaGnNNwwQAGaqmMvM3wnKVslPI-ew5s1tRVHs0dQz_T1Q0TOibDYln1h6CcSaeFprwXT8X-PMpYWJWoxWTW7NH8Ak_3lZ9nSGeJOdilLiwXJTsYgvuJDyEnXdHIjs5UgUovj_WxPigNpYn7BZT6feAAjUsKiGe2OEOvnJYhAKVHOQtvUhFUZOE6IiUdToytBaWroSILeLfY9B4JLXz6huXOKYOBWrdX4p1Naul-JHWvruSYsr5ja8ga7zZFgzUH3j82v-Kbfakv33IXNDJGHXGePo_f8AkB4Bw3Rohs1QJe7aTBBqMAUmUBsgboq4AL6_SCC1JQun-ScD9fcH2a1YXRucaplUGLvsThlhOiu1JkSEuhb_GpVFe4HprxOuF_c_0RHM_r0MpwjbkgfS49tqtE2sf05Qo2_iyE-hMl0ehmkyEe21ice1-0ogy7y-6m-STb5xXZzlSwghBhCwXTx8XgKvKDVHWQWw.btBy8lBSW-xKBuJO3geDRA"

    def test_oauth_login_url(self):
        response = self.client.get(reverse('social:begin', args=['openstax']))
        self.assertNotEqual(response.status_code, 404)

    def test_login_redirects(self):
        response = self.client.get(reverse('login'))
        self.assertRedirects(response, "/accounts/login/", fetch_redirect_response=False)

        response = self.client.get(reverse('login') + "?next=foo")
        self.assertRedirects(response, "/accounts/login/?r=foo", fetch_redirect_response=False)

    def test_logout_redirects(self):
        response = self.client.get(reverse('logout'))
        self.assertRedirects(response, "/accounts/logout/", fetch_redirect_response=False)

        response = self.client.get(reverse('logout') + "?next=foo")
        self.assertRedirects(response, "/accounts/logout/?r=foo", fetch_redirect_response=False)

    def test_can_decrypt_sso_cookie(self):
        decrypted_cookie = decrypt_cookie(self.sso_cookie)
        self.assertEqual(decrypted_cookie.user_uuid, '467cea6c-8159-40b1-90f1-e9b0dc26344c')

    def test_can_bypass_cookie_checks(self):
        mock = RequestMock()
        user_id = get_logged_in_user_id(mock.request, bypass_sso_cookie_check=True)
        self.assertEqual(user_id, -1) #bypassed cookie checks return -1 for a user id
