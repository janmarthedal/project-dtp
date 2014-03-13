from django.shortcuts import render
from django.views.decorators.http import require_GET
from items.helpers import search_items, make_search_url
from main.helpers import init_context

@require_GET
def index(request):
    search_args = {'type': 'D'}
    c = init_context('definitions', itempage=search_items(5, search_args),
                     see_all_link=make_search_url(search_args))
    return render(request, 'definitions/index.html', c)
