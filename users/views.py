from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from django.contrib import auth
from django.core.urlresolvers import reverse

@require_http_methods(["GET", "POST"])
def login(request):
    c = {}
    if request.method == 'GET':
        c['next'] = request.GET.get('next', reverse('account_view'))
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
    return render(request, 'thrms/login.html', c)

def logout(request):
    auth.logout(request)
    return HttpResponseRedirect(reverse('index_view'))

@login_required
def account(request):
    return render(request, 'thrms/account.html')

