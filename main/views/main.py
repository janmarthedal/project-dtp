import random
from django.contrib.auth import logout as auth_logout, get_user_model
from django.contrib.auth.decorators import login_required
from django.http import Http404
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
    context = {
        'latest': prepare_item_view_list(MathItem.objects.order_by('-created_at')[:1]),
        'def_count': MathItem.objects.filter(item_type=ItemTypes.DEF).count(),
        'thm_count': MathItem.objects.filter(item_type=ItemTypes.THM).count(),
        'prf_count': MathItem.objects.filter(item_type=ItemTypes.PRF).count(),
        'media_count': media_count,
        'concept_count': ConceptMeta.objects.filter(def_count__gt=0).count(),
        'eqn_count': Equation.objects.count(),
        'val_count': ItemValidation.objects.count(),
        'src_count': Source.objects.count(),
        'user_count': get_user_model().objects.filter(is_active=True).count()
    }
    if media_count:
        context['featured_media'] = Media.objects.all()[random.randrange(0, media_count)]
    return render(request, 'main/home.html', context)


@require_safe
def login(request):
    return render(request, 'main/login.html', {
        'title': 'Sign In',
        'next': request.GET.get('next'),
    })


@login_required
@require_safe
def current_user(request):
    return redirect('user-page', request.user.pk)


@require_safe
def logout(request):
    auth_logout(request)
    return redirect('home')


@require_safe
def user_page(request, user_id):
    User = get_user_model()
    try:
        user = User.objects.get(id=int(user_id))
    except User.DoesNotExist:
        raise Http404('User does not exist')
    context = {
        'is_me': False,
        'title': user.username
    }
    if user == request.user:
        context['is_me'] = True
        context['drafts'] = DraftItem.objects.filter(created_by=user).order_by('-updated_at').all()
    return render(request, 'main/user-page.html', context)


@require_safe
def users_home(request):
    return render(request, 'main/users-home.html', {
        'title': 'Users',
        'users': [{
            'id': user.id,
            'username': user.username,
            'last_login': user.last_login,
            'items': MathItem.objects.filter(created_by=user).count(),
            'validations': ItemValidation.objects.filter(created_by=user).count(),
        } for user in get_user_model().objects.order_by('username')]
    })
