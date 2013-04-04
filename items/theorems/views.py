from django.shortcuts import render
from django.views.decorators.http import require_safe, require_GET
from items.models import FinalItem
from items.helpers import item_search_to_json
from main.helpers import init_context


@require_safe
def index(request):
    c = init_context('theorems')
    c['finalitems'] = list(FinalItem.objects.filter(itemtype='T', status='F').order_by('-created_at')[:5])
    return render(request, 'theorems/index.html', c) 


@require_GET
def search(request):
    c = init_context('theorems')
    c['init_items'] = item_search_to_json(itemtype='T')
    c['itemtype'] = 'theorem'
    c['shorttype'] = 'T'
    return render(request, 'items/search.html', c) 
