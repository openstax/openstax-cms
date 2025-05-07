"""
OpenStax Accounts settings for OpenStax CMS.

This module contains settings related to OpenStax Accounts integration.
"""

import os

# Base URL for accounts
BASE_URL = os.getenv('BASE_URL', 'https://openstax.org')

# OpenStax Accounts settings
ACCOUNTS_URL = os.getenv('ACCOUNTS_DOMAIN', f'{BASE_URL}/accounts')
AUTHORIZATION_URL = os.getenv('ACCOUNTS_AUTHORIZATION_URL', f'{ACCOUNTS_URL}/oauth/authorize')
ACCESS_TOKEN_URL = os.getenv('ACCOUNTS_ACCESS_TOKEN_URL', f'{ACCOUNTS_URL}/oauth/token')
USER_QUERY = os.getenv('ACCOUNTS_USER_QUERY', f'{ACCOUNTS_URL}/api/user?')
USERS_QUERY = os.getenv('ACCOUNTS_USERS_QUERY', f'{ACCOUNTS_URL}/api/users?')

# Social auth settings
SOCIAL_AUTH_OPENSTAX_KEY = os.getenv('SOCIAL_AUTH_OPENSTAX_KEY')
SOCIAL_AUTH_OPENSTAX_SECRET = os.getenv('SOCIAL_AUTH_OPENSTAX_SECRET')
SOCIAL_AUTH_LOGIN_REDIRECT_URL = os.getenv('SOCIAL_AUTH_LOGIN_REDIRECT_URL', BASE_URL)
SOCIAL_AUTH_SANITIZE_REDIRECTS = os.getenv('SOCIAL_AUTH_SANITIZE_REDIRECTS') == 'True'

# SSO settings
SSO_COOKIE_NAME = os.getenv('SSO_COOKIE_NAME', 'oxa')
SIGNATURE_PUBLIC_KEY = os.getenv('SSO_SIGNATURE_PUBLIC_KEY',
                                 "-----BEGIN PUBLIC KEY-----\
                                 MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQDjvO/E8lO+ZJ7JMglbJyiF5/Ae\
                                 IIS2NKbIAMLBMPVBQY7mSqo6j/yxdVNKZCzYAMDWc/VvEfXQQJ2ipIUuDvO+SOwz\
                                 MewQ70hC71hC4s3dmOSLnixDJlnsVpcnKPEFXloObk/fcpK2Vw27e+yY+kIFmV2X\
                                 zrvTnmm9UJERp6tVTQIDAQAB\
                                 -----END PUBLIC KEY-----")
ENCRYPTION_PRIVATE_KEY = os.getenv('SSO_ENCRYPTION_PRIVATE_KEY', "c6d9b8683fddce8f2a39ac0565cf18ee") 