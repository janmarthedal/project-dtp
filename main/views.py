from django.shortcuts import render
from main.models import Item, ItemTag, Tag
from django.http import HttpResponseRedirect
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login

def index(request):
    #latest_items = Item.objects.filter(status='F').order_by('-modified_at')[:10]
    #latest_item_list = [{
    #    'link': item.get_absolute_url(),
    #    'name': item.get_cap_kind_with_id()
    #} for item in latest_items]
    return render(request, 'thrms/index.html')

@require_http_methods(["GET", "POST"])
def user_login(request):
    c = {}
    if request.method == 'GET':
        pass
    else:
        username = request.POST['user']
        password = request.POST['pwd']
        next_page = request.POST['next']
        user = authenticate(username=username, password=password)
        if user is not None:
            if user.is_active:
                login(request, user)
                return HttpResponseRedirect('/user/account')
            else:
                c['error'] = 'Account has been disabled'
        else:
            c['error'] = 'Invalid login and/or password'
    return render(request, 'thrms/login.html', c)

@login_required
def user_account(request):
    return render(request, 'thrms/account.html')

