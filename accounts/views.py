from django.shortcuts import redirect
from django.contrib.auth import logout as auth_logout

def logout(request):
    """Logs out user redirects if in request"""
    next = request.GET.get('next', '')

    auth_logout(request)

    if next:
        return redirect(next)
    else:
        return redirect('/')
