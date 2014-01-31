import StringIO
from django import forms
from django.contrib import messages
from django.contrib.auth import get_user_model, logout as auth_logout
from django.core import management
from django.core.urlresolvers import reverse
from django.forms.util import ErrorList
from django.http import HttpResponseRedirect, Http404
from django.shortcuts import render, get_object_or_404
from django.utils.html import escape
from django.views.decorators.http import require_safe, require_http_methods
from document.models import Document
from items.helpers import item_search_to_json
from main.helpers import init_context, logged_in_or_404
from users.models import Invitations

import logging
logger = logging.getLogger(__name__)

@require_safe
def index(request):
    c = init_context('users',
                     userlist=list(get_user_model().objects
                                   .filter(is_active=True, is_admin=False).order_by('name')))
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
    description = '<br/>\n'.join(map(escape, (pageuser.description or '').split('\n')))
    c = init_context('users',
                     pageuser = pageuser,
                     description = description,
                     init_items = item_search_to_json(itemtype='D', user=pageuser),
                     statuses = 'FRD' if own_profile else 'FR',
                     user_id = pageuser.id,
                     own_profile = own_profile,
                     documents = Document.objects.filter(created_by=pageuser).all())
    return render(request, 'users/profile.html', c)

class CustomErrorList(ErrorList):
    def __unicode__(self):
        return self.as_custom()
    def as_custom(self):
        if not self: return u''
        return ''.join(u'<span class="label label-danger">{}</span>'.format(e) for e in self)

class ProfileForm(forms.Form):
    name = forms.CharField(label='Display name', max_length=255,
                           widget=forms.TextInput(attrs={'class':'form-control'}))
    email = forms.EmailField(label='Email address', max_length=255,
                             widget=forms.EmailInput(attrs={'class':'form-control'}))
    description = forms.CharField(label='Description',
                                  widget=forms.Textarea(attrs={'class':'form-control'}))

@require_http_methods(['GET', 'POST'])
@logged_in_or_404
def profile_edit(request):
    if request.method == 'POST':
        form = ProfileForm(request.POST, error_class=CustomErrorList)
        if form.is_valid():
            request.user.name = form.cleaned_data['name']
            request.user.email = form.cleaned_data['email']
            request.user.description = form.cleaned_data['description']
            request.user.save()
            return HttpResponseRedirect(reverse('users.views.profile', args=[request.user.id]))
    else:
        form = ProfileForm({'name': request.user.get_full_name(), 'email': request.user.email,
                            'description': request.user.description})
    c = init_context('users', form=form)
    return render(request, 'users/profile_edit.html', c)

@require_safe
@logged_in_or_404
def profile_current(request):
    return HttpResponseRedirect(reverse('users.views.profile', args=[request.user.id]))

@require_http_methods(['GET', 'POST'])
@logged_in_or_404
def administration(request):
    if not request.user.is_admin:
        raise Http404('Must be administrator')
    c = init_context('users')
    if request.method == 'GET':
        return render(request, 'users/administration.html', c)
    action = request.POST.get('action')
    output = StringIO.StringIO()
    if action == 'deps':
        header = 'Recompute item dependencies'
        management.call_command('deps', stdout=output)
    elif action == 'points':
        header = 'Recompute points'
        management.call_command('points', stdout=output)
    elif action == 'invite':
        header = 'Invite new beta user'
        management.call_command('invite', target_email=request.POST.get('email'), stdout=output)
    c.update({'header': header, 'output': output.getvalue()})
    return render(request, 'users/admin-output.html', c)
