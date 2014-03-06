from django.shortcuts import render
from django.views.decorators.http import require_safe
from main.helpers import init_context
from main.blog_feed import get_blog_feed
from items.models import FinalItem

#import logging
#logger = logging.getLogger(__name__)

def prepare_final_items(queryset, max_length):
    item_list = queryset[0:(max_length + 1)]
    return {
        'items': item_list[0:max_length],
        'more': len(item_list) > max_length
    }

@require_safe
def index(request):
    latest_items = prepare_final_items(FinalItem.objects.filter(status='F').order_by('-created_at'), 5)
    c = init_context('home', blog_feed=get_blog_feed(), latest_items=latest_items['items'])
    return render(request, 'home.html', c)
