from django.contrib.auth import logout as auth_logout
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from django.shortcuts import render, redirect, get_object_or_404
from social.apps.django_app.context_processors import backends as auth_backends

from main.models import DraftItem, ItemTypes

import logging
logger = logging.getLogger(__name__)

test_body = r"""The $n$th [harmonic number](=harmonic-number), $H_n$, is defined as

$$
H_n = 1 + \frac{1}{2} + \ldots + \frac{1}{n} = \sum_{k=1}^n \frac{1}{k}
$$

for $n \geq 1$."""

# view function helper
def new_item(request, item_type):
    item = DraftItem(creator=request.user, item_type=item_type, body='')
    context = {'title': 'New ' + item.get_item_type_display()}
    if request.method == 'POST':
        body = request.POST['src']
        item.body = body
        context['body'] = body
        if request.POST['submit'] == 'preview':
            html, defined, errors = item.prepare()
            context.update(item_html=html, defined=defined, errors=errors)
        elif request.POST['submit'] == 'save':
            item.save()
            return redirect(item)
    else:
        context['body'] = test_body
    return render(request, 'main/new-item.html', context)

@login_required
def new_definition(request):
    return new_item(request, ItemTypes.DEF)

@login_required
def new_theorem(request):
    return new_item(request, ItemTypes.THM)

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

@login_required
def show_draft(request, id_str):
    item = get_object_or_404(DraftItem, id=int(id_str))
    if item.creator != request.user:
        return HttpResponseForbidden()
    context = {'title': 'New {} (Draft {})'.format(item.get_item_type_display(), item.id)}
    html, defined, errors = item.prepare()
    context.update(item_html=html, defined=defined, errors=errors)
    return render(request, 'main/show-draft.html', context)
