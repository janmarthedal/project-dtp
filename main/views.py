import requests
from django.contrib.auth import logout as auth_logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from social.apps.django_app.context_processors import backends as auth_backends

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

def new_item(request, item_type):
    context = {'title': 'New ' + item_type}
    if request.method == 'POST':
        body = request.POST['src']
        context['body'] = body
        if request.POST['submit'] == 'preview':
            item_data = node_request('/prepare-item', {'text': body})
            data = node_request('/render-item', item_data)
            context['item_html'] = data['html']
            context['errors'] = data['errors'];
    else:
        context['body'] = test_body
    return render(request, 'main/new-item.html', context)

def new_definition(request):
    return new_item(request, 'Definition')

def new_theorem(request):
    return new_item(request, 'Theorem')

def home(request):
    return render(request, 'main/home.html')

def login(request):
    context = {'title': 'Sign In'}
    return render(request, 'main/login.html', context)

@login_required
def profile(request):
    context = {'title': 'Profile'}
    backends = auth_backends(request)['backends']
    logger.info('User {} has providers: {}'.format(request.user.username,
        ', '.join(p.provider for p in backends['associated'])))
    return render(request, 'main/profile.html', context)

def logout(request):
    auth_logout(request)
    return redirect('home')
