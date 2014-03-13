from django.shortcuts import render
from django.views.decorators.http import require_safe
from main.helpers import init_context
from main.blog_feed import get_blog_feed
from items.helpers import search_items, make_search_url

@require_safe
def index(request):
    c = init_context('home', blog_feed=get_blog_feed(), itempage=search_items(5),
                     latest_link=make_search_url())
    return render(request, 'home.html', c)
