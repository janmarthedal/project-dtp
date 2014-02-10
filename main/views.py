from django.shortcuts import render
from django.views.decorators.http import require_safe
from main.helpers import init_context
from main.blog_feed import get_blog_feed
from items.helpers import item_search_to_json

@require_safe
def index(request):
    c = init_context('home', blog_feed=get_blog_feed(), init_items=item_search_to_json())
    return render(request, 'home.html', c)
