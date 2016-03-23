from django.shortcuts import redirect
from django.conf import settings

def save_profile( user, *args, **kwargs):
    #for now - setting email address to prevent issues, should update it eventually
    if user:
        user.email = '{}@openstax.org'.format(user.username)
        user.save()

def new_user_redirect(backend, user, response, *args, **kwargs):
    if(kwargs['new_association']):
        return redirect(settings.NEW_USER_REDIRECT)
