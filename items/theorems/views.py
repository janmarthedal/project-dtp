from django.shortcuts import render
from django.views.decorators.http import require_safe
from items.helpers import search_items, make_search_url
from main.helpers import init_context

@require_safe
def index(request):
    search_args = {'type': 'T'}
    c = init_context('theorems', itempage=search_items(5, search_args),
                     see_all_link=make_search_url(search_args))
    return render(request, 'theorems/index.html', c)
