from django.shortcuts import redirect
from django.http import request
from django.conf import settings

def accounts(request):
    # This will not be reached in deployed environments where Cloudfront is serving OSWeb,
    # because Cloudfront proxies all `/accounts*` traffic straight to Accounts.  It is only
    # for test and dev environments.

    url = "{}{}".format(settings.ACCOUNTS_SERVER_URL, request.get_full_path())
    return redirect(url)
