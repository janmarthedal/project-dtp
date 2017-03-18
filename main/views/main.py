from django.contrib.auth import logout as auth_logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.views.decorators.http import require_safe

from concepts.models import Concept
from drafts.models import DraftItem
from main.views.helpers import prepare_item_view_list
from mathitems.models import MathItem

#import logging
#logger = logging.getLogger(__name__)

@require_safe
def home(request):
    return render(request, 'main/home.html', {
        'items': prepare_item_view_list(MathItem.objects.order_by('-created_at')[:5])
    })

@require_safe
def login(request):
    return render(request, 'main/login.html', {
        'title': 'Sign In',
        'next': request.GET.get('next'),
    })

@login_required
@require_safe
def profile(request):
    drafts = DraftItem.objects.filter(created_by=request.user).order_by('updated_at').all()
    return render(request, 'main/profile.html', {
        'drafts': drafts,
        'title': 'Profile'
    })

@require_safe
def logout(request):
    auth_logout(request)
    return redirect('home')
