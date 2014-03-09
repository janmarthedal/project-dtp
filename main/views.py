from django.shortcuts import render
from django.views.decorators.http import require_safe
from main.helpers import init_context, make_get_url
from main.blog_feed import get_blog_feed
from items.helpers import prepare_list_items
from items.models import FinalItem

@require_safe
def index(request):
    queryset = FinalItem.objects.filter(status='F').order_by('-created_at')
    items, _ = prepare_list_items(queryset, 5)
    results = {
        'items': items,
        'more': {
            'text': 'View all',
            'link': make_get_url('items.views.search')
        }
    }
    c = init_context('home', blog_feed=get_blog_feed(), items=results)
    return render(request, 'home.html', c)
