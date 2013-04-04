from django.shortcuts import render
from django.views.decorators.http import require_safe, require_GET
from items.models import FinalItem
from items.helpers import item_search_to_json
from main.helpers import init_context


@require_safe
def index(request):
    c = init_context('proofs')
    c['finalitems'] = list(FinalItem.objects.filter(itemtype='P', status='F').order_by('-created_at')[:5])
    return render(request, 'proofs/index.html', c) 


@require_GET
def search(request):
    c = init_context('proof')
    c['init_items'] = item_search_to_json(itemtype='P')
    c['itemtype'] = 'proof'
    c['shorttype'] = 'P'
    return render(request, 'items/search.html', c) 
