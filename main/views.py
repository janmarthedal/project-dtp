from django.shortcuts import render
from django.views.decorators.http import require_safe
from main.helpers import init_context
from main.blog_feed import get_blog_feed
from drafts.models import DraftItem
from items.models import FinalItem
from users.models import User
from items.helpers import item_search_to_json
from analysis.models import TagCount

@require_safe
def index(request):
    c = init_context('home',
                     blog_feed  = get_blog_feed(),
                     init_items = item_search_to_json(),
                     top_tags   = [{ 'name': tc.tag.name, 'count': tc.count }
                                   for tc in TagCount.objects.exclude(count=0).order_by('-count')[:20]])
    return render(request, 'home.html', c)

@require_safe
def about(request):
    c = init_context('about',
                     def_final  = FinalItem.objects.filter(itemtype='D', status='F').count(),
                     thm_final  = FinalItem.objects.filter(itemtype='T', status='F').count(),
                     prf_final  = FinalItem.objects.filter(itemtype='P', status='F').count(),
                     def_review = DraftItem.objects.filter(itemtype='D', status='R').count(),
                     thm_review = DraftItem.objects.filter(itemtype='T', status='R').count(),
                     prf_review = DraftItem.objects.filter(itemtype='P', status='R').count(),
                     def_draft  = DraftItem.objects.filter(itemtype='D', status='D').count(),
                     thm_draft  = DraftItem.objects.filter(itemtype='T', status='D').count(),
                     prf_draft  = DraftItem.objects.filter(itemtype='P', status='D').count(),
                     user_count = User.objects.filter(is_active=True).count())
    return render(request, 'about.html', c)
