from exceptions import ValueError
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseRedirect
from django.views.decorators.http import require_http_methods, require_safe
from django.contrib import auth
from django.core.urlresolvers import reverse
from django.contrib.auth import get_user_model
from django.contrib import messages
from django import forms
from main.helpers import init_context
from items.helpers import item_search_to_json

import logging
logger = logging.getLogger(__name__)


@require_safe
def index(request):
    c = init_context('users')
    c['userlist'] = list(get_user_model().objects.filter(is_active=True).order_by('name'))
    return render(request, 'users/index.html', c)


class LoginForm(forms.Form):
    username = forms.CharField(max_length=30)
    password = forms.CharField(widget=forms.PasswordInput, required=False)
    nexturl  = forms.CharField(widget=forms.HiddenInput, required=False)


@require_http_methods(["GET", "POST"])
def login(request):
    c = init_context('users')
    if request.user.is_authenticated():
        return HttpResponseRedirect(reverse('users.views.profile', args=[request.user.id]))
    if request.method == 'GET':
        form = LoginForm(initial={'nexturl': request.GET.get('next', '')})
    else:
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            if username.find('@') >= 0:
                q = get_user_model().objects.filter(email=username)
                if len(q) == 1:
                    username = q[0].pk
            try:
                user = auth.authenticate(username=username, password=password)
            except ValueError:
                user = None
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
    c = init_context('users')
    pageuser = get_object_or_404(get_user_model(), pk=user_id)
    own_profile = request.user == pageuser
    c['pageuser'] = pageuser
    c['init_items'] = item_search_to_json(itemtype='D', user=pageuser)
    c['user_id'] = user_id
    c['enable_drafts'] = own_profile
    c['own_profile'] = own_profile
    return render(request, 'users/profile.html', c)
