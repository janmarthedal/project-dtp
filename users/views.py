from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from django.contrib import auth
from django.core.urlresolvers import reverse
from main.helpers import init_context

@require_http_methods(["GET", "POST"])
def login(request):
    if request.user.is_authenticated():
        return HttpResponseRedirect(reverse('main.views.index'))
    c = {}
    if request.method == 'GET':
        c['next'] = request.GET.get('next', reverse('users.views.account'))
    else:
        username = request.POST['user']
        password = request.POST['pwd']
        c['next'] = request.POST['next']
        user = auth.authenticate(username=username, password=password)
        if user is not None:
            if user.is_active:
                auth.login(request, user)
                return HttpResponseRedirect(c['next'])
            else:
                c['error'] = 'Account has been disabled'
        else:
            c['error'] = 'Invalid login and/or password'
    return render(request, 'login.html', c)

def logout(request):
    auth.logout(request)
    return HttpResponseRedirect(reverse('main.views.index'))

@login_required
def account(request):
    c = init_context(request)
    return render(request, 'account.html', c)

