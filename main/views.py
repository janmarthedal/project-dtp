import requests
from django.contrib.auth import logout as auth_logout
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from django.shortcuts import render, redirect, get_object_or_404
from social.apps.django_app.context_processors import backends as auth_backends

from project.helpers import capfirst
from main.models import DraftItem, ItemTypes

import logging
logger = logging.getLogger(__name__)

test_body = r"""The $n$th [harmonic number](=harmonic-number), $H_n$, is defined as

$$
H_n = 1 + \frac{1}{2} + \ldots + \frac{1}{n} = \sum_{k=1}^n \frac{1}{k}
$$

for $n \geq 1$."""

def node_request(path, payload):
    r = requests.post('http://localhost:3000' + path, json=payload)
    r.raise_for_status()
    return r.json()

def prepare_item(item_type, body):
    item_data = node_request('/prepare-item', {'text': body})
    tag_map = {int(key): value for key, value in item_data['tags'].items()}
    data = node_request('/render-item', item_data)
    defined = [tag_map[id] for id in data['defined']]
    errors = data['errors']
    item_type_display = ItemTypes.NAMES[item_type]
    if item_type == ItemTypes.DEF:
        if not defined:
            errors.append('A {} must define at least one concept'.format(item_type_display))
    else:
        if defined:
            errors.append('A {} may not define concepts'.format(item_type_display))
        defined = None
    return data['html'], defined, errors

# view function helper
def new_item(request, item_type):
    context = {'title': 'New ' + capfirst(ItemTypes.NAMES[item_type])}
    if request.method == 'POST':
        body = request.POST['src']
        context['body'] = body
        if request.POST['submit'] == 'preview':
            html, defined, errors = prepare_item(item_type, body)
            context.update(item_html=html, defined=defined, errors=errors)
        elif request.POST['submit'] == 'save':
            item = DraftItem.objects.create(creator=request.user,
                                            item_type=item_type, body=body)
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
    context = {'title': 'New {} (Draft {})'.format(id_str, item.get_item_type_title())}
    html, defined, errors = prepare_item(item.item_type, item.body)
    context.update(item_html=html, defined=defined, errors=errors)
    return render(request, 'main/show-draft.html', context)
