from django.shortcuts import render
from django.views.decorators.http import require_safe
from items.helpers import item_search_to_json
from main.helpers import init_context

@require_safe
def index(request):
    c = init_context('proofs')
    c['init_items'] = item_search_to_json(itemtype='P')
    return render(request, 'proofs/index.html', c) 
