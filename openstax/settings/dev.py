from .base import *

DEBUG = True

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# BASE_URL required for notification emails
BASE_URL = 'http://localhost:8000'

try:
    from .local import *
except ImportError:
    pass

##################################
#   OVERRIDE ACCOUNTS SETTINGS   #
##################################

# use default loging and logout urls,
# Needed for selenium test.
ACC_APP_LOGIN_URL = None
ACC_APP_LOGOUT_URL = None
ACC_APP_PROFILE_URL = None
