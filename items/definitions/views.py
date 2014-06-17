import json
from django.core.urlresolvers import reverse
from django.http import HttpResponse
from django.shortcuts import render
from django.template.loader import render_to_string
from django.views.decorators.http import require_GET
from analysis.models import CategoryDefinitionUsage
from items.helpers import search_items, make_search_url, prepare_list_items, request_get_int
from main.helpers import init_context, make_get_url

def request_to_wanted_search_data(request):
    return {
        'page': request_get_int(request, 'page', 1, lambda v: v >= 1)
    }

def search_wanted(page_size, search_data):
    queryset = CategoryDefinitionUsage.objects.order_by('score')
    current_url = make_get_url(reverse('items.definitions.views.most_wanted'), search_data)
    page = search_data.get('page') or 1
    items, more = prepare_list_items(queryset, page_size, page)
    return {
        'rendered': render_to_string('include/wanted_single_page.html',
                                     {'items': items, 'current_url': current_url}),
        #'current_url': current_url,
        'prev_data_url': make_get_url(reverse('items.definitions.views.most_wanted'), {'page': page-1}) if page > 1 else '',
        'next_data_url': make_get_url(reverse('items.definitions.views.most_wanted'), {'page': page+1}) if more else ''
    }

@require_GET
def index(request):
    search_args = {'type': 'D'}
    c = init_context('definitions', itempage=search_items(5, search_args),
                     see_all_link=make_search_url(search_args),
                     wanted_defs=search_wanted(5, {}),
                     all_wanted_link=reverse('items.definitions.views.most_wanted'))
    return render(request, 'definitions/index.html', c)

@require_GET
def most_wanted(request):
    search_data = request_to_wanted_search_data(request)
    itempage = search_wanted(5, search_data)   # 5 -> 20
    if request.GET.get('partial') is not None:
        return HttpResponse(json.dumps(itempage), content_type="application/json")
    else:
        c = init_context('definitions', itempage=itempage)
        return render(request, 'definitions/most-wanted.html', c)
    