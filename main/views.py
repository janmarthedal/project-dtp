from django.shortcuts import render
from django.views.decorators.http import require_safe
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.conf import settings
from main.helpers import init_context

@require_safe
def index(request):
    if not settings.DEBUG:
        return HttpResponseRedirect(reverse('main.views.signup'))
    return home(request)

@require_safe
def home(request):
    c = init_context('home') 
    return render(request, 'home.html', c)

@require_safe
def about(request):
    c = init_context('about') 
    return render(request, 'about.html', c)

@require_safe
def signup(request):
    return render(request, 'signup.html')