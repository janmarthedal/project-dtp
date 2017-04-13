import random
from django.contrib.auth import logout as auth_logout, get_user_model
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.views.decorators.http import require_safe

from concepts.models import ConceptMeta
from drafts.models import DraftItem
from equations.models import Equation
from main.views.helpers import prepare_item_view_list
from mathitems.models import MathItem
from mathitems.itemtypes import ItemTypes
from media.models import Media
from validations.models import ItemValidation, Source

# import logging
# logger = logging.getLogger(__name__)


@require_safe
def home(request):
    media_count = Media.objects.count()
    return render(request, 'main/home.html', {
        'latest': prepare_item_view_list(MathItem.objects.order_by('-created_at')[:1]),
        'featured_media': Media.objects.all()[random.randrange(0, media_count)],
        'def_count': MathItem.objects.filter(item_type=ItemTypes.DEF).count(),
        'thm_count': MathItem.objects.filter(item_type=ItemTypes.THM).count(),
        'prf_count': MathItem.objects.filter(item_type=ItemTypes.PRF).count(),
        'media_count': media_count,
        'concept_count': ConceptMeta.objects.filter(def_count__gt=0).count(),
        'eqn_count': Equation.objects.filter(cache_access__isnull=True).count(),
        'val_count': ItemValidation.objects.count(),
        'src_count': Source.objects.count(),
        'user_count': get_user_model().objects.filter(is_active=True).count()
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
