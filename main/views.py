from django.contrib.auth import logout as auth_logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from social.apps.django_app.context_processors import backends as auth_backends

import logging
logger = logging.getLogger(__name__)

def home(request):
    return render(request, 'main/home.html')

def login(request):
    context = {'title': 'Sign In'}
    return render(request, 'main/login.html', context)

@login_required
def profile(request):
    next = request.GET.get('next')
    if next:
        return redirect(next)
    context = {'title': 'Profile'}
    backends = auth_backends(request)['backends']
    logger.info('User {} has providers: {}'.format(request.user.username,
        ', '.join(p.provider for p in backends['associated'])))
    return render(request, 'main/profile.html', context)

def logout(request):
    auth_logout(request)
    return redirect('home')
