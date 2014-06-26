from django.shortcuts import render
from django.views.decorators.http import require_safe
from main.helpers import init_context
from main.blog_feed import get_blog_feed
from items.models import ItemPagedSearch

@require_safe
def index(request):
    latest_search = ItemPagedSearch()
    c = init_context('home', blog_feed=get_blog_feed(), itempage=latest_search.make_search(5),
                     see_all_link=latest_search.get_url())
    return render(request, 'home.html', c)
