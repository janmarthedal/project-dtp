from django.contrib.auth import logout as auth_logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.views.decorators.http import require_safe

from concepts.models import Concept
from drafts.models import DraftItem
from mathitems.models import MathItem

#import logging
#logger = logging.getLogger(__name__)

@require_safe
def home(request):
    items = [{
        'item': item,
        'defines': list(Concept.objects.filter(conceptdefinition__item=item)
                            .order_by('name')
                            .values_list('name', flat=True))
    } for item in MathItem.objects.order_by('-created_at')[:10]]
    return render(request, 'main/home.html', {'items': items})

@require_safe
def login(request):
    return render(request, 'main/login.html', {
        'title': 'Sign In',
        'next': request.GET.get('next'),
    })

@login_required
@require_safe
def profile(request):
    """from social.apps.django_app.context_processors import backends as auth_backends
    backends = auth_backends(request)['backends']
    logger.info('User {} has providers: {}'.format(request.user.username,
        ', '.join(p.provider for p in backends['associated'])))"""
    drafts = DraftItem.objects.order_by('updated_at').all()
    return render(request, 'main/profile.html', {
        'drafts': drafts,
        'title': 'Profile'
    })

@require_safe
def logout(request):
    auth_logout(request)
    return redirect('home')
