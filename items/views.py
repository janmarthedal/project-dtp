import json
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect, Http404, HttpResponse
from django.shortcuts import render, get_object_or_404
from django.template.loader import render_to_string
from django.views.decorators.http import require_POST, require_GET
from django.views.defaults import bad_request
from document.models import Document
from items.helpers import item_search_to_json, prepare_list_items
from items.models import FinalItem
from main.helpers import init_context, logged_in_or_404, make_get_url

import logging
logger = logging.getLogger(__name__)

@require_GET
def show_final(request, final_id):
    item = get_object_or_404(FinalItem, final_id=final_id)
    c = init_context(item.itemtype, item=item, proof_count=0,
                     allow={p: request.user.has_perm(p, item)
                            for p in ['add_proof', 'add_source', 'edit', 'add_to_doc', 'delete']},
                     validations=[v.json_data(request.user) for v in item.itemvalidation_set.all()],
                     documents=Document.objects.filter(created_by=request.user.id).exclude(documentitementry__item=item).all())
    if item.itemtype == 'T':
        c.update(proof_count=item.finalitem_set.filter(itemtype='P', status='F').count(),
                 init_proofs=item_search_to_json(itemtype='P', parent=final_id))
    if request.user.is_authenticated():
        c.update(user_id=request.user.id)
    return render(request, 'items/show_final.html', c)

@logged_in_or_404
@require_GET
def edit_final(request, final_id):
    item = get_object_or_404(FinalItem, final_id=final_id)
    if not request.user.has_perm('edit', item):
        raise Http404
    c = init_context(item.itemtype, item=item)
    if item.itemtype == 'D':
        c['primary_text'] = 'Terms defined'
    elif item.itemtype == 'T':
        c['primary_text'] = 'Name(s) of theorem'
    return render(request, 'items/edit_final.html', c)

@logged_in_or_404
@require_POST
def delete_final(request, item_id):
    item = get_object_or_404(FinalItem, pk=item_id)
    if not request.user.has_perm('delete', item):
        raise Http404
    item.delete()
    return HttpResponseRedirect(reverse('main.views.index'))

def search_data(request, is_fragment):
    page = int(request.GET.get('page', 1))
    page_data = {}
    if page != 1:
        page_data.update(page=page)
    queryset = FinalItem.objects.filter(status='F').order_by('-created_at')
    items, more = prepare_list_items(queryset, 10, page)
    current_url = make_get_url('items.views.search', page_data)
    return {
        'items': items,
        'current_url': current_url,
        'prev_data_url': make_get_url('items.views.search_fragment', {'page': page - 1}) if page > 1 else '',
        'next_data_url': make_get_url('items.views.search_fragment', {'page': page + 1}) if more else ''
    }

@require_GET
def search(request):
    try:
        itempage = search_data(request)
    except ValueError:
        return bad_request(request)
    c = init_context('search', itempage=itempage)
    return render(request, 'items/search.html', c)

@require_GET
def search_fragment(request):
    try:
        itempage = search_data(request)
    except ValueError:
        return bad_request(request)
    itempage['items'] = render_to_string('include/item_list_items.html',
                                         {'items': itempage['items'],
                                          'current_url': itempage['current_url']})
    return HttpResponse(json.dumps(itempage), content_type="application/json")
