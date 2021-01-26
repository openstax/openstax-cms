import json
from urllib.parse import urlencode
from urllib.request import urlopen
from oauthlib.oauth2 import BackendApplicationClient
from requests_oauthlib import OAuth2Session

from django.conf import settings
from .strategy_2 import Strategy2

def decrypt_cookie(cookie):
    strategy = Strategy2(
        signature_public_key=settings.SIGNATURE_PUBLIC_KEY,
        signature_algorithm = settings.SIGNATURE_ALGORITHM,
        encryption_private_key = settings.ENCRYPTION_PRIVATE_KEY,
        encryption_method = 'A256GCM',
        encryption_algorithm = 'dir'
    )

    payload = strategy.decrypt(cookie)
    return payload

def get_logged_in_user_id(request, bypass_sso_cookie_check=settings.BYPASS_SSO_COOKIE_CHECK):
    """
    This simplifies getting the logged in user id - since this happens often.
    Requires SSO_COOKIE_NAME to be set in settings file.
    Takes an optional bypass_cookie_check param to bypass cookie checking for local dev / testing
    which returns -1 (a never valid user id)
    :param request:
    :return: user_id from SSO cookie
    """
    if not bypass_sso_cookie_check:
        decrypted_cookie = decrypt_cookie(request.COOKIES.get(settings.SSO_COOKIE_NAME))
        if decrypted_cookie:
            return decrypted_cookie.user_id
        else:
            return None
    else:
        return -1

def get_token():
    client = BackendApplicationClient(client_id=settings.SOCIAL_AUTH_OPENSTAX_KEY)
    oauth = OAuth2Session(client=client)
    token = oauth.fetch_token(token_url=settings.ACCESS_TOKEN_URL,
                              client_id=settings.SOCIAL_AUTH_OPENSTAX_KEY,
                              client_secret=settings.SOCIAL_AUTH_OPENSTAX_SECRET)

    return token


def get_user_info(uid=None):
    if uid:
        token = get_token()
        url = settings.USERS_QUERY + urlencode({
            'q': 'id:{}'.format(uid),
            'access_token': token['access_token']
        })

        with urlopen(url) as url:
            data = json.loads(url.read().decode())

            # update email address if possible
            try:
                contact_infos = data['items'][0]['contact_infos']
                most_recent_email = max(contact_infos, key=lambda x: x['id'])
                email = most_recent_email['value']
            except (ValueError, IndexError, KeyError):
                email = None  # no saved emails

            # update full name if possible
            try:
                fullname = data['items'][0]['full_name']
            except (ValueError, IndexError, KeyError):
                fullname = None

            try:
                user_data = {
                    'email': email,
                    'self_reported_role': data['items'][0]['self_reported_role'],
                    'faculty_status': data['items'][0]['faculty_status'],
                    'applications': data['items'][0]['applications'],
                    'fullname': fullname
                }
            except IndexError:
                return False

            return user_data
    else:
        return False
