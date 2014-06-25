from django.shortcuts import render
from django.views.decorators.http import require_safe
from items.helpers import ItemPagedSearch
from main.helpers import init_context

@require_safe
def index(request):
    search = ItemPagedSearch(type='P')
    c = init_context('proofs', itempage=search.make_search(5),
                     see_all_link=search.get_url())
    return render(request, 'proofs/index.html', c)
