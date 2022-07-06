from django.contrib.auth.backends import BaseBackend
from django.conf import settings
from .functions import decrypt_cookie
from .models import OpenStaxUserProfile
from django.contrib.auth.models import User

class OpenStaxAccountsBackend(BaseBackend):
    def authenticate(self, request):
        decrypted_cookie = decrypt_cookie(request.COOKIES.get(settings.SSO_COOKIE_NAME)).payload_dict['sub']

        openstax_user = OpenStaxUserProfile.objects.get(openstax_accounts_uuid=decrypted_cookie['uuid'])
        return openstax_user.user

    def get_user(self, user_id):
        return User.objects.get(pk=user_id)

    def has_perm(self, user_obj, perm, obj=None):
        return user_obj.is_superuser == True
