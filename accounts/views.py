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
    if settings.ACC_APP_LOGOUT_URL:
        return redirect(settings.ACC_APP_LOGOUT_URL)    
    return redirect('login')

@csrf_protect
def auth(request):
    """A csrf protected view to gather request info 
    for authorization procedure.
    """
    # Begin OAuth2 procedure
    return redirect('/accounts/login/openstax')


def login(request):
    """Displays login mechanism""" 
    if settings.ACC_APP_LOGIN_URL:
        return redirect(settings.ACC_APP_LOGIN_URL)

    if request.user.is_authenticated():
        return redirect('done')
    return render(request,'login.html')

def home(request):
    """Home view for this app, redirects to login view"""
    if settings.ACC_APP_LOGIN_URL:
        return redirect(settings.ACC_APP_LOGIN_URL)
    return redirect('login')

@login_required
def done(request):
    """Login complete, direct user to profile view."""
    return redirect('profile')

@login_required
def profile(request):
    """displays user data"""
    if settings.ACC_APP_PROFILE_URL:
        return redirect(settings.ACC_APP_PROFILE_URL)
    return render(request,'profile.html')
