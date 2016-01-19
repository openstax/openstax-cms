import json
from django.conf import settings

from django.shortcuts import redirect,render
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout as auth_logout, login

from social.backends.utils import load_backends

from django.views.decorators.csrf import csrf_protect


def logout(request):
    """Logs out user"""
    auth_logout(request)
    if settings.APP_LOGOUT_URL:
        return redirect(settings.APP_LOGOUT_URL)    
    return redirect('login')

@csrf_protect
def oauth(request):
    """A csrf protected view to gather login information
    and direct user to the link that begins the oauth procedure.
    """
    return redirect('/accounts/login/openstax')


def login(request):
    """Displays login mechanism""" 
    if settings.APP_LOGIN_URL:
        return redirect(settings.APP_LOGIN_URL)

    if request.user.is_authenticated():
        return redirect('done')
    return render(request,'login.html')

def home(request):
    """Home view for this app, redirects to login view"""
    if settings.APP_LOGIN_URL:
        return redirect(settings.APP_LOGIN_URL)
    return redirect('login')

@login_required
def done(request):
    """Login complete, direct user to profile view."""
    return redirect('profile')

@login_required
def profile(request):
    """displays user data"""
    if settings.APP_PROFILE_URL:
        return redirect(settings.APP_PROFILE_URL)
    return render(request,'profile.html')
