from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect, Http404
from django.shortcuts import render, get_object_or_404
from django.views.decorators.http import require_POST, require_GET
from items.helpers import item_search_to_json
from items.models import FinalItem
from main.helpers import init_context, logged_in_or_404

import logging
logger = logging.getLogger(__name__)

def get_user_final_permissions(user, item):
    logged_in = user.is_authenticated()
    return {
        'add_proof':  item.status == 'F' and item.itemtype == 'T' and logged_in,
        'add_source': item.status == 'F' and logged_in,
        'edit_final': item.status == 'F' and logged_in
    }

@require_GET
def show_final(request, final_id):
    item = get_object_or_404(FinalItem, final_id=final_id)
    item_perms = get_user_final_permissions(request.user, item)
    c = { 'item':        item,
          'perm':        item_perms,
          'validations': [v.json_serializable() for v in item.sourcevalidation_set.all()],
          'proof_count': 0 }
    if item.itemtype == 'T':
        c.update(proof_count = item.finalitem_set.filter(itemtype='P', status='F').count(),
                 init_proofs = item_search_to_json(itemtype='P', parent=final_id))
    if request.user.is_authenticated():
        c.update(user_id = request.user.pk)
    return render(request, 'items/show_final.html', c)

@logged_in_or_404
@require_GET
def edit_final(request, final_id):
    item = get_object_or_404(FinalItem, final_id=final_id)
    item_perms = get_user_final_permissions(request.user, item)
    if not item_perms['edit_final']:
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
    if not request.user.is_admin:
        raise Http404
    item = get_object_or_404(FinalItem, pk=item_id)
    item.delete()
    return HttpResponseRedirect(reverse('main.views.index'))
