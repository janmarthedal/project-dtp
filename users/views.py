from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseRedirect
from django.views.decorators.http import require_http_methods, require_safe
from django.contrib import auth
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User
from django.contrib import messages
from django import forms
from main.helpers import init_context
from users.helpers import get_user_info

import logging
logger = logging.getLogger(__name__)

class LoginForm(forms.Form):
    username = forms.CharField(max_length=30)
    password = forms.CharField(widget=forms.PasswordInput, required=False)
    nexturl  = forms.CharField(widget=forms.HiddenInput, required=False)

@require_http_methods(["GET", "POST"])
def login(request):
    c = init_context(request)
    if request.user.is_authenticated():
        return HttpResponseRedirect(reverse('users.views.profile', args=[request.user.id]))
    if request.method == 'GET':
        form = LoginForm(initial={'nexturl': request.GET.get('next', '')})
    else:
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = auth.authenticate(username=username, password=password)
            if user is not None:
                if user.is_active:
                    auth.login(request, user)
                    nexturl = request.POST.get('nexturl', reverse('users.views.profile', args=[request.user.id]))
                    return HttpResponseRedirect(nexturl)
                else:
                    messages.info(request, 'Account has been disabled')
            else:
                messages.warning(request, 'Invalid login and/or password')
    c['form'] = form
    return render(request, 'users/login.html', c)

@require_safe
def logout(request):
    auth.logout(request)
    return HttpResponseRedirect(reverse('main.views.index'))

@require_safe
def profile(request, user_id):
    c = init_context(request)
    user = get_object_or_404(User, pk=user_id)
    c['user'] = get_user_info(user)
    c['own_profile'] = c['user'] == c.get('auth')
    return render(request, 'users/profile.html', c)

