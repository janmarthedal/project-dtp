from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseRedirect
from django.views.decorators.http import require_http_methods, require_safe
#from django.contrib.auth.decorators import login_required
from django.contrib import auth
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User
from main.helpers import init_context
from users.helpers import get_user_info

import logging
logger = logging.getLogger(__name__)

@require_http_methods(["GET", "POST"])
def login(request):
    if request.user.is_authenticated():
        return HttpResponseRedirect(reverse('main.views.index'))
    c = {}
    if request.method == 'GET':
        c['next'] = request.GET.get('next', None)
    else:
        username = request.POST['user']
        password = request.POST['pwd']
        user = auth.authenticate(username=username, password=password)
        if user is not None:
            if user.is_active:
                auth.login(request, user)
                next_url = request.POST.get('next', reverse('users.views.profile', args=[request.user.id]))
                return HttpResponseRedirect(next_url)
            else:
                c['error'] = 'Account has been disabled'
        else:
            c['error'] = 'Invalid login and/or password'
        c['next'] = request.POST.get('next', None)
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

