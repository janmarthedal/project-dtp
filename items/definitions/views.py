import json
from django.core.urlresolvers import reverse
from django.http import HttpResponse
from django.shortcuts import render
from django.views.decorators.http import require_GET
from analysis.models import CategoryDefinitionUsage
from items.helpers import PagedSearch, ItemPagedSearch
from main.helpers import init_context

class WantedPagedSearch(PagedSearch):
    template_name = 'include/wanted_single_page.html'

    def get_queryset(self):
        return CategoryDefinitionUsage.objects.order_by('score')

    def get_base_url(self):
        return reverse('items.definitions.views.most_wanted')

@require_GET
def index(request):
    latest_defs_search = ItemPagedSearch(type='D')
    wanted_defs_search = WantedPagedSearch()
    c = init_context('definitions',
                     itempage=latest_defs_search.make_search(5),
                     see_all_link=latest_defs_search.get_url(),
                     wanted_defs=wanted_defs_search.make_search(5),
                     all_wanted_link=wanted_defs_search.get_url())
    return render(request, 'definitions/index.html', c)

@require_GET
def most_wanted(request):
    itempage = WantedPagedSearch(request=request).make_search(5)   # TODO: default page_size
    if request.GET.get('partial') is not None:
        return HttpResponse(json.dumps(itempage), content_type="application/json")
    else:
        c = init_context('definitions', itempage=itempage)
        return render(request, 'definitions/most-wanted.html', c)
