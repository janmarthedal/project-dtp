from django.contrib import messages
from django.contrib.auth import get_user_model, logout as auth_logout
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.views.decorators.http import require_safe
from document.models import Document
from items.helpers import item_search_to_json
from main.helpers import init_context, logged_in_or_404
from users.models import Invitations

import logging
logger = logging.getLogger(__name__)

@require_safe
def index(request):
    c = init_context('users',
                     userlist = list(get_user_model().objects.filter(is_active=True).order_by('name')))
    return render(request, 'users/index.html', c)

@require_safe
def login(request):
    if request.user.is_authenticated():
        messages.info(request, 'Already logged in')
        return HttpResponseRedirect(reverse('users.views.profile_current'))
    c = init_context('users', next=request.GET.get('next', reverse('users.views.profile_current')))
    token = request.GET.get('token', None)
    if token:
        if Invitations.objects.filter(token=token).exists():
            request.session['invite_token'] = token
            c['invited'] = True
        else:
            messages.warning(request, 'Illegal invitation token')
    return render(request, 'users/login.html', c)

@require_safe
def logout(request):
    auth_logout(request)
    return HttpResponseRedirect(reverse('main.views.index'))

@require_safe
def profile(request, user_id):
    pageuser = get_object_or_404(get_user_model(), pk=user_id)
    own_profile = request.user == pageuser
    c = init_context('users',
                     pageuser    = pageuser,
                     init_items  = item_search_to_json(itemtype='D', user=pageuser),
                     statuses    = 'FRD' if own_profile else 'FR',
                     user_id     = pageuser.id,
                     own_profile = own_profile,
                     documents   = Document.objects.filter(created_by=pageuser).all())
    return render(request, 'users/profile.html', c)

@logged_in_or_404
@require_safe
def profile_current(request):
    return HttpResponseRedirect(reverse('users.views.profile', args=[request.user.id]))
